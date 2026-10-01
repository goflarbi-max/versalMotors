"""Build cleaned CSVs and the local versalMotors DuckDB database."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import duckdb  # noqa: E402

from src.data.cleaning import CLEAN_DIR, LOG_PATH, TABLES, clean_all  # noqa: E402


DATABASE_PATH = ROOT / "data" / "business.duckdb"


def build_database() -> None:
    """Run cleaning and replace the managed analytical tables in DuckDB."""
    cleaned = clean_all()
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(str(DATABASE_PATH))
    try:
        for table in TABLES:
            csv_path = (CLEAN_DIR / f"{table}.csv").as_posix().replace("'", "''")
            connection.execute(
                f"CREATE OR REPLACE TABLE {table} AS "
                f"SELECT * FROM read_csv_auto('{csv_path}', header=true, sample_size=-1, all_varchar=false)"
            )
            actual = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            expected = len(cleaned[table])
            if actual != expected:
                raise RuntimeError(f"{table}: DuckDB has {actual} rows; expected {expected}")
        log_path = LOG_PATH.as_posix().replace("'", "''")
        connection.execute(
            "CREATE OR REPLACE TABLE cleaning_log AS "
            f"SELECT * FROM read_csv_auto('{log_path}', header=true, sample_size=-1)"
        )
    finally:
        connection.close()

    print(f"Built {DATABASE_PATH}")
    for table in TABLES:
        print(f"  {table}: {len(cleaned[table]):,} cleaned rows")
    print(f"Cleaning log: {LOG_PATH}")


if __name__ == "__main__":
    build_database()
