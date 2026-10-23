"""Regenerate the committed Phase 0 baseline from the current read-only database."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.parity_support import BASELINE_PATH, write_baseline  # noqa: E402


if __name__ == "__main__":
    baseline = write_baseline()
    print(f"Wrote {BASELINE_PATH}")
    print(f"Source commit: {baseline['metadata']['source_git_commit']}")
    print(f"Database SHA-256: {baseline['metadata']['database_sha256']}")
