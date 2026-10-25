"""Authentication request and response models."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class UserResponse(BaseModel):
    authenticated: bool
    email: str


class CurrentUserResponse(UserResponse):
    role: Literal["viewer", "admin"]


class CsrfResponse(BaseModel):
    csrf_token: str
