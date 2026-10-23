"""Protected Overview endpoints backed by existing metric functions."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from backend.app.api.dependencies import BundleDependency, FilterDependency, require_api_user
from backend.app.schemas.common import Envelope, Meta
from backend.app.services import overview
from src.analytics.metrics import Filters

router = APIRouter(
    prefix="/api/v1/overview",
    tags=["overview"],
    dependencies=[Depends(require_api_user)],
)


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


def _response(data: list[dict], bundle: BundleDependency, filters: FilterDependency) -> Envelope:
    return Envelope(
        data=data,
        meta=Meta(
            filters=_filter_meta(filters),
            data_version=bundle.version,
            generated_at=datetime.now(timezone.utc).isoformat(),
        ),
    )


@router.get("/kpis", response_model=Envelope)
def get_kpis(bundle: BundleDependency, filters: FilterDependency) -> Envelope:
    return _response(overview.kpis(bundle, filters), bundle, filters)


@router.get("/revenue-trend", response_model=Envelope)
def get_revenue_trend(bundle: BundleDependency, filters: FilterDependency) -> Envelope:
    return _response(overview.revenue_trend(bundle, filters), bundle, filters)


@router.get("/revenue-by-branch", response_model=Envelope)
def get_revenue_by_branch(bundle: BundleDependency, filters: FilterDependency) -> Envelope:
    return _response(overview.branch_revenue(bundle, filters), bundle, filters)


@router.get("/margin-by-model", response_model=Envelope)
def get_margin_by_model(bundle: BundleDependency, filters: FilterDependency) -> Envelope:
    return _response(overview.model_margin(bundle, filters), bundle, filters)
