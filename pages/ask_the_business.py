"""Evidence-backed natural-language business questions."""

import os

import streamlit as st

from src.ai.fallback import (
    build_fallback_evidence,
    fallback_response,
    run_with_reviewed_fallback,
)
from src.ai.gemini_client import generate_text
from src.ai.guardrails import build_grounded_response, handle_unanswerable, validate_question
from src.database.connection import get_connection, run_readonly_sql


SUGGESTIONS = {
    "Revenue trend": "How did completed-sale revenue change by month?",
    "Best branch": "Which branch had the highest completed-sale revenue?",
    "Aged inventory": "Which available vehicles have been in inventory over 90 days?",
    "Complaints": "Which branch had the most valid complaints?",
}


@st.cache_data(show_spinner="Loading business context…")
def load_context() -> tuple[str, dict[str, float]]:
    connection = get_connection(read_only=True)
    tables = [row[0] for row in connection.execute("SHOW TABLES").fetchall()]
    schema = []
    for table in tables:
        columns = connection.execute(f'DESCRIBE "{table}"').fetchall()
        schema.append(f"TABLE {table} (" + ", ".join(column[0] for column in columns) + ")")
    kpis = {
        "revenue": float(run_readonly_sql("SELECT COALESCE(SUM(net_sale_price),0) AS metric_value FROM sales WHERE sale_status='completed' AND COALESCE(_row_quality_status,'VALID')<>'ERROR'").iloc[0, 0]),
        "sales": float(run_readonly_sql("SELECT COUNT(*) AS metric_value FROM sales WHERE sale_status='completed' AND COALESCE(_row_quality_status,'VALID')<>'ERROR'").iloc[0, 0]),
        "branches": float(run_readonly_sql("SELECT COUNT(*) AS metric_value FROM branches WHERE branch_name IS NOT NULL").iloc[0, 0]),
        "aged": float(run_readonly_sql("SELECT COUNT(*) AS metric_value FROM inventory WHERE inventory_status='available' AND arrival_date IS NOT NULL AND date_diff('day',arrival_date,record_updated_at)>90 AND COALESCE(_row_quality_status,'VALID')<>'ERROR'").iloc[0, 0]),
    }
    return "\n".join(schema), kpis


def key() -> str:
    try:
        return str(st.secrets["GEMINI_API_KEY"])
    except Exception:
        return os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")


st.session_state.setdefault("business_messages", [])
with st.sidebar:
    if st.button("Clear chat", icon=":material/delete:", width="stretch"):
        st.session_state.business_messages = []
        st.rerun()

st.title("Ask the Business")
st.caption("Ask a question and inspect the database evidence behind the answer.")
schema, kpis = load_context()
with st.container(horizontal=True):
    st.metric("Revenue", f'GHS {kpis["revenue"] / 1_000_000_000:.2f}B', border=True)
    st.metric("Completed sales", f'{kpis["sales"]:,.0f}', border=True)
    st.metric("Branches", f'{kpis["branches"]:,.0f}', border=True)
    st.metric("Available over 90 days", f'{kpis["aged"]:,.0f}', border=True)

ask_tab, history_tab = st.tabs(["Ask", "History"])
with ask_tab:
    st.caption("Quick questions")
    quick_question = None
    with st.container(horizontal=True):
        for label, prompt in SUGGESTIONS.items():
            if st.button(label, key=f"quick_{label.lower().replace(' ', '_')}"):
                quick_question = prompt
    for message in st.session_state.business_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    submitted = st.chat_input("Ask about the business", submit_mode="disable")
    # Buttons are transient per rerun, so they cannot override later questions.
    question = submitted or quick_question
    use_reviewed_query = quick_question is not None and submitted is None
    if question:
        valid, error = validate_question(question)
        out_of_scope = handle_unanswerable(question)
        if not valid:
            st.error(error)
        elif out_of_scope:
            st.warning(out_of_scope)
        else:
            st.session_state.business_messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)
            with st.chat_message("assistant"):
                try:
                    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
                    prompt = f"Schema:\n{schema}\nQuestion: {question}\nReturn one DuckDB SELECT only. Use net_sale_price for revenue, exclude ERROR rows, and limit detail to 100 rows."
                    sql_result = (
                        {"ok": False, "text": "", "reason": "reviewed_quick_question"}
                        if use_reviewed_query
                        else generate_text(prompt, api_key=key(), model=model)
                    )
                    if sql_result["ok"]:
                        sql = sql_result["text"].replace("```sql", "").replace("```", "").strip()
                    else:
                        sql = None
                    result, mode_message, used_fallback = run_with_reviewed_fallback(
                        question, sql, run_readonly_sql
                    )
                    if result is None:
                        st.info(mode_message)
                        st.session_state.business_messages.append({"role": "assistant", "content": mode_message})
                        st.stop()
                    st.dataframe(result, hide_index=True, width="stretch")
                    evidence = build_fallback_evidence(question, result)
                    answer_prompt = f"Question: {question}\nEvidence: {result.to_json(orient='records', date_format='iso')[:12000]}\nAnswer directly and concisely. Use only numbers in evidence; do not add a FACTS heading."
                    answer_result = (
                        {"ok": False, "text": "", "reason": "deterministic_fallback"}
                        if used_fallback
                        else generate_text(answer_prompt, api_key=key(), model=model)
                    )
                    fallback_answer = fallback_response(question, evidence)
                    grounded = build_grounded_response(answer_result["text"], evidence, fallback_answer)
                    if grounded["status"] != "verified":
                        st.info("AI is temporarily unavailable. Showing the verified database result.")
                    st.markdown(grounded["response"])
                    st.session_state.business_messages.append({"role": "assistant", "content": grounded["response"]})
                except Exception:
                    safe_message = "The request could not be answered safely. Try one of the reviewed quick questions."
                    st.warning(safe_message)
                    st.session_state.business_messages.append({"role": "assistant", "content": safe_message})

with history_tab:
    if not st.session_state.business_messages:
        st.info("No questions have been asked in this session.")
    for message in st.session_state.business_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
