"""Tests for evidence-preserving warranty drill-down analytics."""

import pandas as pd

from src.analytics.drilldown import warranty_by_branch, warranty_by_model, warranty_claim_records
from src.analytics.metrics import AnalyticsData, Filters


def _data() -> AnalyticsData:
    empty = pd.DataFrame()
    return AnalyticsData(
        branches=pd.DataFrame({"branch_id": [1, 2], "branch_name": ["Accra", "Kumasi"], "branch_code": ["ACC", "KMS"]}),
        models=pd.DataFrame({"model_id": [10], "model_name": ["Hilux"], "manufacturer": ["Toyota"]}),
        salespeople=pd.DataFrame({"salesperson_id": [7], "employee_code": ["SP007"], "first_name": ["Ama"], "last_name": ["Mensah"]}),
        inventory=pd.DataFrame({"inventory_id": [100, 101], "model_id": [10, 10]}),
        sales=pd.DataFrame({"sale_id": [1000, 1001], "salesperson_id": [7, 7], "sale_status": ["completed", "completed"]}),
        warranty_claims=pd.DataFrame({
            "claim_id": [1, 2, 3], "claim_date": ["2025-01-10", "2025-01-20", "2024-12-10"],
            "inventory_id": [100, 101, 100], "sale_id": [1000, 1001, 1000], "service_id": [50, 51, 49],
            "branch_id": [1, 2, 1], "failure_category": ["Engine", "Electrical", "Engine"],
            "claim_description": ["A", "B", "C"], "claim_status": ["approved"] * 3,
            "claim_amount": [120.0, 240.0, 80.0], "approved_amount": [100.0, 200.0, 50.0],
            "manufacturer_recovery_amount": [0.0, 0.0, 0.0], "_row_quality_status": ["VALID"] * 3,
        }),
        service_records=empty, complaints=empty, satisfaction=empty,
    )


def test_warranty_drilldown_reconciles_summary_branch_and_records():
    data = _data()
    filters = Filters(start_date="2025-01-01", end_date="2025-01-31")

    models = warranty_by_model(data, filters)
    branches = warranty_by_branch(data, filters, "Hilux")
    accra_records = warranty_claim_records(data, filters, "Hilux", "Accra")

    assert models.loc[0, "claim_cost"] == 300.0
    assert models.loc[0, "previous_claim_cost"] == 50.0
    assert models.loc[0, "cost_change"] == 250.0
    assert branches["claim_cost"].sum() == models.loc[0, "claim_cost"]
    assert accra_records["approved_amount"].sum() == branches.loc[branches["branch"] == "Accra", "claim_cost"].iloc[0]


def test_warranty_drilldown_preserves_exact_global_filters():
    result = warranty_by_model(
        _data(),
        Filters(start_date="2025-01-01", end_date="2025-01-31", branch=("Kumasi",), brand=("Toyota",), status=("completed",)),
    )

    assert result.loc[0, "model"] == "Hilux"
    assert result.loc[0, "claim_count"] == 1
    assert result.loc[0, "claim_cost"] == 200.0
