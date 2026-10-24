"""Read-only Data Quality adapter preserving the frozen Streamlit check rules."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

import duckdb
import pandas as pd

from backend.app.services.data_loader import DataBundle
from backend.app.services.investigate import Page, _page, _sorted_copy
from src.ui.pdf_exports import dataframe_to_pdf

SortDirection = Literal["original", "asc", "desc"]
CHECK_COLUMNS = ("table", "issue", "count", "total_rows", "share_pct", "impact")
LOG_COLUMNS = ("step", "table", "rows_affected", "reason", "action_taken")
PRIMARY_KEYS = {
    "branches": "branch_id", "models": "model_id", "salespeople": "salesperson_id",
    "inventory": "inventory_id", "sales": "sale_id", "service_records": "service_id",
    "warranty_claims": "claim_id", "complaints": "complaint_id", "satisfaction": "survey_id",
}


@lru_cache(maxsize=2)
def _frames(database_path: str, data_version: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    del data_version
    connection = duckdb.connect(database_path, read_only=True)
    results: list[dict] = []

    def add(table: str, issue: str, count: int, total: int, impact: str) -> None:
        results.append({
            "table": table, "issue": issue, "count": int(count), "total_rows": int(total),
            "share_pct": round(count / total * 100, 2) if total else 0, "impact": impact,
        })

    try:
        tables = [row[0] for row in connection.execute("SHOW TABLES").fetchall()]
        for table in tables:
            total = connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            if not total:
                continue
            columns = [row[0] for row in connection.execute(f'DESCRIBE "{table}"').fetchall()]
            null_sql = "SELECT " + ", ".join(
                f'COUNT(*) FILTER (WHERE "{column}" IS NULL)' for column in columns
            ) + f' FROM "{table}"'
            for column, missing in zip(columns, connection.execute(null_sql).fetchone()):
                if missing:
                    add(table, f"Missing values in {column}", missing, total, f"Affects KPIs if {column} is revenue/date. Analyses filtering on {column} will undercount [EV-001].")

            primary_key = PRIMARY_KEYS.get(table.lower())
            if primary_key and primary_key in columns:
                duplicates = connection.execute(f'SELECT COUNT(*) - COUNT(DISTINCT "{primary_key}") FROM "{table}"').fetchone()[0]
                if duplicates:
                    add(table, "Duplicate primary keys", duplicates, total, "Can inflate counts and financial totals if not resolved.")

            lowered = [column.lower() for column in columns]
            if "model" in lowered:
                model_column = columns[lowered.index("model")]
                unknown = connection.execute(
                    f'SELECT COUNT(*) FROM "{table}" WHERE LOWER("{model_column}") '
                    f"IN ('unknown','unk','n/a','na','') OR \"{model_column}\" IS NULL"
                ).fetchone()[0]
                if unknown:
                    add(table, f"Unknown models in {model_column}", unknown, total, "Affects Product / Inventory conclusions. Model breakdown will be inaccurate.")

            for date_column in [column for column in columns if "date" in column.lower()]:
                try:
                    invalid = connection.execute(
                        f'SELECT COUNT(*) FROM "{table}" WHERE "{date_column}"::DATE '
                        f'> CURRENT_DATE OR "{date_column}"::DATE < \'2000-01-01\''
                    ).fetchone()[0]
                    issue = f"Invalid dates in {date_column}"
                    impact = "Affects monthly revenue trends, June drop analysis, and Management Brief period filter [EV-005]."
                except duckdb.Error:
                    invalid = connection.execute(
                        f'SELECT COUNT(*) FROM "{table}" WHERE TRY_CAST("{date_column}" AS DATE) IS NULL '
                        f'AND "{date_column}" IS NOT NULL'
                    ).fetchone()[0]
                    issue = f"Unparsable dates in {date_column}"
                    impact = "Breaks time-series. Rows excluded from period KPIs."
                if invalid:
                    add(table, issue, invalid, total, impact)

            if table.lower() == "sales" and "branches" in [name.lower() for name in tables]:
                orphans = connection.execute(
                    "SELECT COUNT(*) FROM sales s LEFT JOIN branches b ON s.branch_id=b.branch_id WHERE b.branch_id IS NULL"
                ).fetchone()[0]
                if orphans:
                    add(table, "Orphan records: branch_id not in branches", orphans, total, "Branch performance conclusions (best branch) will be incomplete [EV-004].")

        checks = pd.DataFrame(results, columns=CHECK_COLUMNS)
        cleaning_log = connection.execute("SELECT * FROM cleaning_log").fetchdf()
        return checks, cleaning_log
    finally:
        connection.close()


def frames(bundle: DataBundle) -> tuple[pd.DataFrame, pd.DataFrame]:
    checks, log = _frames(str(bundle.database_path), bundle.version)
    return checks.copy(deep=True), log.copy(deep=True)


def summary(bundle: DataBundle) -> dict:
    checks, _ = frames(bundle)
    if checks.empty:
        return {"issues_found": 0, "tables_affected": 0, "total_affected": 0, "highest_share": 0.0}
    worst = checks.sort_values("share_pct", ascending=False, kind="mergesort").iloc[0]
    return {
        "issues_found": len(checks), "tables_affected": int(checks["table"].nunique()),
        "total_affected": int(checks["count"].sum()), "highest_share": float(checks["share_pct"].max()),
        "highest_share_table": str(worst["table"]),
    }


def checks_page(bundle: DataBundle, *, page: int, page_size: int, sort_by: str | None, sort_dir: SortDirection) -> Page:
    checks, _ = frames(bundle)
    return _page(checks, page=page, page_size=page_size, sort_by=sort_by, sort_dir=sort_dir, allowed_columns=CHECK_COLUMNS)


def log_page(bundle: DataBundle, *, page: int, page_size: int, sort_by: str | None, sort_dir: SortDirection) -> Page:
    _, log = frames(bundle)
    return _page(log, page=page, page_size=page_size, sort_by=sort_by, sort_dir=sort_dir, allowed_columns=LOG_COLUMNS)


def ordered_checks(bundle: DataBundle, *, sort_by: str | None, sort_dir: SortDirection) -> pd.DataFrame:
    checks, _ = frames(bundle)
    return _sorted_copy(checks, sort_by=sort_by, sort_dir=sort_dir, allowed_columns=CHECK_COLUMNS)


def checks_csv(frame: pd.DataFrame) -> bytes:
    return frame.to_csv(index=False).encode("utf-8")


def checks_pdf(frame: pd.DataFrame) -> bytes:
    return dataframe_to_pdf("VersalMotors data quality report", frame)
