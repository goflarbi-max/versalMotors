"""Measure an API deployment without logging credentials or response bodies."""

from __future__ import annotations

import argparse
import json
import os
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from http.cookiejar import CookieJar
from urllib.error import HTTPError
from urllib.request import HTTPCookieProcessor, Request, build_opener, urlopen


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * fraction)))
    return ordered[index]


def timed_request(request: Request, opener=None) -> tuple[int, float, bytes]:
    started = time.perf_counter()
    handler = opener.open if opener else urlopen
    try:
        with handler(request, timeout=30) as response:
            return response.status, (time.perf_counter() - started) * 1000, response.read()
    except HTTPError as error:
        return error.code, (time.perf_counter() - started) * 1000, error.read()


def authenticated_cookie(base_url: str, email: str, password: str) -> str:
    jar = CookieJar()
    opener = build_opener(HTTPCookieProcessor(jar))
    csrf_status, _, csrf_body = timed_request(Request(f"{base_url}/api/v1/auth/csrf"), opener)
    if csrf_status != 200:
        raise RuntimeError(f"CSRF request failed with HTTP {csrf_status}")
    csrf = json.loads(csrf_body)["csrf_token"]
    payload = json.dumps({"email": email, "password": password}).encode("utf-8")
    login = Request(
        f"{base_url}/api/v1/auth/login",
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json", "Origin": base_url, "X-CSRF-Token": csrf},
    )
    login_status, _, _ = timed_request(login, opener)
    if login_status != 200:
        raise RuntimeError(f"Login failed with HTTP {login_status}")
    return "; ".join(f"{cookie.name}={cookie.value}" for cookie in jar)


def measure(base_url: str, email: str, password: str, requests: int, concurrency: int) -> dict[str, object]:
    base_url = base_url.rstrip("/")
    ready_status, ready_ms, ready_body = timed_request(Request(f"{base_url}/health/ready"))
    if ready_status != 200 or json.loads(ready_body).get("status") != "ready":
        raise RuntimeError(f"Readiness check failed with HTTP {ready_status}")
    cookie = authenticated_cookie(base_url, email, password)
    endpoint = f"{base_url}/api/v1/overview/kpis?start_date=2025-04-02&end_date=2025-06-30"

    warm_status, warm_ms, _ = timed_request(Request(endpoint, headers={"Cookie": cookie}))
    if warm_status != 200:
        raise RuntimeError(f"Overview warm-up failed with HTTP {warm_status}")

    def one_request(_: int) -> tuple[int, float]:
        status, duration, _ = timed_request(Request(endpoint, headers={"Cookie": cookie}))
        return status, duration

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        results = list(pool.map(one_request, range(requests)))
    statuses = [status for status, _ in results]
    durations = [duration for _, duration in results]
    return {
        "base_url": base_url,
        "readiness_ms": round(ready_ms, 2),
        "requests": requests,
        "concurrency": concurrency,
        "successful": sum(status == 200 for status in statuses),
        "uncached_overview_ms": round(warm_ms, 2),
        "latency_ms": {
            "minimum": round(min(durations), 2),
            "mean": round(statistics.fmean(durations), 2),
            "p50": round(percentile(durations, 0.50), 2),
            "p95": round(percentile(durations, 0.95), 2),
            "maximum": round(max(durations), 2),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--requests", type=int, default=20)
    parser.add_argument("--concurrency", type=int, default=4)
    args = parser.parse_args()
    email = os.getenv("SMOKE_EMAIL", "demo@versalmotors.com")
    password = os.getenv("SMOKE_PASSWORD")
    if not password:
        raise SystemExit("Set SMOKE_PASSWORD in the environment")
    print(json.dumps(measure(args.base_url, email, password, max(1, args.requests), max(1, args.concurrency)), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
