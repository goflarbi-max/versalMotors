"""Framework-neutral credential validation shared by Streamlit and FastAPI."""

from __future__ import annotations

import re
from collections.abc import Mapping

import bcrypt


INVALID_CREDENTIALS_MESSAGE = "Invalid email or password"
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
DEFAULT_DEMO_USERS = {
    "demo@versalmotors.com": (
        "$2b$12$Hcb3wXrzER0BeTWmDilcQeWNL8oJMEPLYFJq1StHS7ESHlzkSDzQa"
    )
}
DUMMY_PASSWORD_HASH = b"$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6Ttxu.8N7Yfbp9S2nP5W/w9O1qC6e"


def normalize_email(value: str | None) -> str:
    return (value or "").strip().lower()


def valid_email(value: str) -> bool:
    return bool(EMAIL_RE.fullmatch(value))


def password_matches(email: str, password: str, users: Mapping[str, str]) -> bool:
    """Check bcrypt in constant work for known and unknown normalized emails."""
    configured_hash = users.get(email)
    password_hash = (configured_hash or DUMMY_PASSWORD_HASH.decode("ascii")).encode("utf-8")
    supplied = password.encode("utf-8")
    too_long = len(supplied) > 72
    candidate = supplied[:72]
    try:
        valid = bcrypt.checkpw(candidate, password_hash) and not too_long
    except ValueError:
        bcrypt.checkpw(candidate, DUMMY_PASSWORD_HASH)
        valid = False
    return configured_hash is not None and valid
