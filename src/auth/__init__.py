"""Authentication access layer for the VersalMotors demo application."""

from .auth import (
    AuthenticationError,
    current_user_email,
    is_authenticated,
    login,
    logout,
    require_login,
    verify_credentials,
)

__all__ = [
    "AuthenticationError",
    "current_user_email",
    "is_authenticated",
    "login",
    "logout",
    "require_login",
    "verify_credentials",
]
