"""Load the existing analytical tables once, read-only, for API adapters."""

from __future__ import annotations

import hashlib
import threading
from dataclasses import dataclass
from pathlib import Path

import duckdb
import pandas as pd

from src.analytics.metrics import AnalyticsData
from src.database.bootstrap import DATABASE_PATH, REQUIRED_TABLES, database_is_ready


@dataclass(frozen=True)
class DataBundle:
    analytics: AnalyticsData
    version: str
    database_path: Path
    row_counts: dict[str, int]


_bundle: DataBundle | None = None
_lock = threading.Lock()


def database_hash(path: Path = DATABASE_PATH) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_data(path: Path = DATABASE_PATH) -> DataBundle:
    if not database_is_ready(path):
        raise RuntimeError("The analytical database is unavailable or incomplete")
    connection = duckdb.connect(str(path), read_only=True)
    try:
        frames: dict[str, pd.DataFrame] = {
            table: connection.execute(f'SELECT * FROM "{table}"').fetchdf()
            for table in sorted(REQUIRED_TABLES)
        }
    finally:
        connection.close()
    analytics = AnalyticsData(**{name: frames[name] for name in AnalyticsData.__dataclass_fields__})
    return DataBundle(
        analytics=analytics,
        version=database_hash(path),
        database_path=path,
        row_counts={name: len(frame) for name, frame in frames.items()},
    )


def get_data_bundle(*, force_reload: bool = False) -> DataBundle:
    global _bundle
    if _bundle is not None and not force_reload:
        return _bundle
    with _lock:
        if _bundle is None or force_reload:
            _bundle = load_data()
    return _bundle


def clear_data_bundle() -> None:
    global _bundle
    with _lock:
        _bundle = None
