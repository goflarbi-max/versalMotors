"""Small bounded TTL cache for immutable API response data."""

from __future__ import annotations

import threading
import time
from collections import OrderedDict
from collections.abc import Callable
from concurrent.futures import Future
from typing import Generic, TypeVar


T = TypeVar("T")


class TTLCache(Generic[T]):
    def __init__(self, *, ttl_seconds: float, max_entries: int, max_concurrent_creations: int = 4) -> None:
        self._ttl = ttl_seconds
        self._max_entries = max_entries
        self._values: OrderedDict[object, tuple[float, T]] = OrderedDict()
        self._pending: dict[object, Future[T]] = {}
        self._lock = threading.Lock()
        self._compute_slots = threading.BoundedSemaphore(max(1, max_concurrent_creations))

    def get_or_create(self, key: object, factory: Callable[[], T]) -> tuple[T, bool]:
        now = time.monotonic()
        with self._lock:
            cached = self._values.get(key)
            if cached is not None and now - cached[0] < self._ttl:
                self._values.move_to_end(key)
                return cached[1], True
            self._values.pop(key, None)
            pending = self._pending.get(key)
            if pending is None:
                pending = Future()
                self._pending[key] = pending
                creator = True
            else:
                creator = False

        if not creator:
            return pending.result(), True

        try:
            with self._compute_slots:
                value = factory()
            with self._lock:
                self._values[key] = (time.monotonic(), value)
                self._values.move_to_end(key)
                while len(self._values) > self._max_entries:
                    self._values.popitem(last=False)
            pending.set_result(value)
            return value, False
        except BaseException as error:
            pending.set_exception(error)
            raise
        finally:
            with self._lock:
                self._pending.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._values.clear()
