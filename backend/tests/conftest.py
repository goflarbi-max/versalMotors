from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture
def api_client(monkeypatch):
    monkeypatch.setenv("VERSALMOTORS_SESSION_SECRET", "test-secret-with-enough-entropy")
    monkeypatch.setenv("VERSALMOTORS_ALLOWED_ORIGINS", "https://testserver")
    monkeypatch.setenv("VERSALMOTORS_SECURE_COOKIES", "true")
    with TestClient(app, base_url="https://testserver") as client:
        yield client


def authenticate(client: TestClient) -> None:
    csrf_response = client.get("/api/v1/auth/csrf")
    assert csrf_response.status_code == 200
    token = csrf_response.json()["csrf_token"]
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "demo@versalmotors.com", "password": "VersalDemo2026!"},
        headers={"Origin": "https://testserver", "X-CSRF-Token": token},
    )
    assert response.status_code == 200, response.text
