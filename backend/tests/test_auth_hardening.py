from __future__ import annotations

import json
import logging

from backend.app.core.config import _users_from_environment
from backend.app.core.security import SessionStore
from backend.app.schemas.auth import LoginRequest


def test_environment_users_support_roles_and_legacy_hashes(monkeypatch):
    monkeypatch.setenv(
        "VERSALMOTORS_AUTH_USERS_JSON",
        json.dumps(
            {
                "ADMIN@VERSALMOTORS.COM": {
                    "password_hash": "$2b$12$example",
                    "role": "admin",
                },
                "viewer@versalmotors.com": "$2b$12$legacy",
            }
        ),
    )

    users = _users_from_environment()

    assert users["admin@versalmotors.com"].role == "admin"
    assert users["viewer@versalmotors.com"].role == "viewer"
    assert users["viewer@versalmotors.com"].password_hash == "$2b$12$legacy"


def test_login_request_normalizes_email_and_limits_input_lengths():
    request = LoginRequest(email="  Demo@VersalMotors.com ", password="safe password")
    assert request.email == "demo@versalmotors.com"


def test_invalid_configured_role_is_not_loaded(monkeypatch):
    monkeypatch.setenv(
        "VERSALMOTORS_AUTH_USERS_JSON",
        json.dumps(
            {
                "bad@versalmotors.com": {
                    "password_hash": "$2b$12$example",
                    "role": "superuser",
                }
            }
        ),
    )

    assert "bad@versalmotors.com" not in _users_from_environment()


def test_session_store_rejects_idle_absolute_and_tampered_tokens():
    store = SessionStore("test-secret", lifetime_seconds=100, idle_seconds=10)
    session, token = store.create("demo@versalmotors.com", "viewer", now=100)

    assert session.role == "viewer"
    assert store.validate(token, now=105) is not None
    assert store.validate(f"{token}tampered", now=106) is None
    assert store.validate(token, now=116) is None

    _, second_token = store.create("demo@versalmotors.com", "viewer", now=200)
    assert store.validate(second_token, now=301) is None


def test_role_aware_me_requires_a_valid_session(api_client):
    assert api_client.get("/api/auth/me").status_code == 401


def test_correct_password_is_blocked_during_active_lockout(api_client):
    headers = {"Origin": "https://testserver"}
    for _ in range(5):
        token = api_client.get("/api/v1/auth/csrf").json()["csrf_token"]
        response = api_client.post(
            "/api/v1/auth/login",
            json={"email": "demo@versalmotors.com", "password": "wrong-password"},
            headers={**headers, "X-CSRF-Token": token},
        )
    assert response.status_code == 429

    token = api_client.get("/api/v1/auth/csrf").json()["csrf_token"]
    blocked = api_client.post(
        "/api/v1/auth/login",
        json={"email": "demo@versalmotors.com", "password": "VersalDemo2026!"},
        headers={**headers, "X-CSRF-Token": token},
    )
    assert blocked.status_code == 429
    assert blocked.json()["message"].startswith("Too many failed attempts")


def test_auth_responses_are_not_cached_and_include_security_headers(api_client):
    response = api_client.get("/api/v1/auth/csrf")

    assert response.headers["cache-control"] == "no-store, max-age=0"
    assert response.headers["pragma"] == "no-cache"
    assert response.headers["strict-transport-security"].startswith("max-age=")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]


def test_foreign_origin_is_rejected_without_leaking_credentials(api_client):
    token = api_client.get("/api/v1/auth/csrf").json()["csrf_token"]
    response = api_client.post(
        "/api/v1/auth/login",
        json={"email": "demo@versalmotors.com", "password": "VersalDemo2026!"},
        headers={"Origin": "https://evil.example", "X-CSRF-Token": token},
    )

    assert response.status_code == 403
    assert "VersalDemo2026!" not in response.text


def test_login_cookie_has_secure_http_only_and_samesite_flags(api_client):
    token = api_client.get("/api/v1/auth/csrf").json()["csrf_token"]
    response = api_client.post(
        "/api/v1/auth/login",
        json={"email": "demo@versalmotors.com", "password": "VersalDemo2026!"},
        headers={"Origin": "https://testserver", "X-CSRF-Token": token},
    )

    cookie = response.headers["set-cookie"].lower()
    assert "versal_session=" in cookie
    assert "httponly" in cookie
    assert "secure" in cookie
    assert "samesite=lax" in cookie


def test_auth_events_mask_email_and_never_log_password(api_client, caplog):
    caplog.set_level(logging.INFO, logger="versalmotors.auth")
    token = api_client.get("/api/v1/auth/csrf").json()["csrf_token"]
    api_client.post(
        "/api/v1/auth/login",
        json={"email": "demo@versalmotors.com", "password": "not-the-password"},
        headers={"Origin": "https://testserver", "X-CSRF-Token": token},
    )

    combined = "\n".join(record.getMessage() for record in caplog.records)
    assert "login_failure" in combined
    assert "d***@versalmotors.com" in combined
    assert "demo@versalmotors.com" not in combined
    assert "not-the-password" not in combined


def test_role_aware_me_returns_viewer_role_after_login(api_client):
    token = api_client.get("/api/v1/auth/csrf").json()["csrf_token"]
    response = api_client.post(
        "/api/v1/auth/login",
        json={"email": "demo@versalmotors.com", "password": "VersalDemo2026!"},
        headers={"Origin": "https://testserver", "X-CSRF-Token": token},
    )
    assert response.status_code == 200
    assert api_client.get("/api/auth/me").json() == {
        "authenticated": True,
        "email": "demo@versalmotors.com",
        "role": "viewer",
    }
