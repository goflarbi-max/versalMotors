"""VersalMotors Phase 1 FastAPI application."""

from __future__ import annotations

import json
import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.routes import ask, auth, data_quality, filters, health, investigate, management_brief, overview
from backend.app.core.config import get_settings
from backend.app.core.cache import TTLCache
from backend.app.core.rate_limit import LoginRateLimiter
from backend.app.core.report_store import ReportStore
from backend.app.core.request_rate_limit import TokenBucketRateLimiter
from backend.app.core.security import SessionStore
from backend.app.services.data_loader import get_data_bundle


logger = logging.getLogger("versalmotors.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.settings = settings
    app.state.data_bundle = get_data_bundle()
    app.state.sessions = SessionStore(
        settings.session_secret,
        settings.session_hours * 3600,
        settings.session_idle_minutes * 60,
    )
    app.state.login_email_limiter = LoginRateLimiter(
        maximum=settings.login_max_failures,
        window_seconds=settings.login_window_seconds,
        lock_seconds=settings.login_lock_seconds,
    )
    app.state.login_ip_limiter = LoginRateLimiter(
        maximum=settings.login_ip_max_failures,
        window_seconds=settings.login_window_seconds,
        lock_seconds=settings.login_lock_seconds,
    )
    app.state.ask_limiter = TokenBucketRateLimiter(requests_per_minute=10, burst=3)
    app.state.report_store = ReportStore()
    app.state.response_cache = TTLCache(ttl_seconds=300, max_entries=256, max_concurrent_creations=4)
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
async def request_log(request: Request, call_next):
    """Emit one query-free structured access record without sensitive values."""
    started = time.perf_counter()
    status_code = 500
    response = None
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        error_category = "none" if status_code < 400 else ("client_error" if status_code < 500 else "server_error")
        record = {
            "request_id": getattr(request.state, "request_id", "pending"),
            "route": request.url.path,
            "method": request.method,
            "duration_ms": duration_ms,
            "status": status_code,
            "cache_result": response.headers.get("x-cache-result", "none") if response else "none",
            "error_category": error_category,
        }
        logger.info(json.dumps(record, separators=(",", ":"), sort_keys=True))


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
    if request.url.path.startswith(("/api/v1/auth", "/api/auth")):
        response.headers["Cache-Control"] = "no-store, max-age=0"
        response.headers["Pragma"] = "no-cache"
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
app.include_router(auth.session_router)
app.include_router(filters.router)
app.include_router(overview.router)
app.include_router(investigate.router)
app.include_router(ask.router)
app.include_router(management_brief.router)
app.include_router(data_quality.router)
