"""Protected, grounded Ask the Business endpoints."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request

from backend.app.api.dependencies import (
    BundleDependency,
    UserDependency,
    require_api_user,
    require_mutation_security,
)
from backend.app.schemas.ask import AskRequest
from backend.app.schemas.common import Envelope, Meta
from backend.app.services import ask

router = APIRouter(
    prefix="/api/v1/ask",
    tags=["ask"],
    dependencies=[Depends(require_api_user)],
)


def _response(data, bundle: BundleDependency) -> Envelope:
    return Envelope(
        data=data,
        meta=Meta(
            filters={},
            data_version=bundle.version,
            generated_at=datetime.now(timezone.utc).isoformat(),
        ),
    )


@router.get("/summary", response_model=Envelope)
def get_summary(bundle: BundleDependency) -> Envelope:
    return _response(ask.summary(), bundle)


@router.get("/suggestions", response_model=Envelope)
def get_suggestions(bundle: BundleDependency) -> Envelope:
    return _response(
        [{"label": label, "question": question} for label, question in ask.SUGGESTIONS.items()],
        bundle,
    )


@router.post("/questions", response_model=Envelope)
def ask_question(
    payload: AskRequest,
    request: Request,
    bundle: BundleDependency,
    user: UserDependency,
) -> Envelope:
    require_mutation_security(request)
    client_ip = request.client.host if request.client else "unknown"
    allowed, retry_after = request.app.state.ask_limiter.consume(f"{client_ip}:{user.email}")
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Too many questions. Please wait before asking again.",
            headers={"Retry-After": str(retry_after)},
        )
    return _response(ask.answer_question(payload.question, bundle), bundle)
