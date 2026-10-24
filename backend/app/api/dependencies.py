"""Validated filters and request-scoped API dependencies."""

from __future__ import annotations

from datetime import date
from typing import Annotated, Literal

from fastapi import Depends, HTTPException, Query, Request, status

from backend.app.core.security import CSRF_COOKIE, SESSION_COOKIE, Session, csrf_matches
from backend.app.services.data_loader import DataBundle
from src.analytics.metrics import Filters


def get_bundle(request: Request) -> DataBundle:
    return request.app.state.data_bundle


def require_api_user(request: Request) -> Session:
    session = request.app.state.sessions.validate(request.cookies.get(SESSION_COOKIE))
    if session is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return session


def require_mutation_security(request: Request) -> None:
    origin = (request.headers.get("origin") or "").rstrip("/")
    if origin not in request.app.state.settings.allowed_origins:
        raise HTTPException(status_code=403, detail="Request origin is not allowed")
    if not csrf_matches(request.cookies.get(CSRF_COOKIE), request.headers.get("x-csrf-token")):
        raise HTTPException(status_code=403, detail="Invalid request token")


def _limited(values: list[str] | None, name: str) -> tuple[str, ...]:
    selected = tuple(values or ())
    if len(selected) > 50:
        raise HTTPException(status_code=422, detail=f"{name} accepts at most 50 values")
    return selected


def get_filters(
    start_date: date | None = None,
    end_date: date | None = None,
    branch: Annotated[list[str] | None, Query()] = None,
    brand: Annotated[list[str] | None, Query()] = None,
    model: Annotated[list[str] | None, Query()] = None,
    salesperson: Annotated[list[str] | None, Query()] = None,
    status_values: Annotated[list[str] | None, Query(alias="status")] = None,
    period: Literal["D", "W", "M", "Q", "Y"] = "M",
) -> Filters:
    if start_date and end_date and end_date < start_date:
        raise HTTPException(status_code=422, detail="end_date must be on or after start_date")
    return Filters(
        start_date=start_date,
        end_date=end_date,
        branch=_limited(branch, "branch"),
        brand=_limited(brand, "brand"),
        model=_limited(model, "model"),
        salesperson=_limited(salesperson, "salesperson"),
        status=_limited(status_values, "status"),
        period=period,
    )


BundleDependency = Annotated[DataBundle, Depends(get_bundle)]
FilterDependency = Annotated[Filters, Depends(get_filters)]
UserDependency = Annotated[Session, Depends(require_api_user)]
