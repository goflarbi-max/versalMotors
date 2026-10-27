"""Cookie authentication endpoints with CSRF and session-scoped lockout."""

from __future__ import annotations

import json
import logging
import time

from fastapi import APIRouter, HTTPException, Request, Response, status

from backend.app.api.dependencies import UserDependency
from backend.app.core.security import (
    CSRF_COOKIE,
    SESSION_COOKIE,
    csrf_matches,
    new_csrf_token,
    normalize_email,
    valid_email,
    verify_password,
)
from backend.app.schemas.auth import CsrfResponse, CurrentUserResponse, LoginRequest, UserResponse

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])
session_router = APIRouter(prefix="/api/auth", tags=["authentication"])
auth_logger = logging.getLogger("versalmotors.auth")


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "").split(",", 1)[0].strip()
    return forwarded or (request.client.host if request.client else "unknown")


def _masked_email(email: str) -> str:
    local, separator, domain = email.partition("@")
    if not separator:
        return "***"
    visible = local[:1]
    return f"{visible}{'*' * max(3, len(local) - 1)}@{domain}"


def _log_auth_event(event: str, request: Request, email: str) -> None:
    auth_logger.info(json.dumps({
        "event": event,
        "ip": _client_ip(request),
        "masked_email": _masked_email(email),
        "request_id": getattr(request.state, "request_id", "unknown"),
    }, separators=(",", ":"), sort_keys=True))


def _require_origin(request: Request) -> None:
    origin = (request.headers.get("origin") or "").rstrip("/")
    if origin not in request.app.state.settings.allowed_origins:
        raise HTTPException(status_code=403, detail="Request origin is not allowed")


def _require_csrf(request: Request) -> None:
    if not csrf_matches(request.cookies.get(CSRF_COOKIE), request.headers.get("x-csrf-token")):
        raise HTTPException(status_code=403, detail="Invalid request token")


@router.get("/csrf", response_model=CsrfResponse)
def csrf(request: Request, response: Response) -> CsrfResponse:
    token = new_csrf_token()
    response.set_cookie(
        CSRF_COOKIE,
        token,
        httponly=False,
        secure=request.app.state.settings.secure_cookies,
        samesite="lax",
        path="/",
        max_age=3600,
    )
    return CsrfResponse(csrf_token=token)


@router.post("/login", response_model=UserResponse)
def login(payload: LoginRequest, request: Request, response: Response) -> UserResponse:
    _require_origin(request)
    _require_csrf(request)
    email = normalize_email(payload.email)
    if not email or not payload.password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    if not valid_email(email):
        raise HTTPException(status_code=400, detail="Enter a valid email address")
    client_ip = _client_ip(request)
    ip_key = f"ip:{client_ip}"
    email_key = f"email:{email}"
    remaining = max(
        request.app.state.login_ip_limiter.remaining(ip_key),
        request.app.state.login_email_limiter.remaining(email_key),
    )
    if remaining:
        _log_auth_event("login_lockout", request, email)
        raise HTTPException(
            status_code=429,
            detail=f"Too many failed attempts. Try again in {remaining} seconds.",
            headers={"Retry-After": str(remaining)},
        )
    if not verify_password(email, payload.password, request.app.state.settings.password_hashes):
        delay = request.app.state.settings.login_failure_delay_ms / 1000
        if delay:
            time.sleep(delay)
        lock_seconds = max(
            request.app.state.login_ip_limiter.fail(ip_key),
            request.app.state.login_email_limiter.fail(email_key),
        )
        if lock_seconds:
            _log_auth_event("login_lockout", request, email)
            raise HTTPException(
                status_code=429,
                detail=f"Too many failed attempts. Try again in {lock_seconds} seconds.",
                headers={"Retry-After": str(lock_seconds)},
            )
        _log_auth_event("login_failure", request, email)
        raise HTTPException(status_code=401, detail="Invalid email or password")
    request.app.state.login_email_limiter.clear(email_key)
    request.app.state.sessions.revoke(request.cookies.get(SESSION_COOKIE))
    account = request.app.state.settings.auth_users[email]
    remembered_seconds = request.app.state.settings.remember_days * 24 * 3600
    lifetime_seconds = remembered_seconds if payload.remember_me else request.app.state.settings.session_hours * 3600
    idle_seconds = remembered_seconds if payload.remember_me else request.app.state.settings.session_idle_minutes * 60
    _, token = request.app.state.sessions.create(
        email,
        account.role,
        lifetime_seconds=lifetime_seconds,
        idle_seconds=idle_seconds,
    )
    response.set_cookie(
        SESSION_COOKIE,
        token,
        httponly=True,
        secure=request.app.state.settings.secure_cookies,
        samesite="lax",
        path="/",
        max_age=remembered_seconds if payload.remember_me else None,
    )
    _log_auth_event("login_success", request, email)
    return UserResponse(authenticated=True, email=email)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response, user: UserDependency) -> None:
    _require_origin(request)
    _require_csrf(request)
    request.app.state.sessions.revoke(request.cookies.get(SESSION_COOKIE))
    response.delete_cookie(SESSION_COOKIE, path="/", secure=request.app.state.settings.secure_cookies, samesite="lax")
    response.delete_cookie(CSRF_COOKIE, path="/", secure=request.app.state.settings.secure_cookies, samesite="lax")
    _log_auth_event("logout", request, user.email)


@router.get("/me", response_model=UserResponse)
def me(user: UserDependency) -> UserResponse:
    return UserResponse(authenticated=True, email=user.email)


@session_router.get("/me", response_model=CurrentUserResponse)
def role_aware_me_alias(user: UserDependency) -> CurrentUserResponse:
    return CurrentUserResponse(authenticated=True, email=user.email, role=user.role)
