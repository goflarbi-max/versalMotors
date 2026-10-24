"""Protected Management Brief generation and exact-artifact downloads."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response

from backend.app.api.dependencies import BundleDependency, require_api_user, require_mutation_security
from backend.app.schemas.brief import BriefRequest
from backend.app.schemas.common import Envelope, Meta
from backend.app.services import management_brief

router = APIRouter(
    prefix="/api/v1/management-brief",
    tags=["management-brief"],
    dependencies=[Depends(require_api_user)],
)


@router.post("", response_model=Envelope)
def create_brief(payload: BriefRequest, request: Request, bundle: BundleDependency) -> Envelope:
    require_mutation_security(request)
    data = management_brief.generate(payload.start_date, payload.end_date, request.app.state.report_store)
    return Envelope(
        data=data,
        meta=Meta(
            filters={"start_date": payload.start_date.isoformat(), "end_date": payload.end_date.isoformat()},
            data_version=bundle.version,
            generated_at=datetime.now(timezone.utc).isoformat(),
        ),
    )


def _artifact(request: Request, report_id: str):
    artifact = request.app.state.report_store.get(report_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="Management Brief not found or expired")
    return artifact


@router.get("/{report_id}.md")
def download_markdown(report_id: str, request: Request) -> Response:
    artifact = _artifact(request, report_id)
    return Response(
        content=artifact.markdown,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="management_brief_{report_id}.md"'},
    )


@router.get("/{report_id}.pdf")
def download_pdf(report_id: str, request: Request) -> Response:
    artifact = _artifact(request, report_id)
    return Response(
        content=artifact.pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="management_brief_{report_id}.pdf"'},
    )
