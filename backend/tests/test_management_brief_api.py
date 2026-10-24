from __future__ import annotations

from backend.tests.conftest import authenticate
from tests.parity_support import assert_nested_equal, capture_direct_sql_verification, load_baseline


def _headers(client) -> dict[str, str]:
    token = client.get("/api/v1/auth/csrf").json()["csrf_token"]
    return {"Origin": "https://testserver", "X-CSRF-Token": token}


def _create(client):
    return client.post(
        "/api/v1/management-brief",
        json={"start_date": "2024-01-01", "end_date": "2024-12-31"},
        headers=_headers(client),
    )


def test_management_brief_numbers_match_baseline_and_direct_sql(api_client, monkeypatch):
    authenticate(api_client)
    monkeypatch.setattr(
        "src.ai.brief.generate_text",
        lambda *args, **kwargs: {"ok": False, "text": "", "reason": "not_configured"},
    )
    response = _create(api_client)
    expected = load_baseline()["management_brief"]
    direct = capture_direct_sql_verification()["management_brief"]

    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert data["start_date"] == expected["start_date"]
    assert data["end_date"] == expected["end_date"]
    for actual, baseline_item, sql_item in zip(data["evidence"], expected["evidence"], direct["evidence"]):
        assert actual["id"] == baseline_item["id"] == sql_item["id"]
        assert actual["label"] == baseline_item["label"] == sql_item["label"]
        assert_nested_equal(actual["number"], baseline_item["number"], path=actual["id"])
        assert_nested_equal(actual["number"], sql_item["number"], path=f"sql.{actual['id']}")
        assert actual["value"] == baseline_item["value"] == sql_item["value"]
        assert_nested_equal(actual["data"], baseline_item["data"]["records"], path=f"data.{actual['id']}")
        assert "sql" not in actual
    assert "executive_summary" in data["sections"]
    assert expected["evidence"][0]["value"] in data["sections"]["executive_summary"]


def test_management_brief_exports_exact_generated_artifact(api_client, monkeypatch):
    authenticate(api_client)
    monkeypatch.setattr(
        "src.ai.brief.generate_text",
        lambda *args, **kwargs: {"ok": False, "text": "", "reason": "service_unavailable_503"},
    )
    created = _create(api_client)
    data = created.json()["data"]
    report_id = data["report_id"]
    markdown = api_client.get(f"/api/v1/management-brief/{report_id}.md")
    markdown_again = api_client.get(f"/api/v1/management-brief/{report_id}.md")
    pdf = api_client.get(f"/api/v1/management-brief/{report_id}.pdf")

    assert created.status_code == markdown.status_code == markdown_again.status_code == pdf.status_code == 200
    assert markdown.content == markdown_again.content
    assert markdown.text.startswith("# Management Brief 2024-01-01 to 2024-12-31")
    for evidence in data["evidence"]:
        assert evidence["id"] in markdown.text
        assert evidence["value"] in markdown.text
    assert pdf.content.startswith(b"%PDF")
    assert "attachment" in markdown.headers["content-disposition"]
    assert "attachment" in pdf.headers["content-disposition"]


def test_management_brief_rejects_bad_dates_and_missing_security(api_client):
    unauthenticated = api_client.post(
        "/api/v1/management-brief",
        json={"start_date": "2024-01-01", "end_date": "2024-12-31"},
    )
    authenticate(api_client)
    backwards = api_client.post(
        "/api/v1/management-brief",
        json={"start_date": "2024-12-31", "end_date": "2024-01-01"},
        headers=_headers(api_client),
    )
    no_csrf = api_client.post(
        "/api/v1/management-brief",
        json={"start_date": "2024-01-01", "end_date": "2024-12-31"},
    )
    missing = api_client.get("/api/v1/management-brief/not-a-report.pdf")

    assert unauthenticated.status_code == 401
    assert backwards.status_code == 422
    assert no_csrf.status_code == 403
    assert missing.status_code == 404


def test_management_brief_ai_failure_never_breaks_generation(api_client, monkeypatch):
    authenticate(api_client)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(
        "src.ai.brief.generate_text",
        lambda *args, **kwargs: {"ok": False, "text": "", "reason": "service_unavailable_503"},
    )
    response = _create(api_client)

    assert response.status_code == 200
    assert "executive_summary" in response.json()["data"]["sections"]
    assert "503" not in response.text
