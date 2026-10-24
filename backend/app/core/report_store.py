"""Small expiring store for exact generated Management Brief artifacts."""

from __future__ import annotations

import secrets
import threading
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class ReportArtifact:
    markdown: bytes
    pdf: bytes
    created_at: float


class ReportStore:
    def __init__(self, ttl_seconds: int = 3600, capacity: int = 200):
        self.ttl_seconds = ttl_seconds
        self.capacity = capacity
        self._reports: dict[str, ReportArtifact] = {}
        self._lock = threading.Lock()

    def create(self, markdown: bytes, pdf: bytes, now: float | None = None) -> str:
        current = time.monotonic() if now is None else now
        report_id = secrets.token_urlsafe(18)
        with self._lock:
            self._purge(current)
            if len(self._reports) >= self.capacity:
                oldest = min(self._reports, key=lambda key: self._reports[key].created_at)
                self._reports.pop(oldest, None)
            self._reports[report_id] = ReportArtifact(markdown, pdf, current)
        return report_id

    def get(self, report_id: str, now: float | None = None) -> ReportArtifact | None:
        current = time.monotonic() if now is None else now
        with self._lock:
            self._purge(current)
            return self._reports.get(report_id)

    def _purge(self, now: float) -> None:
        expired = [
            key for key, artifact in self._reports.items()
            if now - artifact.created_at >= self.ttl_seconds
        ]
        for key in expired:
            self._reports.pop(key, None)
