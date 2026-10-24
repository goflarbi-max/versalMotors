"""Thin warranty drill-down adapters with deterministic display pagination."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd

from backend.app.services.data_loader import DataBundle
from backend.app.services.serialization import frame_records
from src.analytics.drilldown import (
    warranty_by_branch,
    warranty_by_model,
    warranty_claim_records,
)
from src.analytics.metrics import Filters
from src.ui.pdf_exports import dataframe_to_pdf

SortDirection = Literal["original", "asc", "desc"]

MODEL_COLUMNS = (
    "model",
    "claim_count",
    "claim_cost",
    "previous_claim_cost",
    "cost_change",
    "cost_change_rate",
)
BRANCH_COLUMNS = ("branch", "claim_count", "claim_cost", "share_of_model_cost")
CLAIM_COLUMNS = (
    "claim_id",
    "claim_date",
    "model",
    "branch",
    "failure_category",
    "claim_description",
    "claim_status",
    "claim_amount",
    "approved_amount",
    "manufacturer_recovery_amount",
    "sale_id",
    "service_id",
    "inventory_id",
    "_row_quality_status",
)


@dataclass(frozen=True)
class Page:
    records: list[dict]
    total: int
    page: int
    page_size: int
    sort_by: str | None
    sort_dir: SortDirection

    def as_dict(self) -> dict:
        return {
            "records": self.records,
            "total": self.total,
            "page": self.page,
            "page_size": self.page_size,
            "sort_by": self.sort_by,
            "sort_dir": self.sort_dir,
        }


def _sorted_copy(
    frame: pd.DataFrame,
    *,
    sort_by: str | None,
    sort_dir: SortDirection,
    allowed_columns: tuple[str, ...],
) -> pd.DataFrame:
    result = frame.copy(deep=True)
    if sort_dir == "original" or sort_by is None:
        return result
    if sort_by not in allowed_columns:
        raise ValueError("Unsupported sort column")
    return result.sort_values(
        sort_by,
        ascending=sort_dir == "asc",
        kind="mergesort",
        na_position="last",
        ignore_index=True,
    )


def _page(
    frame: pd.DataFrame,
    *,
    page: int,
    page_size: int,
    sort_by: str | None,
    sort_dir: SortDirection,
    allowed_columns: tuple[str, ...],
) -> Page:
    ordered = _sorted_copy(
        frame,
        sort_by=sort_by,
        sort_dir=sort_dir,
        allowed_columns=allowed_columns,
    )
    start = (page - 1) * page_size
    current = ordered.iloc[start : start + page_size]
    return Page(
        records=frame_records(current),
        total=len(ordered),
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


def model_page(
    bundle: DataBundle,
    filters: Filters,
    *,
    page: int,
    page_size: int,
    sort_by: str | None,
    sort_dir: SortDirection,
) -> Page:
    return _page(
        warranty_by_model(bundle.analytics, filters),
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_dir=sort_dir,
        allowed_columns=MODEL_COLUMNS,
    )


def branch_page(
    bundle: DataBundle,
    filters: Filters,
    model: str,
    *,
    page: int,
    page_size: int,
    sort_by: str | None,
    sort_dir: SortDirection,
) -> Page:
    return _page(
        warranty_by_branch(bundle.analytics, filters, model),
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_dir=sort_dir,
        allowed_columns=BRANCH_COLUMNS,
    )


def claim_frame(
    bundle: DataBundle,
    filters: Filters,
    model: str,
    branch: str,
    *,
    sort_by: str | None,
    sort_dir: SortDirection,
) -> pd.DataFrame:
    return _sorted_copy(
        warranty_claim_records(bundle.analytics, filters, model, branch),
        sort_by=sort_by,
        sort_dir=sort_dir,
        allowed_columns=CLAIM_COLUMNS,
    )


def claim_page(
    bundle: DataBundle,
    filters: Filters,
    model: str,
    branch: str,
    *,
    page: int,
    page_size: int,
    sort_by: str | None,
    sort_dir: SortDirection,
) -> Page:
    return _page(
        warranty_claim_records(bundle.analytics, filters, model, branch),
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_dir=sort_dir,
        allowed_columns=CLAIM_COLUMNS,
    )


def claims_csv(frame: pd.DataFrame) -> bytes:
    return frame.to_csv(index=False).encode("utf-8")


def claims_pdf(frame: pd.DataFrame, model: str, branch: str) -> bytes:
    return dataframe_to_pdf(f"Warranty claims - {model} - {branch}", frame)
