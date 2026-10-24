from __future__ import annotations

from io import StringIO
from urllib.parse import quote

import pandas as pd

from backend.app.services.investigate import _sorted_copy
from backend.tests.conftest import authenticate
from tests.parity_support import (
    assert_nested_equal,
    capture_direct_sql_verification,
    load_baseline,
)


def _params(filters: dict, **extra) -> list[tuple[str, str]]:
    params: list[tuple[str, str]] = []
    for key, value in {**filters, **extra}.items():
        if value is None:
            continue
        if isinstance(value, list):
            params.extend((key, str(item)) for item in value)
        else:
            params.append((key, str(value)))
    return params


def _all_records(client, path: str, filters: dict) -> list[dict]:
    records: list[dict] = []
    page = 1
    while True:
        response = client.get(path, params=_params(filters, page=page, page_size=50))
        assert response.status_code == 200, response.text
        data = response.json()["data"]
        records.extend(data["records"])
        if len(records) >= data["total"]:
            return records
        page += 1


def test_warranty_levels_match_baseline_and_direct_sql(api_client):
    authenticate(api_client)
    expected = load_baseline()["investigate"]
    direct = capture_direct_sql_verification()["investigate"]
    model = quote(expected["selected_model"], safe="")
    branch = quote(expected["selected_branch"], safe="")
    endpoints = {
        "models": "/api/v1/investigate/warranty/models",
        "branches": f"/api/v1/investigate/warranty/models/{model}/branches",
        "claims": f"/api/v1/investigate/warranty/models/{model}/branches/{branch}/claims",
    }

    for section, endpoint in endpoints.items():
        records = _all_records(api_client, endpoint, expected["filters"])
        assert_nested_equal(records, expected[section]["records"], path=f"baseline.{section}")
        assert_nested_equal(records, direct[section]["records"], path=f"sql.{section}")


def test_warranty_sorting_is_stable_numeric_and_nulls_last(api_client):
    authenticate(api_client)
    filters = load_baseline()["investigate"]["filters"]
    response = api_client.get(
        "/api/v1/investigate/warranty/models",
        params=_params(filters, page_size=10, sort_by="claim_count", sort_dir="asc"),
    )
    counts = [row["claim_count"] for row in response.json()["data"]["records"]]
    assert counts == sorted(counts)

    original = pd.DataFrame({"label": ["b", None, "a", "a"], "position": [0, 1, 2, 3]})
    snapshot = original.copy(deep=True)
    ordered = _sorted_copy(original, sort_by="label", sort_dir="asc", allowed_columns=("label",))
    assert ordered["position"].tolist() == [2, 3, 0, 1]
    pd.testing.assert_frame_equal(original, snapshot)


def test_warranty_paging_validation_and_boundaries(api_client):
    authenticate(api_client)
    filters = load_baseline()["investigate"]["filters"]
    first = api_client.get(
        "/api/v1/investigate/warranty/models", params=_params(filters, page=1, page_size=10)
    )
    beyond = api_client.get(
        "/api/v1/investigate/warranty/models", params=_params(filters, page=99, page_size=10)
    )
    invalid_page = api_client.get("/api/v1/investigate/warranty/models?page=0")
    invalid_size = api_client.get("/api/v1/investigate/warranty/models?page_size=11")
    invalid_sort = api_client.get(
        "/api/v1/investigate/warranty/models?sort_by=not_a_column&sort_dir=asc"
    )

    assert first.status_code == 200
    assert first.json()["data"]["total"] == 8
    assert beyond.status_code == 200 and beyond.json()["data"]["records"] == []
    assert invalid_page.status_code == invalid_size.status_code == invalid_sort.status_code == 422


def test_full_csv_and_pdf_exports_ignore_page_and_preserve_sort(api_client):
    authenticate(api_client)
    expected = load_baseline()["investigate"]
    model = quote(expected["selected_model"], safe="")
    branch = quote(expected["selected_branch"], safe="")
    base = f"/api/v1/investigate/warranty/models/{model}/branches/{branch}/claims"
    params = _params(expected["filters"], sort_by="approved_amount", sort_dir="asc")

    all_response = api_client.get(base, params=[*params, ("page", "1"), ("page_size", "50")])
    csv_response = api_client.get(f"{base}.csv", params=params)
    pdf_response = api_client.get(f"{base}.pdf", params=params)
    csv_frame = pd.read_csv(StringIO(csv_response.text))

    assert all_response.status_code == csv_response.status_code == pdf_response.status_code == 200
    assert len(csv_frame) == all_response.json()["data"]["total"] == expected["claims"]["row_count"]
    assert csv_frame["approved_amount"].tolist() == sorted(csv_frame["approved_amount"].tolist())
    assert pdf_response.content.startswith(b"%PDF")
    assert "attachment" in csv_response.headers["content-disposition"]
    assert "attachment" in pdf_response.headers["content-disposition"]


def test_investigate_routes_require_authentication(api_client):
    assert api_client.get("/api/v1/investigate/warranty/models").status_code == 401
