"""Thin adapters that call the existing Overview metric functions unchanged."""

from __future__ import annotations

from src.analytics.metrics import (
    Filters,
    gross_margin_by_model,
    overview_kpis,
    revenue,
    revenue_by_branch,
)

from backend.app.services.data_loader import DataBundle
from backend.app.services.serialization import frame_records


def kpis(bundle: DataBundle, filters: Filters) -> list[dict]:
    return frame_records(overview_kpis(bundle.analytics, filters))


def revenue_trend(bundle: DataBundle, filters: Filters) -> list[dict]:
    return frame_records(revenue(bundle.analytics, filters))


def branch_revenue(bundle: DataBundle, filters: Filters) -> list[dict]:
    return frame_records(revenue_by_branch(bundle.analytics, filters))


def model_margin(bundle: DataBundle, filters: Filters) -> list[dict]:
    return frame_records(gross_margin_by_model(bundle.analytics, filters))
