"""Compare Streamlit-source outputs with the FastAPI adapters for ten filters."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.services import ask as api_ask
from backend.app.services import investigate as api_investigate
from backend.app.services import overview as api_overview
from backend.app.services.data_loader import get_data_bundle
from backend.app.services.serialization import frame_records
from src.analytics.drilldown import warranty_by_model
from src.analytics.metrics import (
    Filters,
    gross_margin_by_model,
    overview_kpis,
    revenue,
    revenue_by_branch,
)
from src.database.connection import run_readonly_sql


OUTPUT = ROOT / "docs" / "screenshots" / "parity" / "number-parity.json"


def records_match(frame: pd.DataFrame, records: list[dict]) -> bool:
    return frame_records(frame) == records


def total(records: list[dict], field: str) -> float:
    return float(sum(float(row.get(field) or 0) for row in records))


def scenarios() -> dict[str, Filters]:
    return {
        "default_90_days": Filters(start_date="2025-04-02", end_date="2025-06-30"),
        "full_range": Filters(start_date="2022-11-10", end_date="2025-06-30"),
        "branch_accra": Filters(start_date="2022-11-10", end_date="2025-06-30", branch=("Accra",)),
        "branch_kumasi_90_days": Filters(start_date="2025-04-02", end_date="2025-06-30", branch=("Kumasi",)),
        "model_hilux": Filters(start_date="2022-11-10", end_date="2025-06-30", model=("Hilux",)),
        "model_corolla_90_days": Filters(start_date="2025-04-02", end_date="2025-06-30", model=("Corolla",)),
        "brand_elara": Filters(start_date="2022-11-10", end_date="2025-06-30", brand=("Elara",)),
        "completed_90_days": Filters(start_date="2025-04-02", end_date="2025-06-30", status=("completed",)),
        "single_day": Filters(start_date="2025-06-30", end_date="2025-06-30"),
        "valid_empty_pair": Filters(start_date="2025-04-02", end_date="2025-06-30", branch=("Kasoa",), model=("Yaris",)),
    }


def main() -> None:
    bundle = get_data_bundle(force_reload=True)
    results: dict[str, object] = {"scenarios": {}, "mismatches": []}
    mismatches: list[str] = results["mismatches"]  # type: ignore[assignment]

    for name, filters in scenarios().items():
        source_kpis = overview_kpis(bundle.analytics, filters)
        source_trend = revenue(bundle.analytics, filters)
        source_branches = revenue_by_branch(bundle.analytics, filters)
        source_models = gross_margin_by_model(bundle.analytics, filters)
        source_warranty = warranty_by_model(bundle.analytics, filters)

        api_kpis = api_overview.kpis(bundle, filters)
        api_trend = api_overview.revenue_trend(bundle, filters)
        api_branches = api_overview.branch_revenue(bundle, filters)
        api_models = api_overview.model_margin(bundle, filters)
        api_warranty_total = api_investigate.model_page(
            bundle, filters, page=1, page_size=50, sort_by=None, sort_dir="original"
        ).total

        checks = {
            "kpis": records_match(source_kpis, api_kpis),
            "revenue_chart": records_match(source_trend, api_trend),
            "branch_chart": records_match(source_branches, api_branches),
            "model_chart": records_match(source_models, api_models),
            "warranty_table_row_count": len(source_warranty) == api_warranty_total,
        }
        for check, matched in checks.items():
            if not matched:
                mismatches.append(f"{name}.{check}")

        results["scenarios"][name] = {  # type: ignore[index]
            "filters": asdict(filters),
            "matches": checks,
            "kpis": api_kpis,
            "chart_totals": {
                "revenue_trend": total(api_trend, "revenue"),
                "revenue_by_branch": total(api_branches, "revenue"),
                "gross_margin_by_model": total(api_models, "gross_margin"),
            },
            "chart_rows": {
                "revenue_trend": len(api_trend),
                "revenue_by_branch": len(api_branches),
                "gross_margin_by_model": len(api_models),
            },
            "warranty_table_rows": api_warranty_total,
        }

    direct_ask = {
        key: float(run_readonly_sql(query).iloc[0, 0])
        for key, query in api_ask.SUMMARY_QUERIES.items()
    }
    api_summary = api_ask.summary()
    ask_matches = all(
        float(api_summary["values"][key]) == value for key, value in direct_ask.items()
    )
    if not ask_matches:
        mismatches.append("ask_summary_cards")
    results["ask_summary"] = {
        "streamlit_direct_values": direct_ask,
        "nextjs_api_values": api_summary["values"],
        "nextjs_display": api_summary["display"],
        "matches": ask_matches,
        "note": "Both implementations expose these four cards without shared filters.",
    }
    results["all_match"] = not mismatches
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    print(f"Scenarios: {len(scenarios())}; mismatches: {len(mismatches)}")
    if mismatches:
        raise SystemExit("Parity mismatches: " + ", ".join(mismatches))


if __name__ == "__main__":
    main()
