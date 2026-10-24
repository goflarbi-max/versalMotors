"""Protected Data Quality summary, tables, and complete exports."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response

from backend.app.api.dependencies import BundleDependency, require_api_user
from backend.app.schemas.common import Envelope, Meta
from backend.app.services import data_quality

router = APIRouter(prefix="/api/v1/data-quality", tags=["data-quality"], dependencies=[Depends(require_api_user)])
SortDirection = Literal["original", "asc", "desc"]


def _response(data: dict, bundle: BundleDependency) -> Envelope:
    return Envelope(data=data, meta=Meta(filters={}, data_version=bundle.version, generated_at=datetime.now(timezone.utc).isoformat()))


def _validate(page_size: int, sort_by: str | None, sort_dir: SortDirection, allowed: tuple[str, ...]) -> None:
    if page_size not in {10, 25, 50}:
        raise HTTPException(status_code=422, detail="page_size must be 10, 25, or 50")
    if sort_dir != "original" and sort_by not in allowed:
        raise HTTPException(status_code=422, detail="sort_by is not allowed for this table")


@router.get("/summary", response_model=Envelope)
def get_summary(bundle: BundleDependency) -> Envelope:
    return _response(data_quality.summary(bundle), bundle)


@router.get("/checks", response_model=Envelope)
def get_checks(bundle: BundleDependency, page: Annotated[int, Query(ge=1)] = 1, page_size: int = 10, sort_by: str | None = None, sort_dir: SortDirection = "original") -> Envelope:
    _validate(page_size, sort_by, sort_dir, data_quality.CHECK_COLUMNS)
    result = data_quality.checks_page(bundle, page=page, page_size=page_size, sort_by=sort_by, sort_dir=sort_dir)
    return _response(result.as_dict(), bundle)


@router.get("/cleaning-log", response_model=Envelope)
def get_cleaning_log(bundle: BundleDependency, page: Annotated[int, Query(ge=1)] = 1, page_size: int = 10, sort_by: str | None = None, sort_dir: SortDirection = "original") -> Envelope:
    _validate(page_size, sort_by, sort_dir, data_quality.LOG_COLUMNS)
    result = data_quality.log_page(bundle, page=page, page_size=page_size, sort_by=sort_by, sort_dir=sort_dir)
    payload = result.as_dict()
    payload["available"] = result.total > 0
    return _response(payload, bundle)


@router.get("/checks.csv")
def export_checks_csv(bundle: BundleDependency, sort_by: str | None = None, sort_dir: SortDirection = "original") -> Response:
    _validate(10, sort_by, sort_dir, data_quality.CHECK_COLUMNS)
    frame = data_quality.ordered_checks(bundle, sort_by=sort_by, sort_dir=sort_dir)
    return Response(content=data_quality.checks_csv(frame), media_type="text/csv; charset=utf-8", headers={"Content-Disposition": 'attachment; filename="data_quality_report.csv"'})


@router.get("/checks.pdf")
def export_checks_pdf(bundle: BundleDependency, sort_by: str | None = None, sort_dir: SortDirection = "original") -> Response:
    _validate(10, sort_by, sort_dir, data_quality.CHECK_COLUMNS)
    frame = data_quality.ordered_checks(bundle, sort_by=sort_by, sort_dir=sort_dir)
    return Response(content=data_quality.checks_pdf(frame), media_type="application/pdf", headers={"Content-Disposition": 'attachment; filename="data_quality_report.pdf"'})
