from __future__ import annotations

from pathlib import Path

from deployment.verify_database import verify


ROOT = Path(__file__).resolve().parents[1]


def test_deployment_database_matches_frozen_baseline() -> None:
    result = verify(ROOT / "data" / "business.duckdb", ROOT / "tests" / "parity_baseline.json")
    assert result["table_row_counts"]["sales"] == 20_520
    assert result["table_row_counts"]["cleaning_log"] == 150


def test_backend_container_is_non_root_read_only_data_and_single_worker() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "FROM python:3.12-slim AS builder" in dockerfile
    assert "python scripts/build_database.py" in dockerfile
    assert "python deployment/verify_database.py" in dockerfile
    assert "USER 10001:10001" in dockerfile
    assert "--workers 1" in dockerfile
    assert "data/business.duckdb" in dockerfile


def test_railway_configuration_has_readiness_and_preserved_secrets() -> None:
    config = (ROOT / ".railway" / "railway.ts").read_text(encoding="utf-8")
    assert 'healthcheck: "/health/ready"' in config
    assert 'replicas: { "europe-west4": 1 }' in config
    assert "VERSALMOTORS_SESSION_SECRET: preserve()" in config
    assert "VERSALMOTORS_AUTH_USERS_JSON: preserve()" in config
    assert "GEMINI_API_KEY: preserve()" in config


def test_docker_context_excludes_local_secrets_and_generated_database() -> None:
    ignored = (ROOT / ".dockerignore").read_text(encoding="utf-8").splitlines()
    assert ".env" in ignored
    assert ".streamlit/secrets.toml" in ignored
    assert "data/business.duckdb" in ignored
    assert "data/generator_truth.md" in ignored


def test_frontend_uses_same_origin_proxy_and_security_headers() -> None:
    next_config = (ROOT / "frontend" / "next.config.ts").read_text(encoding="utf-8")
    assert "process.env.API_ORIGIN" in next_config
    assert 'source: "/api/:path*"' in next_config
    assert "X-Content-Type-Options" in next_config
    assert "Content-Security-Policy" in next_config
    assert "frame-ancestors 'none'" in next_config
    assert "poweredByHeader: false" in next_config
