from __future__ import annotations

import json

from backend.app.core.config import _users_from_environment
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
