"""Deterministic, allowlisted question handling used when Gemini is unavailable."""


def fallback_sql_for_question(question: str) -> tuple[str | None, str]:
    """Map supported intents to reviewed DuckDB queries without fuzzy SQL generation."""
    text = question.lower()
    valid = "COALESCE(_row_quality_status, 'VALID') <> 'ERROR'"

    if "revenue" in text and any(word in text for word in ("month", "trend", "change")):
        return f"""
            SELECT date_trunc('month', sale_date)::DATE AS month,
                   SUM(net_sale_price) AS revenue
            FROM sales
            WHERE sale_status = 'completed' AND {valid}
            GROUP BY 1 ORDER BY 1
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
            SELECT branch_id, COUNT(*) AS complaint_count
            FROM complaints
            WHERE COALESCE(_row_quality_status, 'VALID') <> 'ERROR'
            GROUP BY 1 ORDER BY complaint_count DESC LIMIT 10
        """, "Showing the reviewed valid-complaint count by branch."
    return None, (
        "Gemini is unavailable and this question has no reviewed offline query yet. "
        "Try Revenue trend, Best branch, Aged inventory, or Complaints."
    )
