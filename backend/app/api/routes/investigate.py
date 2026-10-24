"""Protected warranty investigation, paging, sorting, and export endpoints."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Literal
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response

from backend.app.api.dependencies import BundleDependency, FilterDependency, require_api_user
from backend.app.schemas.common import Envelope, Meta
from backend.app.services import investigate
from src.analytics.metrics import Filters

router = APIRouter(
    prefix="/api/v1/investigate/warranty",
    tags=["investigate"],
    dependencies=[Depends(require_api_user)],
)

SortDirection = Literal["original", "asc", "desc"]


def _filter_meta(filters: Filters) -> dict:
    return {
        "start_date": filters.start_date.isoformat() if filters.start_date else None,
        "end_date": filters.end_date.isoformat() if filters.end_date else None,
        "branch": list(filters.branch),
        "brand": list(filters.brand),
        "model": list(filters.model),
        "salesperson": list(filters.salesperson),
        "status": list(filters.status),
        "period": filters.period,
    }


def _response(data: dict, bundle: BundleDependency, filters: FilterDependency) -> Envelope:
    return Envelope(
        data=data,
        meta=Meta(
            filters=_filter_meta(filters),
            data_version=bundle.version,
            generated_at=datetime.now(timezone.utc).isoformat(),
        ),
    )


def _sort(sort_by: str | None, sort_dir: SortDirection, allowed: tuple[str, ...]) -> None:
    if sort_dir != "original" and sort_by not in allowed:
        raise HTTPException(status_code=422, detail="sort_by is not allowed for this table")


def _page_size(value: int) -> int:
    if value not in {10, 25, 50}:
        raise HTTPException(status_code=422, detail="page_size must be 10, 25, or 50")
    return value


@router.get("/models", response_model=Envelope)
def get_models(
    bundle: BundleDependency,
    filters: FilterDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: int = 10,
    sort_by: str | None = None,
    sort_dir: SortDirection = "original",
) -> Envelope:
    _sort(sort_by, sort_dir, investigate.MODEL_COLUMNS)
    page_size = _page_size(page_size)
    result = investigate.model_page(
        bundle, filters, page=page, page_size=page_size,
        sort_by=sort_by, sort_dir=sort_dir,
    )
    return _response(result.as_dict(), bundle, filters)


@router.get("/models/{selected_model}/branches", response_model=Envelope)
def get_branches(
    selected_model: str,
    bundle: BundleDependency,
    filters: FilterDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: int = 10,
    sort_by: str | None = None,
    sort_dir: SortDirection = "original",
) -> Envelope:
    _sort(sort_by, sort_dir, investigate.BRANCH_COLUMNS)
    page_size = _page_size(page_size)
    result = investigate.branch_page(
        bundle, filters, selected_model, page=page, page_size=page_size,
        sort_by=sort_by, sort_dir=sort_dir,
    )
    return _response(result.as_dict(), bundle, filters)


@router.get("/models/{selected_model}/branches/{selected_branch}/claims", response_model=Envelope)
def get_claims(
    selected_model: str,
    selected_branch: str,
    bundle: BundleDependency,
    filters: FilterDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: int = 10,
    sort_by: str | None = None,
    sort_dir: SortDirection = "original",
) -> Envelope:
    _sort(sort_by, sort_dir, investigate.CLAIM_COLUMNS)
    page_size = _page_size(page_size)
    result = investigate.claim_page(
        bundle, filters, selected_model, selected_branch, page=page, page_size=page_size,
        sort_by=sort_by, sort_dir=sort_dir,
    )
    return _response(result.as_dict(), bundle, filters)


@router.get("/models/{selected_model}/branches/{selected_branch}/claims.csv")
def export_claims_csv(
    selected_model: str,
    selected_branch: str,
    bundle: BundleDependency,
    filters: FilterDependency,
    sort_by: str | None = None,
    sort_dir: SortDirection = "original",
) -> Response:
    _sort(sort_by, sort_dir, investigate.CLAIM_COLUMNS)
    frame = investigate.claim_frame(
        bundle, filters, selected_model, selected_branch, sort_by=sort_by, sort_dir=sort_dir,
    )
    filename = quote(f"warranty_claims_{selected_model}_{selected_branch}.csv")
    return Response(
        content=investigate.claims_csv(frame),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )


@router.get("/models/{selected_model}/branches/{selected_branch}/claims.pdf")
def export_claims_pdf(
    selected_model: str,
    selected_branch: str,
    bundle: BundleDependency,
    filters: FilterDependency,
    sort_by: str | None = None,
    sort_dir: SortDirection = "original",
) -> Response:
    _sort(sort_by, sort_dir, investigate.CLAIM_COLUMNS)
    frame = investigate.claim_frame(
        bundle, filters, selected_model, selected_branch, sort_by=sort_by, sort_dir=sort_dir,
    )
    filename = quote(f"warranty_claims_{selected_model}_{selected_branch}.pdf")
    return Response(
        content=investigate.claims_pdf(frame, selected_model, selected_branch),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )
