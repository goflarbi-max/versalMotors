"""Cookie authentication endpoints with CSRF and session-scoped lockout."""

from __future__ import annotations

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
from backend.app.schemas.auth import CsrfResponse, LoginRequest, UserResponse

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


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
    client_ip = request.client.host if request.client else "unknown"
    limiter_key = f"{client_ip}:{email}"
    remaining = request.app.state.login_limiter.remaining(limiter_key)
    if remaining:
        raise HTTPException(
            status_code=429,
            detail=f"Too many failed attempts. Try again in {remaining} seconds.",
            headers={"Retry-After": str(remaining)},
        )
    if not verify_password(email, payload.password, request.app.state.settings.auth_users):
        lock_seconds = request.app.state.login_limiter.fail(limiter_key)
        if lock_seconds:
            raise HTTPException(
                status_code=429,
                detail=f"Too many failed attempts. Try again in {lock_seconds} seconds.",
                headers={"Retry-After": str(lock_seconds)},
            )
        raise HTTPException(status_code=401, detail="Invalid email or password")
    request.app.state.login_limiter.clear(limiter_key)
    _, token = request.app.state.sessions.create(email)
    response.set_cookie(
        SESSION_COOKIE,
        token,
        httponly=True,
        secure=request.app.state.settings.secure_cookies,
        samesite="lax",
        path="/",
        max_age=request.app.state.settings.session_hours * 3600,
    )
    return UserResponse(authenticated=True, email=email)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response, user: UserDependency) -> None:
    del user
    _require_origin(request)
    _require_csrf(request)
    request.app.state.sessions.revoke(request.cookies.get(SESSION_COOKIE))
    response.delete_cookie(SESSION_COOKIE, path="/", secure=request.app.state.settings.secure_cookies, samesite="lax")


@router.get("/me", response_model=UserResponse)
def me(user: UserDependency) -> UserResponse:
    return UserResponse(authenticated=True, email=user.email)
