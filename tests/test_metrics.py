"""Formula, filter-safety, and DuckDB parity tests for business metrics."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import duckdb
import pandas as pd
import pytest

from src.analytics.metrics import (
    AnalyticsData, Filters, gross_margin, gross_margin_by_model, overview_kpis,
    revenue, revenue_by_branch, warranty_claims,
)


ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / "data" / "business.duckdb"
TABLE_NAMES = [
    "branches", "models", "salespeople", "inventory", "sales",
    "service_records", "warranty_claims", "complaints", "satisfaction",
]


@pytest.fixture
def small_frames() -> AnalyticsData:
    """Three sales whose expected totals can be calculated by hand."""
    return AnalyticsData(
        branches=pd.DataFrame(
            {
                "branch_id": [1, 2],
                "branch_name": ["Accra", "Kumasi"],
            }
        ),
        models=pd.DataFrame(
            {
                "model_id": [1],
                "model_name": ["Corolla"],
                "manufacturer": ["Toyota"],
            }
        ),
        salespeople=pd.DataFrame(
            {
                "salesperson_id": [1, 2],
                "employee_code": ["E1", "E2"],
                "first_name": ["Ama", "Kojo"],
                "last_name": ["Mensah", "Owusu"],
            }
        ),
        inventory=pd.DataFrame(
            {
                "inventory_id": [1, 2, 3],
                "vin": ["AAAAAAAAA00000001", "BBBBBBBBB00000002", "CCCCCCCCC00000003"],
                "model_id": [1, 1, 1],
                "acquisition_cost": [8_000.0, 12_000.0, 18_000.0],
                "arrival_date": ["2024-01-01", "2024-01-02", "2024-01-03"],
                "sold_date": ["2024-01-10", "2024-01-11", "2024-01-12"],
                "inventory_status": ["sold", "sold", "sold"],
            }
        ),
        sales=pd.DataFrame(
            {
                "sale_id": [1, 2, 3],
                "inventory_id": [1, 2, 3],
                "branch_id": [1, 1, 2],
                "salesperson_id": [1, 1, 2],
                "sale_date": ["2024-01-10", "2024-01-11", "2024-01-12"],
                "sale_status": ["completed", "completed", "completed"],
                # net_sale_price is the repository's canonical selling_price.
                "net_sale_price": [10_000.0, 15_000.0, 20_000.0],
                "gross_price": [10_000.0, 15_000.0, 20_000.0],
                "discount_amount": [0.0, 0.0, 0.0],
                "_row_quality_status": ["VALID", "VALID", "VALID"],
            }
        ),
        service_records=pd.DataFrame(),
        warranty_claims=pd.DataFrame(),
        complaints=pd.DataFrame(),
        satisfaction=pd.DataFrame(),
    )


def _analytics_data_from_database(connection: duckdb.DuckDBPyConnection) -> AnalyticsData:
    """Load database tables outside the pure metric functions."""
    frames = {name: connection.execute(f"SELECT * FROM {name}").fetchdf() for name in TABLE_NAMES}
    return AnalyticsData(**frames)


def test_revenue_and_margin_formulas_on_small_frames(small_frames: AnalyticsData) -> None:
    """Revenue=45,000; cost=38,000; margin=7,000; margin%=7,000/45,000."""
    revenue_result = revenue(small_frames, Filters())
    margin_result = gross_margin(small_frames, Filters())

    total_revenue = revenue_result["revenue"].sum()
    total_cost = margin_result["acquisition_cost"].sum()
    total_margin = margin_result["gross_margin"].sum()
    margin_percent = total_margin / margin_result["selling_price"].sum()

    assert total_revenue == 45_000.0
    assert total_cost == 38_000.0
    assert total_margin == 7_000.0
    assert margin_percent == 7_000.0 / 45_000.0


def test_filters_are_exact_and_do_not_mutate_inputs(small_frames: AnalyticsData) -> None:
    """Exact branch/person/date filters must select rows without changing inputs."""
    original_sales = small_frames.sales.copy(deep=True)
    original_inventory = small_frames.inventory.copy(deep=True)

    result = revenue(
        small_frames,
        Filters(
            start_date="2024-01-10",
            end_date="2024-01-11",
            branch=(1,),
            salesperson=(1,),
            status=("completed",),
        ),
    )

    assert result["revenue"].sum() == 25_000.0
    assert result["transaction_count"].sum() == 2
    pd.testing.assert_frame_equal(small_frames.sales, original_sales)
    pd.testing.assert_frame_equal(small_frames.inventory, original_inventory)


def test_missing_and_heavily_null_prices_do_not_crash_metrics(small_frames: AnalyticsData) -> None:
    """A 30% null shock or missing price column must degrade safely."""
    null_prices = small_frames.sales.copy(deep=True)
    null_prices.loc[null_prices.index[:1], "net_sale_price"] = pd.NA
    null_data = AnalyticsData(**{
        **small_frames.__dict__,
        "sales": null_prices,
    })
    assert revenue(null_data, Filters())["revenue"].sum() == 35_000.0

    missing_price_data = AnalyticsData(**{
        **small_frames.__dict__,
        "sales": small_frames.sales.drop(columns=["net_sale_price"]),
    })
    assert revenue(missing_price_data, Filters()).empty
    assert gross_margin(missing_price_data, Filters()).empty
    assert revenue_by_branch(missing_price_data, Filters()).empty
    assert gross_margin_by_model(missing_price_data, Filters()).empty
    degraded_kpis = overview_kpis(missing_price_data, Filters())
    assert set(degraded_kpis["metric"]) == {
        "Revenue", "Gross margin", "Units sold", "Discount rate"
    }


def test_all_metrics_return_expected_columns_and_rows() -> None:
    """Metric revenue must exactly match one-row-per-sale raw SQL revenue."""
    assert DATABASE_PATH.exists(), "Run scripts/build_database.py before pytest."

    connection = duckdb.connect(str(DATABASE_PATH), read_only=False)
    try:
        # The current normalized database has sales.net_sale_price instead of a
        # physical car_sales.selling_price column. This temporary compatibility
        # view keeps one row per sale and makes the requested raw SQL check exact.
        connection.execute(
            """
                CREATE OR REPLACE TEMP VIEW car_sales AS
                SELECT DISTINCT
                    s.sale_id,
                    CAST(s.net_sale_price AS DECIMAL(18, 2)) AS selling_price,
                    s.gross_price AS list_price,
                    1 AS quantity
                FROM sales s
                INNER JOIN inventory i ON s.inventory_id = i.inventory_id
                WHERE s.sale_status = 'completed'
                  AND COALESCE(s._row_quality_status, 'VALID') <> 'ERROR'
                  AND COALESCE(i._row_quality_status, 'VALID') <> 'ERROR'
                """
        )
        sql_revenue = connection.execute(
            "SELECT COALESCE(SUM(selling_price), 0) AS sql_revenue FROM car_sales"
        ).fetchone()[0]
        data = _analytics_data_from_database(connection)
    finally:
        connection.close()

    metric_result = revenue(data, Filters())
    metric_revenue = sum(
        (Decimal(str(value)) for value in metric_result["revenue"].dropna()),
        start=Decimal("0.00"),
    ).quantize(Decimal("0.01"))
    sql_revenue = Decimal(sql_revenue).quantize(Decimal("0.01"))

    assert set(metric_result.columns) == {"period", "revenue", "transaction_count"}
    assert len(metric_result) > 0
    assert metric_revenue == sql_revenue

    model_margin = gross_margin_by_model(data, Filters())
    assert not model_margin["model"].astype(str).str.contains(
        "unresolved|Unmapped", case=False, regex=True
    ).any()

    branch_revenue = revenue_by_branch(data, Filters())
    warranty = warranty_claims(data, Filters())
    assert not branch_revenue["branch"].astype(str).str.contains(
        "unresolved|Unmapped|Model ID", case=False, regex=True
    ).any()
    assert not warranty["model"].astype(str).str.contains(
        "unresolved|Unmapped|Model ID", case=False, regex=True
    ).any()
