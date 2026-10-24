"""Framework-neutral orchestration over the existing Ask the Business tools."""

from __future__ import annotations

import os
from typing import Any

from backend.app.services.data_loader import DataBundle
from backend.app.services.serialization import frame_records, json_value
from src.ai.fallback import (
    build_fallback_evidence,
    fallback_response,
    run_with_reviewed_fallback,
)
from src.ai.gemini_client import generate_text
from src.ai.guardrails import build_grounded_response, handle_unanswerable, validate_question
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


def _schema(bundle: DataBundle) -> str:
    return "\n".join(
        f"TABLE {table} ({', '.join(str(column) for column in frame.columns)})"
        for table, frame in bundle.analytics.__dict__.items()
    )


def answer_question(question: str, bundle: DataBundle) -> dict[str, Any]:
    valid, error = validate_question(question)
    if not valid:
        return {"status": "invalid", "mode": "guardrail", "answer": error, "facts": None, "interpretation": None, "recommendations": [], "evidence": [], "table": []}
    unsupported = handle_unanswerable(question)
    if unsupported:
        return {"status": "unanswerable", "mode": "safe_refusal", "answer": unsupported, "facts": None, "interpretation": None, "recommendations": [], "evidence": [], "table": []}

    reviewed = question.strip() in SUGGESTIONS.values()
    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    sql_result = {"ok": False, "text": "", "reason": "reviewed_quick_question"}
    if not reviewed:
        prompt = (
            f"Schema:\n{_schema(bundle)}\nQuestion: {question}\n"
            "Return one DuckDB SELECT only. Use net_sale_price for revenue, "
            "exclude ERROR rows, and limit detail to 100 rows."
        )
        sql_result = generate_text(prompt, model=model)
    generated_sql = None
    if sql_result["ok"]:
        generated_sql = str(sql_result["text"]).replace("```sql", "").replace("```", "").strip()

    result, mode_message, used_fallback = run_with_reviewed_fallback(
        question, generated_sql, run_readonly_sql
    )
    if result is None:
        return {"status": "unanswerable", "mode": "reviewed_fallback", "answer": mode_message, "facts": None, "interpretation": None, "recommendations": [], "evidence": [], "table": []}

    evidence = build_fallback_evidence(question, result)
    deterministic = fallback_response(question, evidence)
    answer_result = {"ok": False, "text": "", "reason": "deterministic_fallback"}
    if not used_fallback:
        answer_prompt = (
            f"Question: {question}\nEvidence: {result.to_json(orient='records', date_format='iso')[:12000]}\n"
            "Answer directly and concisely. Use only numbers in evidence; do not add a FACTS heading."
        )
        answer_result = generate_text(answer_prompt, model=model)
    grounded = build_grounded_response(str(answer_result["text"]), evidence, deterministic)
    mode = "ai" if grounded["status"] == "verified" else "reviewed_fallback"
    return {
        "status": grounded["status"],
        "mode": mode,
        "answer": grounded["response"],
        "facts": grounded["response"],
        "interpretation": None,
        "recommendations": [],
        "evidence": json_value(evidence),
        "table": frame_records(result),
    }
