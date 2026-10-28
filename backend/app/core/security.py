"""Signed sessions, request-origin checks, and safe authentication primitives."""

from __future__ import annotations

import hashlib
import hmac
import logging
import secrets
import threading
import time
from dataclasses import dataclass

import httpx

from src.auth.credentials import normalize_email, password_matches, valid_email

SESSION_COOKIE = "versal_session"
CSRF_COOKIE = "versal_csrf"

_supabase_logger = logging.getLogger("versalmotors.auth.supabase")


def _verify_with_supabase(email: str, password: str, url: str, service_role_key: str) -> bool:
    """Verify credentials against Supabase Auth. Returns True only on HTTP 200."""
    try:
        response = httpx.post(
            f"{url.rstrip('/')}/auth/v1/token",
            params={"grant_type": "password"},
            headers={
                "apikey": service_role_key,
                "Content-Type": "application/json",
            },
            json={"email": email, "password": password},
            timeout=10.0,
        )
        return response.status_code == 200
    except Exception:
        _supabase_logger.warning("Supabase auth check failed (provider unreachable)")
        return False


def verify_password(
    email: str,
    password: str,
    users: dict[str, str],
    supabase_url: str | None = None,
    supabase_service_role_key: str | None = None,
) -> bool:
    """Verify credentials against bcrypt store first, then Supabase as fallback."""
    # Primary: bcrypt check against VERSALMOTORS_AUTH_USERS_JSON (demo account)
    if password_matches(email, password, users):
        return True
    # Fallback: Supabase Auth (only attempted when both env vars are set)
    if supabase_url and supabase_service_role_key:
        return _verify_with_supabase(email, password, supabase_url, supabase_service_role_key)
    return False


@dataclass(frozen=True)
class Session:
    sid: str
    email: str
    role: str
    issued_at: int
    last_seen_at: int
    absolute_expires_at: int
    idle_seconds: int


class SessionStore:
    def __init__(
        self,
        secret: str,
        lifetime_seconds: int,
        idle_seconds: int | None = None,
        capacity: int = 10_000,
    ):
        self._secret = secret.encode("utf-8")
        self._lifetime = lifetime_seconds
        self._idle = idle_seconds or lifetime_seconds
        self._capacity = capacity
        self._sessions: dict[str, Session] = {}
        self._lock = threading.Lock()

    def _sign(self, body: str) -> str:
        return hmac.new(self._secret, body.encode("ascii"), hashlib.sha256).hexdigest()

    def create(
        self,
        email: str,
        role: str = "viewer",
        now: int | None = None,
        lifetime_seconds: int | None = None,
        idle_seconds: int | None = None,
    ) -> tuple[Session, str]:
        issued = int(time.time()) if now is None else int(now)
        lifetime = lifetime_seconds or self._lifetime
        idle = idle_seconds or self._idle
        session = Session(
            sid=secrets.token_urlsafe(32),
            email=email,
            role=role,
            issued_at=issued,
            last_seen_at=issued,
            absolute_expires_at=issued + lifetime,
            idle_seconds=idle,
        )
        token = f"{session.sid}.{self._sign(session.sid)}"
        with self._lock:
            if len(self._sessions) >= self._capacity:
                oldest = min(self._sessions, key=lambda sid: self._sessions[sid].issued_at)
                self._sessions.pop(oldest, None)
            self._sessions[session.sid] = session
        return session, token

    def validate(self, token: str | None, now: int | None = None) -> Session | None:
        if not token or "." not in token:
            return None
        sid, supplied_signature = token.rsplit(".", 1)
        if not hmac.compare_digest(self._sign(sid), supplied_signature):
            return None
        current = int(time.time()) if now is None else int(now)
        with self._lock:
            session = self._sessions.get(sid)
            if session is None:
                return None
            idle_expired = session.last_seen_at + session.idle_seconds <= current
            absolute_expired = session.absolute_expires_at <= current
            if idle_expired or absolute_expired:
                self._sessions.pop(sid, None)
                return None
            refreshed = Session(
                sid=session.sid,
                email=session.email,
                role=session.role,
                issued_at=session.issued_at,
                last_seen_at=current,
                absolute_expires_at=session.absolute_expires_at,
                idle_seconds=session.idle_seconds,
            )
            self._sessions[sid] = refreshed
            return refreshed

    def revoke(self, token: str | None) -> None:
        session = self.validate(token)
        if session is not None:
            with self._lock:
                self._sessions.pop(session.sid, None)


def new_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def csrf_matches(cookie: str | None, header: str | None) -> bool:
    return bool(cookie and header and hmac.compare_digest(cookie, header))
