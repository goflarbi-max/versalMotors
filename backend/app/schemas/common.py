"""Shared API response contracts."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class Meta(BaseModel):
    filters: dict[str, Any]
    data_version: str
    generated_at: str


class Envelope(BaseModel):
    data: Any
    meta: Meta


class Problem(BaseModel):
    status: int
    message: str
    request_id: str
