"""Read-only filter option adapter over the existing analytics bundle."""

from __future__ import annotations

import pandas as pd

from backend.app.services.data_loader import DataBundle


def _values(frame: pd.DataFrame, column: str) -> list[str]:
    if column not in frame.columns:
        return []
    values = frame[column].dropna().astype(str).str.strip()
    return sorted(values[values.ne("")].unique().tolist())


def options(bundle: DataBundle) -> dict:
    """Return the exact option lists and date defaults used by the current UI."""
    data = bundle.analytics
    sale_dates = pd.to_datetime(data.sales.get("sale_date"), errors="coerce").dropna()
    if sale_dates.empty:
        minimum = maximum = None
        default_start = None
    else:
        minimum = sale_dates.min().date()
        maximum = sale_dates.max().date()
        default_start = max(minimum, (pd.Timestamp(maximum) - pd.Timedelta(days=89)).date())

    people = data.salespeople.copy()
    if {"first_name", "last_name"}.issubset(people.columns):
        people["display_name"] = (
            people["first_name"].fillna("").astype(str).str.strip()
            + " "
            + people["last_name"].fillna("").astype(str).str.strip()
        ).str.strip()

    return {
        "date_range": {
            "minimum": minimum.isoformat() if minimum else None,
            "maximum": maximum.isoformat() if maximum else None,
            "default_start": default_start.isoformat() if default_start else None,
        },
        "branches": _values(data.branches, "branch_name"),
        "brands": _values(data.models, "manufacturer"),
        "models": _values(data.models, "model_name"),
        "salespeople": _values(people, "display_name"),
        "statuses": _values(data.sales, "sale_status"),
    }
