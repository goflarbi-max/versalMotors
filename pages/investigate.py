"""Evidence-led warranty investigation page."""

from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

from src.analytics.drilldown import warranty_by_branch, warranty_by_model, warranty_claim_records
from src.analytics.metrics import AnalyticsData
from src.ui.filters import render_sidebar_filters


DATABASE_PATH = Path("data/business.duckdb")
TABLES = (
    "branches", "models", "salespeople", "inventory", "sales",
    "service_records", "warranty_claims", "complaints", "satisfaction",
)
MODEL_KEY = "warranty_drilldown_model"
BRANCH_KEY = "warranty_drilldown_branch"


@st.cache_data(show_spinner="Loading warranty evidence…")
def load_analytics_data(database_path: str, modified_at: float) -> AnalyticsData:
    del modified_at
    with duckdb.connect(database_path, read_only=True) as connection:
        frames = {table: connection.execute(f'SELECT * FROM "{table}"').fetchdf() for table in TABLES}
    return AnalyticsData(**frames)


def reset_to_models() -> None:
    st.session_state[MODEL_KEY] = None
    st.session_state[BRANCH_KEY] = None


def reset_to_branches() -> None:
    st.session_state[BRANCH_KEY] = None


st.title("Investigate warranty costs")
st.caption("Move from the management signal to the models, branches, and claims behind it.")

if not DATABASE_PATH.exists():
    st.error("The analytical database is unavailable. Run `python scripts/build_database.py` and refresh this page.")
    st.stop()

try:
    data = load_analytics_data(str(DATABASE_PATH), DATABASE_PATH.stat().st_mtime)
except (duckdb.Error, OSError) as exc:
    st.error(f"Business data could not be loaded: {exc}")
    st.stop()

filters = render_sidebar_filters(data)
st.session_state.setdefault(MODEL_KEY, None)
st.session_state.setdefault(BRANCH_KEY, None)
selected_model = st.session_state[MODEL_KEY]
selected_branch = st.session_state[BRANCH_KEY]

with st.container(horizontal=True, vertical_alignment="center"):
    st.page_link("pages/overview.py", label="Overview", icon=":material/home:")
    st.button("Warranty cost", key="crumb_metric", type="tertiary", on_click=reset_to_models)
    if selected_model:
        st.button(selected_model, key="crumb_model", type="tertiary", on_click=reset_to_branches)
    if selected_branch:
        st.markdown(f"**{selected_branch}**")

models = warranty_by_model(data, filters)
if models.empty:
    st.info("No warranty claims match the current filters. Broaden the date range or remove one or more filters.")
    st.stop()

if not selected_model or selected_model not in models["model"].tolist():
    if selected_model:
        reset_to_models()
    st.subheader("Warranty cost by model")
    st.caption("Which models account for warranty cost, and how did cost change from the prior equivalent period?")
    display_models = models.rename(columns={
        "model": "Model", "claim_count": "Claims", "claim_cost": "Claim cost",
        "previous_claim_cost": "Prior cost", "cost_change": "Cost change",
        "cost_change_rate": "Change %",
    })
    st.dataframe(
        display_models, hide_index=True, width="stretch",
        column_config={
            "Claim cost": st.column_config.NumberColumn(format="GHS %.2f"),
            "Prior cost": st.column_config.NumberColumn(format="GHS %.2f"),
            "Cost change": st.column_config.NumberColumn(format="GHS %.2f"),
            "Change %": st.column_config.NumberColumn(format="percent"),
        },
    )
    model_choice = st.selectbox("Choose a model to investigate", models["model"].tolist(), key="model_choice")
    if st.button("View branches", type="primary", icon=":material/arrow_forward:"):
        st.session_state[MODEL_KEY] = model_choice
        st.session_state[BRANCH_KEY] = None
        st.rerun()
    st.stop()

branches = warranty_by_branch(data, filters, selected_model)
if branches.empty:
    st.info("No branch-level warranty evidence remains for this model under the current filters.")
    st.stop()

if not selected_branch or selected_branch not in branches["branch"].tolist():
    if selected_branch:
        reset_to_branches()
    st.subheader(f"{selected_model}: warranty cost by branch")
    st.caption("Which branches contribute most to this model’s warranty cost?")
    display_branches = branches.rename(columns={
        "branch": "Branch", "claim_count": "Claims", "claim_cost": "Claim cost",
        "share_of_model_cost": "Share of model cost",
    })
    st.dataframe(
        display_branches, hide_index=True, width="stretch",
        column_config={
            "Claim cost": st.column_config.NumberColumn(format="GHS %.2f"),
            "Share of model cost": st.column_config.NumberColumn(format="percent"),
        },
    )
    branch_choice = st.selectbox("Choose a branch to inspect", branches["branch"].tolist(), key="branch_choice")
    if st.button("View claims", type="primary", icon=":material/arrow_forward:"):
        st.session_state[BRANCH_KEY] = branch_choice
        st.rerun()
    st.stop()

records = warranty_claim_records(data, filters, selected_model, selected_branch)
st.subheader(f"{selected_model} claims at {selected_branch}")
st.caption("Which individual claims make up this branch and model total?")
if records.empty:
    st.info("No individual claims remain under the current filters.")
    st.stop()

st.metric("Claims shown", f"{len(records):,}")
st.dataframe(
    records, hide_index=True, width="stretch",
    column_config={
        "claim_date": st.column_config.DateColumn("Claim date", format="DD MMM YYYY"),
        "claim_amount": st.column_config.NumberColumn("Claim amount", format="GHS %.2f"),
        "approved_amount": st.column_config.NumberColumn("Approved amount", format="GHS %.2f"),
        "manufacturer_recovery_amount": st.column_config.NumberColumn("Recovery amount", format="GHS %.2f"),
    },
)
st.download_button(
    "Download these claims as CSV", records.to_csv(index=False).encode("utf-8"),
    file_name=f"warranty_claims_{selected_model}_{selected_branch}.csv".replace(" ", "_"),
    mime="text/csv", icon=":material/download:",
)
