"""Verify the immutable deployment database against the committed parity baseline."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import duckdb


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(database: Path, baseline_path: Path) -> dict[str, object]:
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))["metadata"]
    expected_counts = baseline["table_row_counts"]

    connection = duckdb.connect(str(database), read_only=True)
    try:
        actual_counts = {
            table: connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            for table in expected_counts
        }
    finally:
        connection.close()

    mismatches = {
        table: {"expected": expected_counts[table], "actual": actual_counts[table]}
        for table in expected_counts
        if actual_counts[table] != expected_counts[table]
    }
    actual_hash = sha256(database)
    expected_hash = baseline["database_sha256"]
    if mismatches or actual_hash != expected_hash:
        details = {"row_count_mismatches": mismatches, "expected_sha256": expected_hash, "actual_sha256": actual_hash}
        raise RuntimeError(f"Deployment database does not match parity baseline: {json.dumps(details, sort_keys=True)}")

    return {"database_sha256": actual_hash, "table_row_counts": actual_counts}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.database, args.baseline)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
