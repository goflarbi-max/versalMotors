from __future__ import annotations

from hashlib import sha256
from io import StringIO

import pandas as pd

from backend.tests.conftest import authenticate
from tests.parity_support import assert_nested_equal, capture_direct_sql_verification, load_baseline


def _all_records(client, path: str) -> list[dict]:
    records: list[dict] = []
    page = 1
    while True:
        response = client.get(path, params={"page": page, "page_size": 50})
        assert response.status_code == 200, response.text
        payload = response.json()["data"]
        records.extend(payload["records"])
        if len(records) >= payload["total"]:
            return records
        page += 1


def test_quality_summary_checks_and_log_match_baseline_and_direct_sql(api_client):
    authenticate(api_client)
    expected = load_baseline()["data_quality"]
    direct = capture_direct_sql_verification()["data_quality"]

    summary = api_client.get("/api/v1/data-quality/summary")
    checks = _all_records(api_client, "/api/v1/data-quality/checks")
    cleaning_log = _all_records(api_client, "/api/v1/data-quality/cleaning-log")

    assert summary.status_code == 200
    actual_summary = summary.json()["data"]
    assert {key: actual_summary[key] for key in expected["summary"]} == expected["summary"]
    assert_nested_equal(checks, expected["checks"]["records"], path="baseline.data_quality.checks")
    assert_nested_equal(checks, direct["checks"]["records"], path="sql.data_quality.checks")
    assert_nested_equal(cleaning_log, expected["cleaning_log"]["records"], path="baseline.data_quality.cleaning_log")
    assert_nested_equal(cleaning_log, direct["cleaning_log"]["records"], path="sql.data_quality.cleaning_log")


def test_quality_sorting_paging_and_validation(api_client):
    authenticate(api_client)
    response = api_client.get("/api/v1/data-quality/checks", params={"page": 1, "page_size": 10, "sort_by": "count", "sort_dir": "desc"})
    counts = [record["count"] for record in response.json()["data"]["records"]]
    assert response.status_code == 200 and counts == sorted(counts, reverse=True)
    assert api_client.get("/api/v1/data-quality/checks?page=999&page_size=10").json()["data"]["records"] == []
    assert api_client.get("/api/v1/data-quality/checks?page_size=11").status_code == 422
    assert api_client.get("/api/v1/data-quality/checks?sort_by=bad&sort_dir=asc").status_code == 422


def test_quality_exports_are_complete_and_match_frozen_csv(api_client):
    authenticate(api_client)
    expected = load_baseline()["data_quality"]
    csv_response = api_client.get("/api/v1/data-quality/checks.csv")
    pdf_response = api_client.get("/api/v1/data-quality/checks.pdf")
    csv_frame = pd.read_csv(StringIO(csv_response.text))

    assert csv_response.status_code == pdf_response.status_code == 200
    assert len(csv_frame) == expected["checks"]["row_count"]
    assert len(csv_response.content) == expected["csv_bytes"]
    assert sha256(csv_response.content).hexdigest() == expected["csv_sha256"]
    assert pdf_response.content.startswith(b"%PDF")
    assert "attachment" in csv_response.headers["content-disposition"]
    assert "attachment" in pdf_response.headers["content-disposition"]


def test_quality_routes_require_authentication(api_client):
    for path in ("/api/v1/data-quality/summary", "/api/v1/data-quality/checks", "/api/v1/data-quality/cleaning-log", "/api/v1/data-quality/checks.csv", "/api/v1/data-quality/checks.pdf"):
        assert api_client.get(path).status_code == 401
