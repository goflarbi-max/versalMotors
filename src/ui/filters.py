"""Persistent application-wide Streamlit filters."""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from src.analytics.metrics import AnalyticsData, Filters


_KEY_PREFIX = "global_filter_"


def _options(frame: pd.DataFrame, column: str) -> list[str]:
    if column not in frame.columns:
        return []
    values = frame[column].dropna().astype(str).str.strip()
    return sorted(values[values.ne("")].unique().tolist())


def render_sidebar_filters(data: AnalyticsData) -> Filters:
    """Render persistent global controls and return immutable exact filters."""
    sale_dates = pd.to_datetime(data.sales.get("sale_date"), errors="coerce").dropna()
    today = date.today()
    minimum = sale_dates.min().date() if not sale_dates.empty else today
    maximum = sale_dates.max().date() if not sale_dates.empty else today
    default_start = max(minimum, (pd.Timestamp(maximum) - pd.Timedelta(days=89)).date())

    people = data.salespeople.copy()
    if {"first_name", "last_name"}.issubset(people.columns):
        people["display_name"] = (
            people["first_name"].fillna("").astype(str).str.strip() + " "
            + people["last_name"].fillna("").astype(str).str.strip()
        ).str.strip()

    with st.sidebar:
        st.header("Business filters")
        st.caption("Selections persist as you move between pages.")
        selected_dates = st.date_input(
            "Date range", value=(default_start, maximum), min_value=minimum,
            max_value=maximum, key=f"{_KEY_PREFIX}dates",
        )
        branch = st.multiselect("Branch", _options(data.branches, "branch_name"), key=f"{_KEY_PREFIX}branch")
        brand = st.multiselect("Brand", _options(data.models, "manufacturer"), key=f"{_KEY_PREFIX}brand")
        model = st.multiselect("Model", _options(data.models, "model_name"), key=f"{_KEY_PREFIX}model")
        salesperson = st.multiselect("Salesperson", _options(people, "display_name"), key=f"{_KEY_PREFIX}salesperson")
        status = st.multiselect("Sale status", _options(data.sales, "sale_status"), key=f"{_KEY_PREFIX}status")

    if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
    elif isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 1:
        start_date = end_date = selected_dates[0]
    else:
        start_date = end_date = selected_dates
    return Filters(
        start_date=start_date, end_date=end_date, branch=tuple(branch), brand=tuple(brand),
        model=tuple(model), salesperson=tuple(salesperson), status=tuple(status), period="M",
    )
