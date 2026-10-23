"""Signed sessions, request-origin checks, and safe authentication primitives."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import threading
import time
from dataclasses import dataclass

from src.auth.credentials import normalize_email, password_matches, valid_email

SESSION_COOKIE = "versal_session"
CSRF_COOKIE = "versal_csrf"


def verify_password(email: str, password: str, users: dict[str, str]) -> bool:
    return password_matches(email, password, users)


@dataclass(frozen=True)
class Session:
    sid: str
    email: str
    issued_at: int
    expires_at: int


class SessionStore:
    def __init__(self, secret: str, lifetime_seconds: int, capacity: int = 10_000):
        self._secret = secret.encode("utf-8")
        self._lifetime = lifetime_seconds
        self._capacity = capacity
        self._sessions: dict[str, Session] = {}
        self._lock = threading.Lock()

    def _sign(self, body: str) -> str:
        return hmac.new(self._secret, body.encode("ascii"), hashlib.sha256).hexdigest()

    def create(self, email: str, now: int | None = None) -> tuple[Session, str]:
        issued = int(time.time()) if now is None else int(now)
        session = Session(secrets.token_urlsafe(24), email, issued, issued + self._lifetime)
        payload = base64.urlsafe_b64encode(json.dumps(
            {"sid": session.sid, "email": email, "iat": issued, "exp": session.expires_at},
            separators=(",", ":"),
        ).encode("utf-8")).decode("ascii").rstrip("=")
        token = f"{payload}.{self._sign(payload)}"
        with self._lock:
            if len(self._sessions) >= self._capacity:
                oldest = min(self._sessions, key=lambda sid: self._sessions[sid].issued_at)
                self._sessions.pop(oldest, None)
            self._sessions[session.sid] = session
        return session, token

    def validate(self, token: str | None, now: int | None = None) -> Session | None:
        if not token or "." not in token:
            return None
        payload, supplied_signature = token.rsplit(".", 1)
        if not hmac.compare_digest(self._sign(payload), supplied_signature):
            return None
        try:
            padded = payload + "=" * (-len(payload) % 4)
            decoded = json.loads(base64.urlsafe_b64decode(padded).decode("utf-8"))
            sid = str(decoded["sid"])
        except (KeyError, ValueError, TypeError, json.JSONDecodeError):
            return None
        current = int(time.time()) if now is None else int(now)
        with self._lock:
            session = self._sessions.get(sid)
            if session is None or session.expires_at <= current:
                self._sessions.pop(sid, None)
                return None
            return session

    def revoke(self, token: str | None) -> None:
        session = self.validate(token)
        if session is not None:
            with self._lock:
                self._sessions.pop(session.sid, None)


def new_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def csrf_matches(cookie: str | None, header: str | None) -> bool:
    return bool(cookie and header and hmac.compare_digest(cookie, header))
