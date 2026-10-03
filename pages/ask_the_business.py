"""Ask the Business: evidence-backed natural-language exploration."""

from __future__ import annotations

import os
from pathlib import Path
import re
from typing import Any

import duckdb
from google import genai
import streamlit as st

from src.ai.guardrails import build_grounded_response


DATABASE_PATH = Path("data/business.duckdb")
FORBIDDEN_SQL = re.compile(
    r"\b(ALTER|ATTACH|COPY|CREATE|DELETE|DETACH|DROP|EXPORT|IMPORT|INSERT|INSTALL|LOAD|PRAGMA|TRUNCATE|UPDATE)\b",
    re.IGNORECASE,
)


def api_key() -> str:
    """Return the Gemini key from Streamlit secrets or the environment."""
    try:
        return str(st.secrets["GEMINI_API_KEY"]).strip()
    except Exception:
        return os.getenv("GEMINI_API_KEY", "").strip()


def validate_read_only_sql(query: str) -> str:
    """Accept one read-only SELECT/CTE statement and reject unsafe SQL."""
    cleaned = query.strip().removesuffix(";").strip()
    if not cleaned or not re.match(r"^(SELECT|WITH)\b", cleaned, re.IGNORECASE):
        raise ValueError("The generated query was not a SELECT statement.")
    if ";" in cleaned or FORBIDDEN_SQL.search(cleaned):
        raise ValueError("The generated query contained a disallowed SQL operation.")
    return cleaned


def scalar(connection: duckdb.DuckDBPyConnection, query: str) -> Any:
    """Return the first query value, or zero when no row is returned."""
    row = connection.execute(query).fetchone()
    return row[0] if row is not None else 0


@st.cache_data(show_spinner="Loading business context…")
def load_business_context(database_path: str, modified_at: float) -> tuple[str, dict[str, float]]:
    """Load the database schema and trusted headline values."""
    del modified_at
    with duckdb.connect(database_path, read_only=True) as connection:
        table_names = [row[0] for row in connection.execute("SHOW TABLES").fetchall()]
        schema_parts = []
        for table_name in table_names:
            columns = connection.execute(f'DESCRIBE "{table_name}"').fetchall()
            schema_parts.append(
                f"TABLE {table_name} (" + ", ".join(f"{column[0]} {column[1]}" for column in columns) + ")"
            )
        kpis = {
            "revenue": float(scalar(connection,
                "SELECT COALESCE(SUM(net_sale_price), 0) FROM sales "
                "WHERE sale_status = 'completed' AND COALESCE(_row_quality_status, 'VALID') <> 'ERROR'"
            )),
            "sales": int(scalar(connection,
                "SELECT COUNT(*) FROM sales WHERE sale_status = 'completed' "
                "AND COALESCE(_row_quality_status, 'VALID') <> 'ERROR'"
            )),
            "branches": int(scalar(connection,
                "SELECT COUNT(*) FROM branches WHERE branch_name IS NOT NULL"
            )),
            "aged_inventory": int(scalar(connection,
                "SELECT COUNT(*) FROM inventory WHERE inventory_status = 'available' "
                "AND arrival_date IS NOT NULL AND date_diff('day', arrival_date, record_updated_at) > 90 "
                "AND COALESCE(_row_quality_status, 'VALID') <> 'ERROR'"
            )),
        }
    return "\n".join(schema_parts), kpis


def format_money(value: float) -> str:
    if value >= 1_000_000_000:
        return f"GHS {value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"GHS {value / 1_000_000:.1f}M"
    return f"GHS {value:,.0f}"


st.session_state.setdefault("business_messages", [])
st.session_state.setdefault("business_current_df", None)

with st.sidebar:
    st.subheader("AI analyst")
    if st.button("Clear chat history", icon=":material/delete:", width="stretch"):
        st.session_state.business_messages = []
        st.session_state.business_current_df = None
        st.rerun()
    if st.button("Refresh business data", icon=":material/refresh:", width="stretch"):
        st.cache_data.clear()
        st.rerun()

st.title("Ask the Business")
st.caption("Ask a question, inspect the returned records, and verify the evidence behind the answer.")

if not DATABASE_PATH.exists():
    st.error("The analytical database is unavailable. Run `python scripts/build_database.py` and refresh this page.")
    st.stop()

schema, kpis = load_business_context(str(DATABASE_PATH), DATABASE_PATH.stat().st_mtime)

with st.container(horizontal=True):
    st.metric("Completed-sale revenue", format_money(kpis["revenue"]), border=True)
    st.metric("Completed sales", f'{kpis["sales"]:,.0f}', border=True)
    st.metric("Branches", f'{kpis["branches"]:,.0f}', border=True)
    st.metric("Available over 90 days", f'{kpis["aged_inventory"]:,.0f}', border=True)

ask_tab, history_tab = st.tabs(["Ask", "History"])

with ask_tab:
    suggestions = {
        "Revenue trend": "How did completed-sale revenue change by month?",
        "Best branch": "Which branch had the highest completed-sale revenue?",
        "Aged inventory": "Which available vehicles have been in inventory for more than 90 days?",
        "Most complaints": "Which branch had the most valid complaints?",
    }
    selected = st.pills("Quick questions", list(suggestions), key="business_suggestion")

    for message in st.session_state.business_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    submitted = st.chat_input("Ask about sales, inventory, warranty, service, or complaints", submit_mode="disable")
    question = suggestions.get(selected) if selected else submitted

    if question:
        st.session_state.business_messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        key = api_key()
        if not key:
            with st.chat_message("assistant"):
                st.warning("Add `GEMINI_API_KEY` to `.env` or Streamlit secrets to enable AI questions.")
            st.stop()

        with st.chat_message("assistant"):
            client: genai.Client | None = None
            try:
                client = genai.Client(api_key=key)
                model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
                sql_prompt = f"""You query a DuckDB automotive business database.
Schema:
{schema}

Question: {question}

Return exactly one read-only SELECT or WITH query. Do not use markdown.
Use cleaned canonical fields, exclude rows whose _row_quality_status is ERROR,
exclude orphan relationships, use net_sale_price for revenue, and limit detailed
record queries to 100 rows."""
                generated = client.models.generate_content(
                    model=model_name, contents=sql_prompt
                ).text or ""
                sql_query = validate_read_only_sql(
                    generated.replace("```sql", "").replace("```", "").strip()
                )
                with duckdb.connect(str(DATABASE_PATH), read_only=True) as connection:
                    result = connection.execute(sql_query).fetchdf()
                st.session_state.business_current_df = result

                if result.empty:
                    st.info("No valid records matched this question.")
                else:
                    st.dataframe(result, hide_index=True, width="stretch")
                    st.download_button(
                        "Download evidence as CSV", result.to_csv(index=False).encode("utf-8"),
                        "business_evidence.csv", "text/csv", icon=":material/download:",
                    )

                evidence = [
                    {str(field): value for field, value in record.items()}
                    for record in result.to_dict(orient="records")
                ]
                explanation_prompt = f"""Question: {question}
Evidence records: {result.to_json(orient='records', date_format='iso')[:12000]}

Respond with a FACTS: section followed by a short explanation. Every number in
FACTS must appear exactly in the evidence. Do not invent causes or recommendations."""
                model_response = client.models.generate_content(
                    model=model_name, contents=explanation_prompt
                ).text or ""
                fallback = "The query completed. Use the evidence table above as the verified result."
                grounded = build_grounded_response(model_response, evidence, fallback)
                if grounded["status"] != "verified":
                    st.warning(grounded.get("warning", "The AI response could not be verified."))
                st.markdown(grounded["response"])
                with st.expander("Evidence query"):
                    st.code(sql_query, language="sql")
                st.session_state.business_messages.append(
                    {"role": "assistant", "content": grounded["response"]}
                )
            except Exception as exc:
                st.error(f"Could not answer safely: {exc}")
            finally:
                if client is not None:
                    client.close()

with history_tab:
    if not st.session_state.business_messages:
        st.info("No questions have been asked in this session.")
    else:
        for message in st.session_state.business_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
