from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor

from backend.app.core.cache import TTLCache

from .conftest import authenticate


def test_ttl_cache_reuses_value_and_is_bounded() -> None:
    cache = TTLCache[int](ttl_seconds=60, max_entries=2)
    calls = 0

    def factory() -> int:
        nonlocal calls
        calls += 1
        return calls

    assert cache.get_or_create("a", factory) == (1, False)
    assert cache.get_or_create("a", factory) == (1, True)
    assert cache.get_or_create("b", factory) == (2, False)
    assert cache.get_or_create("c", factory) == (3, False)
    assert cache.get_or_create("a", factory) == (4, False)


def test_overview_cache_preserves_payload_and_reports_hit(api_client) -> None:
    authenticate(api_client)
    path = "/api/v1/overview/kpis?start_date=2025-04-02&end_date=2025-06-30"
    first = api_client.get(path)
    second = api_client.get(path)
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.headers["x-cache-result"] == "miss"
    assert second.headers["x-cache-result"] == "hit"
    assert first.json()["data"] == second.json()["data"]


def test_concurrent_same_key_computes_once() -> None:
    cache = TTLCache[int](ttl_seconds=60, max_entries=2)
    calls = 0
    lock = threading.Lock()

    def factory() -> int:
        nonlocal calls
        with lock:
            calls += 1
        time.sleep(0.05)
        return 42

    with ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(lambda _: cache.get_or_create("shared", factory), range(5)))

    assert calls == 1
    assert [value for value, _ in results] == [42] * 5
    assert sum(hit for _, hit in results) == 4
