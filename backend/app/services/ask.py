"""Framework-neutral orchestration over the existing Ask the Business tools."""

from __future__ import annotations

from typing import Any

from backend.app.services.serialization import frame_records, json_value
from src.ai.fallback import (
    build_fallback_evidence,
    fallback_response,
    fallback_sql_for_question,
)
from src.ai.guardrails import handle_unanswerable, validate_question
from src.database.connection import run_readonly_sql

SUGGESTIONS = {
    "Revenue trend": "How did completed-sale revenue change by month?",
    "Best branch": "Which branch had the highest completed-sale revenue?",
    "Aged inventory": "Which available vehicles have been in inventory over 90 days?",
    "Complaints": "Which branch had the most valid complaints?",
}

SUMMARY_QUERIES = {
    "revenue": "SELECT COALESCE(SUM(net_sale_price),0) AS metric_value FROM sales WHERE sale_status='completed' AND COALESCE(_row_quality_status,'VALID')<>'ERROR'",
    "completed_sales": "SELECT COUNT(*) AS metric_value FROM sales WHERE sale_status='completed' AND COALESCE(_row_quality_status,'VALID')<>'ERROR'",
    "branches": "SELECT COUNT(*) AS metric_value FROM branches WHERE branch_name IS NOT NULL",
    "available_over_90_days": "SELECT COUNT(*) AS metric_value FROM inventory WHERE inventory_status='available' AND arrival_date IS NOT NULL AND date_diff('day',arrival_date,record_updated_at)>90 AND COALESCE(_row_quality_status,'VALID')<>'ERROR'",
}


def summary() -> dict[str, Any]:
    values = {
        key: float(run_readonly_sql(sql).iloc[0, 0])
        for key, sql in SUMMARY_QUERIES.items()
    }
    values["completed_sales"] = int(values["completed_sales"])
    values["branches"] = int(values["branches"])
    values["available_over_90_days"] = int(values["available_over_90_days"])
    return {
        "values": values,
        "display": {
            "revenue": f"GHS {values['revenue'] / 1_000_000_000:.2f}B",
            "completed_sales": f"{values['completed_sales']:,}",
            "branches": f"{values['branches']:,}",
            "available_over_90_days": f"{values['available_over_90_days']:,}",
        },
    }


def answer_question(question: str, _bundle: object) -> dict[str, Any]:
    """Answer only through reviewed SQL and deterministic evidence summaries."""
    valid, error = validate_question(question)
    if not valid:
        return {"status": "invalid", "mode": "guardrail", "answer": error, "facts": None, "interpretation": None, "recommendations": [], "evidence": [], "table": []}
    unsupported = handle_unanswerable(question)
    if unsupported:
        return {"status": "unanswerable", "mode": "safe_refusal", "answer": unsupported, "facts": None, "interpretation": None, "recommendations": [], "evidence": [], "table": []}

    reviewed_sql, _ = fallback_sql_for_question(question)
    if not reviewed_sql:
        return {
            "status": "unanswerable",
            "mode": "deterministic",
            "answer": (
                "This question does not match a reviewed VersalMotors data query yet. "
                "Try Revenue trend, Best branch, Aged inventory, or Complaints."
            ),
            "facts": None,
            "interpretation": None,
            "recommendations": [],
            "evidence": [],
            "table": [],
        }

    result = run_readonly_sql(reviewed_sql)
    evidence = build_fallback_evidence(question, result)
    deterministic = fallback_response(question, evidence)
    return {
        "status": "verified",
        "mode": "deterministic",
        "answer": deterministic,
        "facts": deterministic,
        "interpretation": None,
        "recommendations": [],
        "evidence": json_value(evidence),
        "table": frame_records(result),
    }
