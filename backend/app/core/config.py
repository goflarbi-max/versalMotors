"""Environment-only configuration for the API."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

from src.auth.credentials import DEFAULT_DEMO_USERS


@dataclass(frozen=True)
class Settings:
    session_secret: str
    session_hours: int
    allowed_origins: tuple[str, ...]
    auth_users: dict[str, str]
    secure_cookies: bool


def _users_from_environment() -> dict[str, str]:
    raw = os.getenv("VERSALMOTORS_AUTH_USERS_JSON", "").strip()
    if not raw:
        return DEFAULT_DEMO_USERS.copy()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return DEFAULT_DEMO_USERS.copy()
    if not isinstance(parsed, dict):
        return DEFAULT_DEMO_USERS.copy()
    users = {
        str(email).strip().lower(): str(password_hash).strip()
        for email, password_hash in parsed.items()
        if str(email).strip() and str(password_hash).strip()
    }
    return users or DEFAULT_DEMO_USERS.copy()


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
        allowed_origins=origins,
        auth_users=_users_from_environment(),
        secure_cookies=os.getenv("VERSALMOTORS_SECURE_COOKIES", "true").lower()
        not in {"0", "false", "no"},
    )
