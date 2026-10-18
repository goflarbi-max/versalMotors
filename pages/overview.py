"""Management Overview page."""

from pathlib import Path

import duckdb
import pandas as pd
from src.database.connection import get_connection
import streamlit as st

from src.analytics.metrics import (
    AnalyticsData, gross_margin_by_model, overview_kpis, revenue, revenue_by_branch,
)
from src.ui.charts import overview_chart
from src.ui.components import kpi_card, overview_chart_header
from src.ui.filters import render_sidebar_filters
from src.ui.theme import apply_overview_theme


DATABASE_PATH = Path("data/business.duckdb")
TABLES = (
    "branches", "models", "salespeople", "inventory", "sales",
    "service_records", "warranty_claims", "complaints", "satisfaction",
)


@st.cache_data(show_spinner="Loading business data…")
def load_analytics_data(database_path: str, modified_at: float) -> AnalyticsData:
    """Load cleaned tables; the modification time invalidates stale cache data."""
    del modified_at
    connection = get_connection(read_only=True)
    frames = {table: connection.execute(f'SELECT * FROM "{table}"').fetchdf() for table in TABLES}
    return AnalyticsData(**frames)


def money(value: float) -> str:
    return f"GHS {value:,.0f}"


def metric_delta(row: pd.Series) -> str | None:
    return None if pd.isna(row["change_rate"]) else f'{row["change_rate"]:+.1%} vs prior period'


def percentage(value: float) -> str:
    return "—" if pd.isna(value) else f"{value:.1%}"


st.title("Business overview")
st.caption("A management view of sales scale, profitability, discounting, and where performance comes from.")
apply_overview_theme()

if not DATABASE_PATH.exists():
    st.error("The analytical database is unavailable. Run `python scripts/build_database.py` and refresh this page.")
    st.stop()

try:
    data = load_analytics_data(str(DATABASE_PATH), DATABASE_PATH.stat().st_mtime)
except (duckdb.Error, OSError) as exc:
    st.error(f"Business data could not be loaded: {exc}")
    st.stop()

filters = render_sidebar_filters(data)
kpis = overview_kpis(data, filters).set_index("metric")
if kpis.empty or kpis["value"].fillna(0).eq(0).all():
    st.info("No qualifying records match these filters. Broaden the date range or remove one or more filters.")
    st.stop()

metric_cards = (
    ("Revenue", money, "How much sales value did the selected period generate?", "payments"),
    ("Gross margin", money, "How much value remained after vehicle acquisition cost?", "account_balance_wallet"),
    ("Units sold", lambda value: f"{value:,.0f}", "How many distinct vehicles were sold?", "directions_car"),
    ("Discount rate", percentage, "How much of gross price was given up through discounts?", "percent"),
)

for card_pair in (metric_cards[:2], metric_cards[2:]):
    columns = st.columns(2, gap="large")
    for column, (label, formatter, question, icon) in zip(columns, card_pair, strict=True):
        row = kpis.loc[label]
        with column:
            card_key = f"overview_kpi_{label.lower().replace(' ', '_')}"
            with st.container(key=card_key):
                kpi_card(
                    label,
                    formatter(row["value"]),
                    metric_delta(row),
                    question,
                    icon,
                )

trend = revenue(data, filters)
branches = revenue_by_branch(data, filters)
models = gross_margin_by_model(data, filters)

with st.container(key="overview_chart_outer_revenue_trend"):
    with st.container(key="overview_chart_inner_revenue_trend"):
        overview_chart_header(
            "Performance trend",
            "Revenue trend",
            "Is sales revenue rising, falling, or showing seasonal movement over time?",
            "show_chart",
        )
        if trend.empty:
            st.info("No revenue trend is available for the selected filters.")
        else:
            st.plotly_chart(
                overview_chart(
                    trend,
                    chart_type="line",
                    x="period",
                    y="revenue",
                    y_label="Revenue (GHS)",
                    x_label="Month",
                    series_name="Revenue",
                ),
                use_container_width=True,
                theme=None,
                config={"displayModeBar": False, "responsive": True},
            )

with st.container(key="overview_chart_outer_revenue_branch"):
    with st.container(key="overview_chart_inner_revenue_branch"):
        overview_chart_header(
            "Branch performance",
            "Revenue by branch",
            "Which locations contribute most to sales revenue?",
            "location_on",
        )
        if branches.empty:
            st.info("No branch revenue is available for the selected filters.")
        else:
            st.plotly_chart(
                overview_chart(
                    branches,
                    chart_type="horizontal_bar",
                    x="branch",
                    y="revenue",
                    y_label="Revenue (GHS)",
                    x_label="Branch",
                    series_name="Revenue",
                ),
                use_container_width=True,
                theme=None,
                config={"displayModeBar": False, "responsive": True},
            )

with st.container(key="overview_chart_outer_margin_model"):
    with st.container(key="overview_chart_inner_margin_model"):
        overview_chart_header(
            "Model performance",
            "Gross margin by model",
            "Which vehicle models contribute the most gross margin after acquisition cost?",
            "directions_car",
        )
        if models.empty:
            st.info("No model margin is available for the selected filters.")
        else:
            st.plotly_chart(
                overview_chart(
                    models,
                    chart_type="horizontal_bar",
                    x="model",
                    y="gross_margin",
                    y_label="Gross margin (GHS)",
                    x_label="Model",
                    series_name="Gross margin",
                ),
                use_container_width=True,
                theme=None,
                config={"displayModeBar": False, "responsive": True},
            )

with st.container(border=True):
    st.subheader("Investigate the evidence")
    st.caption("Which models, branches, and individual claims are driving warranty cost?")
    st.page_link(
        "pages/investigate.py", label="Investigate warranty costs",
        icon=":material/troubleshoot:",
    )
