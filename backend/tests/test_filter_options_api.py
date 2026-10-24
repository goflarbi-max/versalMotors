from __future__ import annotations

from backend.tests.conftest import authenticate


def test_filter_options_match_current_streamlit_choices(api_client):
    authenticate(api_client)
    response = api_client.get("/api/v1/filters/options")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["date_range"] == {
        "minimum": "2022-11-10",
        "maximum": "2025-06-30",
        "default_start": "2025-04-02",
    }
    assert data["branches"] == sorted(data["branches"])
    assert data["brands"] == sorted(data["brands"])
    assert data["models"] == sorted(data["models"])
    assert data["salespeople"] == sorted(data["salespeople"])
    assert data["statuses"] == sorted(data["statuses"])
    assert "Accra" in data["branches"]
    assert "Hilux" in data["models"]
    assert "completed" in data["statuses"]


def test_filter_options_requires_authentication(api_client):
    response = api_client.get("/api/v1/filters/options")
    assert response.status_code == 401
