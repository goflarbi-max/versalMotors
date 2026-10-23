"""Bounded in-memory login lockout for the initial single-worker deployment."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass


@dataclass
class Attempt:
    failures: int
    locked_until: float
    touched_at: float


class LoginRateLimiter:
    def __init__(self, maximum: int = 5, window_seconds: int = 60, capacity: int = 10_000):
        self.maximum = maximum
        self.window_seconds = window_seconds
        self.capacity = capacity
        self._attempts: dict[str, Attempt] = {}
        self._lock = threading.Lock()

    def remaining(self, key: str, now: float | None = None) -> int:
        current = time.monotonic() if now is None else now
        with self._lock:
            entry = self._attempts.get(key)
            if entry is None:
                return 0
            if entry.locked_until > 0 and entry.locked_until <= current:
                self._attempts.pop(key, None)
                return 0
            if entry.locked_until <= 0:
                return 0
            return max(1, int(entry.locked_until - current + 0.999))

    def fail(self, key: str, now: float | None = None) -> int:
        current = time.monotonic() if now is None else now
        with self._lock:
            if len(self._attempts) >= self.capacity and key not in self._attempts:
                oldest = min(self._attempts, key=lambda item: self._attempts[item].touched_at)
                self._attempts.pop(oldest, None)
            entry = self._attempts.get(key, Attempt(0, 0.0, current))
            entry.failures += 1
            entry.touched_at = current
            if entry.failures >= self.maximum:
                entry.locked_until = current + self.window_seconds
            self._attempts[key] = entry
            return self.window_seconds if entry.locked_until > current else 0

    def clear(self, key: str) -> None:
        with self._lock:
            self._attempts.pop(key, None)
