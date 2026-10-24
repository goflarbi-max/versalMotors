"""Protected Overview endpoints backed by existing metric functions."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request, Response

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


def _cached(request: Request, response: Response, bundle: BundleDependency, filters: FilterDependency, name: str, factory) -> Envelope:
    data, hit = request.app.state.response_cache.get_or_create((bundle.version, name, filters), factory)
    response.headers["X-Cache-Result"] = "hit" if hit else "miss"
    return _response(data, bundle, filters)


@router.get("/kpis", response_model=Envelope)
def get_kpis(request: Request, response: Response, bundle: BundleDependency, filters: FilterDependency) -> Envelope:
    return _cached(request, response, bundle, filters, "kpis", lambda: overview.kpis(bundle, filters))


@router.get("/revenue-trend", response_model=Envelope)
def get_revenue_trend(request: Request, response: Response, bundle: BundleDependency, filters: FilterDependency) -> Envelope:
    return _cached(request, response, bundle, filters, "revenue-trend", lambda: overview.revenue_trend(bundle, filters))


@router.get("/revenue-by-branch", response_model=Envelope)
def get_revenue_by_branch(request: Request, response: Response, bundle: BundleDependency, filters: FilterDependency) -> Envelope:
    return _cached(request, response, bundle, filters, "revenue-by-branch", lambda: overview.branch_revenue(bundle, filters))


@router.get("/margin-by-model", response_model=Envelope)
def get_margin_by_model(request: Request, response: Response, bundle: BundleDependency, filters: FilterDependency) -> Envelope:
    return _cached(request, response, bundle, filters, "margin-by-model", lambda: overview.model_margin(bundle, filters))
