"""Environment-only configuration for the API."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Literal

from src.auth.credentials import DEFAULT_DEMO_USERS


@dataclass(frozen=True)
class AuthUser:
    password_hash: str
    role: Literal["viewer", "admin"] = "viewer"


@dataclass(frozen=True)
class Settings:
    session_secret: str
    session_hours: int
    session_idle_minutes: int
    allowed_origins: tuple[str, ...]
    auth_users: dict[str, AuthUser]
    secure_cookies: bool
    login_max_failures: int
    login_window_seconds: int
    login_lock_seconds: int
    login_failure_delay_ms: int

    @property
    def password_hashes(self) -> dict[str, str]:
        return {email: user.password_hash for email, user in self.auth_users.items()}


def _users_from_environment() -> dict[str, AuthUser]:
    raw = os.getenv("VERSALMOTORS_AUTH_USERS_JSON", "").strip()
    if not raw:
        return {
            email: AuthUser(password_hash=password_hash, role="viewer")
            for email, password_hash in DEFAULT_DEMO_USERS.items()
        }
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {
            email: AuthUser(password_hash=password_hash, role="viewer")
            for email, password_hash in DEFAULT_DEMO_USERS.items()
        }
    if not isinstance(parsed, dict):
        return {
            email: AuthUser(password_hash=password_hash, role="viewer")
            for email, password_hash in DEFAULT_DEMO_USERS.items()
        }
    users: dict[str, AuthUser] = {}
    for raw_email, raw_user in parsed.items():
        email = str(raw_email).strip().lower()
        if not email:
            continue
        if isinstance(raw_user, str):
            password_hash = raw_user.strip()
            role = "viewer"
        elif isinstance(raw_user, dict):
            password_hash = str(raw_user.get("password_hash", "")).strip()
            role = str(raw_user.get("role", "viewer")).strip().lower()
        else:
            continue
        if password_hash and role in {"viewer", "admin"}:
            users[email] = AuthUser(password_hash=password_hash, role=role)  # type: ignore[arg-type]
    if users:
        return users
    return {
        email: AuthUser(password_hash=password_hash, role="viewer")
        for email, password_hash in DEFAULT_DEMO_USERS.items()
    }


def get_settings() -> Settings:
    origins = tuple(
        origin.strip().rstrip("/")
        for origin in os.getenv(
            "VERSALMOTORS_ALLOWED_ORIGINS",
            "http://localhost:3000,https://autobusiness.goflarbi.com",
        ).split(",")
        if origin.strip()
    )
    return Settings(
        session_secret=os.getenv("VERSALMOTORS_SESSION_SECRET", "development-only-change-me"),
        session_hours=max(1, int(os.getenv("VERSALMOTORS_SESSION_HOURS", "8"))),
        session_idle_minutes=max(1, int(os.getenv("VERSALMOTORS_SESSION_IDLE_MINUTES", "30"))),
        allowed_origins=origins,
        auth_users=_users_from_environment(),
        secure_cookies=os.getenv("VERSALMOTORS_SECURE_COOKIES", "true").lower()
        not in {"0", "false", "no"},
        login_max_failures=max(1, int(os.getenv("VERSALMOTORS_LOGIN_MAX_FAILURES", "5"))),
        login_window_seconds=max(60, int(os.getenv("VERSALMOTORS_LOGIN_WINDOW_SECONDS", "900"))),
        login_lock_seconds=max(60, int(os.getenv("VERSALMOTORS_LOGIN_LOCK_SECONDS", "60"))),
        login_failure_delay_ms=max(0, min(2_000, int(os.getenv("VERSALMOTORS_LOGIN_FAILURE_DELAY_MS", "250")))),
    )
