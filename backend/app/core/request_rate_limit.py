"""Bounded token-bucket limiter for authenticated Ask requests."""

from __future__ import annotations

import math
import threading
import time
from dataclasses import dataclass


@dataclass
class Bucket:
    tokens: float
    updated_at: float
    touched_at: float


class TokenBucketRateLimiter:
    def __init__(self, *, requests_per_minute: int = 10, burst: int = 3, capacity: int = 10_000):
        self.rate = requests_per_minute / 60.0
        self.burst = float(burst)
        self.capacity = capacity
        self._buckets: dict[str, Bucket] = {}
        self._lock = threading.Lock()

    def consume(self, key: str, now: float | None = None) -> tuple[bool, int]:
        current = time.monotonic() if now is None else now
        with self._lock:
            if len(self._buckets) >= self.capacity and key not in self._buckets:
                oldest = min(self._buckets, key=lambda item: self._buckets[item].touched_at)
                self._buckets.pop(oldest, None)
            bucket = self._buckets.get(key, Bucket(self.burst, current, current))
            elapsed = max(0.0, current - bucket.updated_at)
            bucket.tokens = min(self.burst, bucket.tokens + elapsed * self.rate)
            bucket.updated_at = current
            bucket.touched_at = current
            if bucket.tokens >= 1.0:
                bucket.tokens -= 1.0
                self._buckets[key] = bucket
                return True, 0
            self._buckets[key] = bucket
            retry_after = max(1, math.ceil((1.0 - bucket.tokens) / self.rate))
            return False, retry_after
