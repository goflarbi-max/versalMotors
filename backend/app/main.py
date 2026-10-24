"""VersalMotors Phase 1 FastAPI application."""

from __future__ import annotations

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.routes import ask, auth, data_quality, filters, health, investigate, management_brief, overview
from backend.app.core.config import get_settings
from backend.app.core.rate_limit import LoginRateLimiter
from backend.app.core.report_store import ReportStore
from backend.app.core.request_rate_limit import TokenBucketRateLimiter
from backend.app.core.security import SessionStore
from backend.app.services.data_loader import get_data_bundle


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.settings = settings
    app.state.data_bundle = get_data_bundle()
    app.state.sessions = SessionStore(settings.session_secret, settings.session_hours * 3600)
    app.state.login_limiter = LoginRateLimiter()
    app.state.ask_limiter = TokenBucketRateLimiter(requests_per_minute=10, burst=3)
    app.state.report_store = ReportStore()
    yield


app = FastAPI(
    title="VersalMotors Business Intelligence API",
    version="1.0.0-phase1",
    description="Authenticated read-only API over the existing VersalMotors business layer.",
    lifespan=lifespan,
)
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-CSRF-Token", "X-Request-ID"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


def _problem(request: Request, status_code: int, message: str, headers: dict | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "status": status_code,
            "message": message,
            "request_id": getattr(request.state, "request_id", "unknown"),
        },
        headers=headers,
    )


@app.exception_handler(HTTPException)
async def http_problem(request: Request, error: HTTPException):
    return _problem(request, error.status_code, str(error.detail), error.headers)


@app.exception_handler(RequestValidationError)
async def validation_problem(request: Request, error: RequestValidationError):
    del error
    return _problem(request, 422, "The request parameters are invalid")


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(filters.router)
app.include_router(overview.router)
app.include_router(investigate.router)
app.include_router(ask.router)
app.include_router(management_brief.router)
app.include_router(data_quality.router)
