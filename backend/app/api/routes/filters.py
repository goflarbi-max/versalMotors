"""Authenticated shared-filter metadata endpoint."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from backend.app.api.dependencies import BundleDependency, require_api_user
from backend.app.schemas.common import Envelope, Meta
from backend.app.services.filter_options import options

router = APIRouter(
    prefix="/api/v1/filters",
    tags=["filters"],
    dependencies=[Depends(require_api_user)],
)


@router.get("/options", response_model=Envelope)
def get_options(bundle: BundleDependency) -> Envelope:
    return Envelope(
        data=options(bundle),
        meta=Meta(
            filters={},
            data_version=bundle.version,
            generated_at=datetime.now(timezone.utc).isoformat(),
        ),
    )
