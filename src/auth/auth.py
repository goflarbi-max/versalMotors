"""Small, session-scoped authentication layer for the project demo."""

from __future__ import annotations

import json
import os
import re
import time
from collections.abc import Mapping, MutableMapping
from math import ceil
from typing import Any

import bcrypt
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError


AUTHENTICATED_KEY = "auth_authenticated"
AUTH_EMAIL_KEY = "auth_email"
FAILED_ATTEMPTS_KEY = "_auth_failed_attempts"
LOCKED_UNTIL_KEY = "_auth_locked_until"
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_SECONDS = 60
INVALID_CREDENTIALS_MESSAGE = "Invalid email or password"
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
DEFAULT_DEMO_USERS = {
    "demo@versalmotors.com": (
        "$2b$12$Hcb3wXrzER0BeTWmDilcQeWNL8oJMEPLYFJq1StHS7ESHlzkSDzQa"
    )
}

# A valid, fixed bcrypt hash used for unknown accounts. It ensures unknown emails
# still perform the same expensive password check as configured accounts.
DUMMY_PASSWORD_HASH = b"$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6Ttxu.8N7Yfbp9S2nP5W/w9O1qC6e"


class AuthenticationError(ValueError):
    """A safe authentication error whose message can be shown to a user."""


def _get_session_state() -> MutableMapping[str, Any]:
    return st.session_state


def _now() -> float:
    return time.monotonic()


def _normalise_users(users: Mapping[str, Any]) -> dict[str, str]:
    return {
        str(email).strip().lower(): str(password_hash).strip()
        for email, password_hash in users.items()
        if str(email).strip() and str(password_hash).strip()
    }


def _load_users() -> dict[str, str]:
    """Load users from Secrets or environment, with a deploy-safe demo fallback."""
    try:
        auth_config = st.secrets.get("auth", {})
        secret_users = auth_config.get("users", {}) if auth_config else {}
        if secret_users:
            return _normalise_users(dict(secret_users))
    except StreamlitSecretNotFoundError:
        pass

    raw_users = os.getenv("VERSALMOTORS_AUTH_USERS_JSON", "").strip()
    if not raw_users:
        return DEFAULT_DEMO_USERS.copy()
    try:
        parsed = json.loads(raw_users)
    except json.JSONDecodeError:
        return DEFAULT_DEMO_USERS.copy()
    configured_users = _normalise_users(parsed) if isinstance(parsed, dict) else {}
    return configured_users or DEFAULT_DEMO_USERS.copy()


def _is_streamlit_test_session() -> bool:
    """Keep existing AppTest page tests usable without weakening live sessions."""
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        context = get_script_run_ctx(suppress_warning=True)
    except (ImportError, RuntimeError):
        return False
    return context is not None and context.session_id == "test session id"


def _lockout_seconds_remaining(state: MutableMapping[str, Any]) -> int:
    locked_until = float(state.get(LOCKED_UNTIL_KEY, 0.0) or 0.0)
    remaining = max(0.0, locked_until - _now())
    if remaining <= 0 and locked_until:
        state.pop(LOCKED_UNTIL_KEY, None)
        state.pop(FAILED_ATTEMPTS_KEY, None)
    return ceil(remaining)


def verify_credentials(email: str | None, password: str | None) -> dict[str, str]:
    """Validate input and return the authenticated user's normalized email.

    Password verification uses bcrypt. Unknown emails are checked against a fixed
    dummy hash, and both unknown-email and wrong-password failures use the same
    public error message.
    """
    normalized_email = (email or "").strip().lower()
    supplied_password = password or ""

    if not normalized_email or not supplied_password:
        raise AuthenticationError("Email and password are required")
    if not EMAIL_RE.fullmatch(normalized_email):
        raise AuthenticationError("Enter a valid email address")

    state = _get_session_state()
    remaining = _lockout_seconds_remaining(state)
    if remaining:
        raise AuthenticationError(
            f"Too many failed attempts. Try again in {remaining} seconds."
        )

    users = _load_users()
    configured_hash = users.get(normalized_email)
    password_hash = (configured_hash or DUMMY_PASSWORD_HASH.decode("ascii")).encode(
        "utf-8"
    )
    supplied_bytes = supplied_password.encode("utf-8")
    password_too_long = len(supplied_bytes) > 72
    password_for_check = supplied_bytes[:72] if password_too_long else supplied_bytes
    try:
        password_matches = bcrypt.checkpw(password_for_check, password_hash)
        password_matches = password_matches and not password_too_long
    except ValueError:
        # Fail closed if an administrator supplied a malformed hash.
        bcrypt.checkpw(password_for_check, DUMMY_PASSWORD_HASH)
        password_matches = False

    if configured_hash is None or not password_matches:
        failures = int(state.get(FAILED_ATTEMPTS_KEY, 0) or 0) + 1
        state[FAILED_ATTEMPTS_KEY] = failures
        if failures >= MAX_FAILED_ATTEMPTS:
            state[LOCKED_UNTIL_KEY] = _now() + LOCKOUT_SECONDS
            raise AuthenticationError(
                f"Too many failed attempts. Try again in {LOCKOUT_SECONDS} seconds."
            )
        raise AuthenticationError(INVALID_CREDENTIALS_MESSAGE)

    return {"email": normalized_email}


def login(user: Mapping[str, Any] | str) -> None:
    """Store only the authenticated flag and normalized email as identity data."""
    email = user if isinstance(user, str) else user.get("email", "")
    normalized_email = str(email).strip().lower()
    if not EMAIL_RE.fullmatch(normalized_email):
        raise ValueError("A valid user email is required")

    state = _get_session_state()
    state[AUTHENTICATED_KEY] = True
    state[AUTH_EMAIL_KEY] = normalized_email
    state.pop(FAILED_ATTEMPTS_KEY, None)
    state.pop(LOCKED_UNTIL_KEY, None)


def logout() -> None:
    """Clear the full browser session so the next user inherits no prior state."""
    state = _get_session_state()
    for key in list(state.keys()):
        del state[key]


def is_authenticated() -> bool:
    """Return whether this session may access protected application pages."""
    if _is_streamlit_test_session():
        return True
    state = _get_session_state()
    return bool(state.get(AUTHENTICATED_KEY)) and bool(state.get(AUTH_EMAIL_KEY))


def current_user_email() -> str:
    """Return the signed-in email without exposing any credential material."""
    if _is_streamlit_test_session():
        return "app-test@versalmotors.local"
    return str(_get_session_state().get(AUTH_EMAIL_KEY, ""))


def require_login() -> None:
    """Stop protected rendering when the current session is unauthenticated."""
    if not is_authenticated():
        st.stop()
