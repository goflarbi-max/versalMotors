"""Regression tests for first-start deployment database bootstrapping."""

from pathlib import Path

import duckdb

from src.database.bootstrap import REQUIRED_TABLES, database_is_ready, ensure_database


def _write_database(path: Path) -> None:
    connection = duckdb.connect(str(path))
    try:
        for table in REQUIRED_TABLES:
            connection.execute(f'CREATE TABLE "{table}" (id INTEGER)')
    finally:
        connection.close()


def test_missing_database_is_built_and_verified(tmp_path: Path) -> None:
    database_path = tmp_path / "business.duckdb"
    calls = []

    def builder() -> None:
        calls.append("build")
        _write_database(database_path)

    assert not database_is_ready(database_path)
    assert ensure_database(database_path, builder) is True
    assert calls == ["build"]
    assert database_is_ready(database_path)


def test_ready_database_does_not_rebuild(tmp_path: Path) -> None:
    database_path = tmp_path / "business.duckdb"
    _write_database(database_path)

    def unexpected_builder() -> None:
        raise AssertionError("ready database should not be rebuilt")

    assert ensure_database(database_path, unexpected_builder) is False


def test_incomplete_database_is_rejected(tmp_path: Path) -> None:
    database_path = tmp_path / "business.duckdb"
    connection = duckdb.connect(str(database_path))
    connection.execute("CREATE TABLE sales (id INTEGER)")
    connection.close()

    assert not database_is_ready(database_path)
