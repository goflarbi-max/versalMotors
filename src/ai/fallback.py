"""Deterministic, allowlisted question handling used when Gemini is unavailable."""

from typing import Any, Callable

import pandas as pd


def fallback_sql_for_question(question: str) -> tuple[str | None, str]:
    """Map supported intents to reviewed DuckDB queries without fuzzy SQL generation."""
    text = question.lower()
    valid = "COALESCE(_row_quality_status, 'VALID') <> 'ERROR'"

    if "revenue" in text and any(word in text for word in ("month", "trend", "change")):
        return f"""
            WITH monthly AS (
                SELECT date_trunc('month', sale_date)::DATE AS month,
                       SUM(net_sale_price) AS revenue
                FROM sales
                WHERE sale_status = 'completed' AND {valid}
                GROUP BY 1
            )
            SELECT month, revenue,
                   LAG(revenue) OVER (ORDER BY month) AS previous_month_revenue,
                   revenue - LAG(revenue) OVER (ORDER BY month) AS change_amount,
                   CASE
                       WHEN LAG(revenue) OVER (ORDER BY month) IS NULL
                         OR LAG(revenue) OVER (ORDER BY month) = 0 THEN NULL
                       ELSE 100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
                            / LAG(revenue) OVER (ORDER BY month)
                   END AS change_pct
            FROM monthly ORDER BY month
        """, "Showing the reviewed monthly completed-sales revenue query."
    if "branch" in text and any(word in text for word in ("best", "highest", "revenue", "top")):
        return f"""
            SELECT b.branch_name, SUM(s.net_sale_price) AS revenue
            FROM sales s LEFT JOIN branches b ON s.branch_id = b.branch_id
            WHERE s.sale_status = 'completed'
              AND COALESCE(s._row_quality_status, 'VALID') <> 'ERROR'
            GROUP BY 1 ORDER BY revenue DESC LIMIT 10
        """, "Showing the reviewed completed-sales revenue ranking by branch."
    if "inventory" in text and any(word in text for word in ("90", "aged", "old")):
        return """
            SELECT inventory_id, vin, branch_id, model_id, arrival_date,
                   date_diff('day', arrival_date, record_updated_at) AS age_days
            FROM inventory
            WHERE inventory_status = 'available' AND arrival_date IS NOT NULL
              AND date_diff('day', arrival_date, record_updated_at) > 90
              AND COALESCE(_row_quality_status, 'VALID') <> 'ERROR'
            ORDER BY age_days DESC LIMIT 100
        """, "Showing the reviewed available-inventory aging query."
    if "complaint" in text:
        return """
            SELECT c.branch_id, b.branch_name, COUNT(*) AS complaint_count
            FROM complaints c
            LEFT JOIN branches b ON c.branch_id = b.branch_id
            WHERE COALESCE(c._row_quality_status, 'VALID') <> 'ERROR'
            GROUP BY 1, 2 ORDER BY complaint_count DESC LIMIT 10
        """, "Showing the reviewed valid-complaint count by branch."
    return None, (
        "Gemini is unavailable and this question has no reviewed offline query yet. "
        "Try Revenue trend, Best branch, Aged inventory, or Complaints."
    )


def build_fallback_evidence(question: str, result: pd.DataFrame) -> list[dict[str, Any]]:
    """Convert reviewed tool results into fact evidence without inventing values."""
    if result.empty:
        return []
    lowered = question.lower()
    source_table = "complaints" if "complaint" in lowered else "inventory" if "inventory" in lowered else "sales"
    evidence = []
    for position, row in enumerate(result.to_dict("records"), start=1):
        values = {str(key): value for key, value in row.items()}
        evidence.append({
            "id": f"OFFLINE-{position:03d}",
            "type": "fact",
            "statement": "; ".join(f"{key}={value}" for key, value in values.items()),
            "value": values,
            "comparison": None,
            "filters": {},
            "source_table": source_table,
        })
    return evidence


def fallback_response(question: str, evidence: list[dict[str, Any]]) -> str:
    """Return a safe statement containing no number computed outside evidence."""
    if not evidence:
        return "No matching verified records were found for this question."
    lowered = question.lower()
    values = evidence[0]["value"]
    if "complaint" in lowered:
        branch = values.get("branch_name") or f"branch {values.get('branch_id')}"
        return f"{branch} had the most valid complaints, with {values.get('complaint_count'):,}."
    if "branch" in lowered and "revenue" in lowered:
        branch = values.get("branch_name") or "The highest-ranked branch"
        return f"{branch} had the highest completed-sale revenue at GHS {values.get('revenue'):,.2f}."
    if "revenue" in lowered:
        latest = evidence[-1]["value"]
        month = pd.Timestamp(latest["month"]).strftime("%B %Y")
        revenue = latest.get("revenue")
        change = latest.get("change_amount")
        change_pct = latest.get("change_pct")
        if pd.isna(change) or pd.isna(change_pct):
            return f"Completed-sale revenue in {month} was GHS {revenue:,.2f}; no prior month is available for comparison."
        direction = "increased" if change >= 0 else "decreased"
        return (
            f"Completed-sale revenue in {month} was GHS {revenue:,.2f}. "
            f"It {direction} by GHS {abs(change):,.2f} ({abs(change_pct):,.1f}%) from the previous month."
        )
    if "inventory" in lowered:
        vin = values.get("vin") or values.get("inventory_id")
        return f"The oldest available vehicle is {vin}, at {values.get('age_days'):,} days in inventory."
    if "branch" in lowered:
        return f"The highest-ranked verified branch result is {evidence[0]['statement']}."
    return "Verified database evidence is shown below."


def run_with_reviewed_fallback(
    question: str,
    generated_sql: str | None,
    runner: Callable[[str], pd.DataFrame],
) -> tuple[pd.DataFrame | None, str, bool]:
    """Run generated SQL once, then use the reviewed route if it is rejected."""
    if generated_sql:
        try:
            return runner(generated_sql), "Gemini query succeeded.", False
        except Exception:
            pass
    reviewed_sql, message = fallback_sql_for_question(question)
    if not reviewed_sql:
        return None, message, True
    return runner(reviewed_sql), message, True
