def test_health_and_openapi_are_available_without_authentication(api_client):
    live = api_client.get("/health/live")
    ready = api_client.get("/health/ready")
    schema = api_client.get("/openapi.json")

    assert live.json() == {"status": "ok"}
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready"
    assert ready.json()["row_counts"]["sales"] == 20_520
    assert schema.status_code == 200
    assert "/api/v1/overview/kpis" in schema.json()["paths"]


def test_security_headers_are_present(api_client):
    response = api_client.get("/health/live")

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["strict-transport-security"].startswith("max-age=")
    assert response.headers["x-request-id"]
