"""Unauthenticated liveness and readiness checks."""

from fastapi import APIRouter, Request

from src.database.bootstrap import REQUIRED_TABLES, database_is_ready

router = APIRouter(tags=["health"])


@router.get("/health/live")
def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
def ready(request: Request) -> dict:
    bundle = request.app.state.data_bundle
    ready_now = database_is_ready(bundle.database_path)
    return {
        "status": "ready" if ready_now else "not_ready",
        "data_version": bundle.version,
        "required_tables": sorted(REQUIRED_TABLES),
        "row_counts": bundle.row_counts,
    }
