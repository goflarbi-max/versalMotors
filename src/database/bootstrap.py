"""Create and validate the generated analytical database at application startup."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import threading

import duckdb


ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = ROOT / "data" / "business.duckdb"
REQUIRED_TABLES = frozenset(
    {
        "branches",
        "models",
        "salespeople",
        "inventory",
        "sales",
        "service_records",
        "warranty_claims",
        "complaints",
        "satisfaction",
    }
)
_BUILD_LOCK = threading.Lock()


def database_is_ready(database_path: Path = DATABASE_PATH) -> bool:
    """Return whether a readable database contains every managed business table."""
    if not database_path.is_file():
        return False
    try:
        connection = duckdb.connect(str(database_path), read_only=True)
        try:
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'main'"
                ).fetchall()
            }
        finally:
            connection.close()
    except (duckdb.Error, OSError):
        return False
    return REQUIRED_TABLES.issubset(tables)


def ensure_database(
    database_path: Path = DATABASE_PATH,
    builder: Callable[[], None] | None = None,
) -> bool:
    """Build a missing/incomplete database once and verify the result.

    Returns ``True`` when this call performed the build and ``False`` when a
    valid database already existed. The lock prevents concurrent Streamlit
    sessions in one process from starting duplicate first-run builds.
    """
    if database_is_ready(database_path):
        return False

    with _BUILD_LOCK:
        if database_is_ready(database_path):
            return False
        if builder is None:
            if database_path.resolve() != DATABASE_PATH.resolve():
                raise ValueError("A custom database path requires a custom builder")
            from scripts.build_database import build_database

            builder = build_database
        builder()
        if not database_is_ready(database_path):
            raise RuntimeError("Database build completed without all required tables")
    return True
