"""Append-only summary log for versalMotors cleaning operations."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path


LOG_COLUMNS = ["step", "table", "rows_affected", "reason", "action_taken"]


@dataclass
class CleaningLog:
    """Collect one audit entry for every cleaning step that runs."""

    entries: list[dict[str, str | int]] = field(default_factory=list)

    def append(
        self,
        *,
        step: str,
        table: str,
        rows_affected: int,
        reason: str,
        action_taken: str,
    ) -> None:
        self.entries.append(
            {
                "step": step,
                "table": table,
                "rows_affected": int(rows_affected),
                "reason": reason,
                "action_taken": action_taken,
            }
        )

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=LOG_COLUMNS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(self.entries)
