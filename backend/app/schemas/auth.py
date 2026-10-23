"""Authentication request and response models."""

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str = Field(max_length=320)
    password: str = Field(max_length=1024)


class UserResponse(BaseModel):
    authenticated: bool
    email: str


class CsrfResponse(BaseModel):
    csrf_token: str
