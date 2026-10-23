from __future__ import annotations

from backend.tests.conftest import authenticate
from tests.parity_support import (
    assert_nested_equal,
    capture_direct_sql_verification,
    load_baseline,
)


ENDPOINTS = {
    "kpis": "/api/v1/overview/kpis",
    "revenue_trend": "/api/v1/overview/revenue-trend",
    "revenue_by_branch": "/api/v1/overview/revenue-by-branch",
    "gross_margin_by_model": "/api/v1/overview/margin-by-model",
}


def _params(filters: dict) -> list[tuple[str, str]]:
    params: list[tuple[str, str]] = []
    for key, value in filters.items():
        if value is None:
            continue
        if isinstance(value, list):
            params.extend((key, str(item)) for item in value)
        else:
            params.append((key, str(value)))
    return params


def test_all_overview_endpoints_match_baseline_and_direct_sql(api_client):
    authenticate(api_client)
    baseline = load_baseline()
    direct_sql = capture_direct_sql_verification()["scenarios"]

    for scenario_name, expected_scenario in baseline["scenarios"].items():
        for section, endpoint in ENDPOINTS.items():
            response = api_client.get(endpoint, params=_params(expected_scenario["filters"]))
            assert response.status_code == 200, (scenario_name, section, response.text)
            records = response.json()["data"]
            expected = expected_scenario[section]
            assert len(records) == expected["row_count"]
            assert_nested_equal(records, expected["records"], path=f"api.{scenario_name}.{section}")
            assert_nested_equal(
                records,
                direct_sql[scenario_name][section]["records"],
                path=f"sql.{scenario_name}.{section}",
            )


def test_filters_are_exact_and_metadata_reports_applied_values(api_client):
    authenticate(api_client)
    response = api_client.get(
        "/api/v1/overview/kpis",
        params=[("start_date", "2023-01-01"), ("end_date", "2025-06-30"), ("branch", "Accra")],
    )

    assert response.status_code == 200
    assert response.json()["meta"]["filters"]["branch"] == ["Accra"]


def test_invalid_date_range_and_excessive_filter_values_are_rejected(api_client):
    authenticate(api_client)
    backwards = api_client.get(
        "/api/v1/overview/kpis?start_date=2025-01-02&end_date=2025-01-01"
    )
    too_many = api_client.get(
        "/api/v1/overview/kpis",
        params=[("branch", str(index)) for index in range(51)],
    )

    assert backwards.status_code == 422
    assert too_many.status_code == 422
