"""Deterministic Phase 0 parity capture for the current production behavior.

This module intentionally lives under ``tests``. It does not become a second
business-logic implementation; it captures the current public Python outputs and
independently verifies their numbers with read-only DuckDB SQL.
"""

from __future__ import annotations

from dataclasses import asdict, replace
from datetime import date, datetime
from decimal import Decimal
from hashlib import sha256
from importlib.metadata import PackageNotFoundError, version
import json
import math
from pathlib import Path
import subprocess
import sys
from typing import Any, Iterable

import duckdb
import numpy as np
import pandas as pd

from src.ai.brief import build_evidence, get_kpis_for_period
from src.ai.fallback import (
    build_fallback_evidence,
    fallback_response,
    fallback_sql_for_question,
)
from src.analytics.drilldown import (
    warranty_by_branch,
    warranty_by_model,
    warranty_claim_records,
)
from src.analytics.metrics import (
    AnalyticsData,
    Filters,
    gross_margin_by_model,
    overview_kpis,
    revenue,
    revenue_by_branch,
)
from src.database.connection import close_connection
from src.ui.pdf_exports import text_to_pdf


ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / "data" / "business.duckdb"
RAW_DIR = ROOT / "data" / "raw"
BASELINE_PATH = ROOT / "tests" / "parity_baseline.json"
TABLE_NAMES = (
    "branches",
    "models",
    "salespeople",
    "inventory",
    "sales",
    "service_records",
    "warranty_claims",
    "complaints",
    "satisfaction",
)
PACKAGE_NAMES = (
    "python-dotenv",
    "bcrypt",
    "duckdb",
    "fpdf2",
    "google-genai",
    "pandas",
    "plotly",
    "pytest",
    "streamlit",
)
ASK_QUESTIONS = {
    "revenue_trend": "How did completed-sale revenue change by month?",
    "best_branch": "Which branch had the highest completed-sale revenue?",
    "aged_inventory": "Which available vehicles have been in inventory over 90 days?",
    "complaints": "Which branch had the most valid complaints?",
}


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _git_commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _scalar(value: Any) -> Any:
    if value is None or value is pd.NA:
        return None
    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.isoformat()
    if isinstance(value, np.datetime64):
        return pd.Timestamp(value).isoformat()
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (np.floating, float)):
        number = float(value)
        return number if math.isfinite(number) else None
    if isinstance(value, (str, int)):
        return value
    if pd.isna(value):
        return None
    return str(value)


def _canonical_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return [
        {str(column): _scalar(value) for column, value in row.items()}
        for row in frame.to_dict(orient="records")
    ]


def frame_snapshot(frame: pd.DataFrame, *, record_limit: int = 500) -> dict[str, Any]:
    """Return an ordered, JSON-safe snapshot or a stable full-content hash."""
    normalized = frame.reset_index(drop=True)
    records = _canonical_records(normalized)
    result: dict[str, Any] = {
        "columns": [str(column) for column in normalized.columns],
        "row_count": len(normalized),
    }
    if len(records) <= record_limit:
        result["records"] = records
    else:
        encoded = json.dumps(records, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        result.update(
            {
                "content_sha256": sha256(encoded.encode("utf-8")).hexdigest(),
                "first_records": records[:5],
                "last_records": records[-5:],
            }
        )
    return result


def _load_data(connection: duckdb.DuckDBPyConnection) -> AnalyticsData:
    frames = {
        table: connection.execute(f'SELECT * FROM "{table}"').fetchdf()
        for table in TABLE_NAMES
    }
    return AnalyticsData(**frames)


def scenario_filters(connection: duckdb.DuckDBPyConnection) -> dict[str, Filters]:
    """Return fixed, meaningful scenarios selected during Phase 0."""
    minimum, maximum = connection.execute(
        "SELECT MIN(sale_date), MAX(sale_date) FROM sales WHERE sale_date IS NOT NULL"
    ).fetchone()
    default_start = maximum - pd.Timedelta(days=89)
    return {
        "default_90_days": Filters(start_date=default_start, end_date=maximum),
        "full_range": Filters(start_date=minimum, end_date=maximum),
        "branch_accra": Filters(start_date=minimum, end_date=maximum, branch=("Accra",)),
        "model_hilux": Filters(start_date=minimum, end_date=maximum, model=("Hilux",)),
        "brand_salesperson": Filters(
            start_date=minimum,
            end_date=maximum,
            brand=("Elara",),
            salesperson=("Michael Darko",),
        ),
        "all_filters": Filters(
            start_date=minimum,
            end_date=maximum,
            branch=("Accra",),
            brand=("Elara",),
            model=("Yaris",),
            salesperson=("Michael Darko",),
            status=("completed",),
        ),
        "single_day": Filters(start_date=maximum, end_date=maximum),
        "empty_result": Filters(
            start_date=minimum,
            end_date=maximum,
            branch=("No such branch",),
        ),
    }


def _display_kpis(frame: pd.DataFrame) -> list[dict[str, Any]]:
    display = []
    for row in frame.to_dict(orient="records"):
        metric = str(row["metric"])
        value = float(row["value"])
        if metric in {"Revenue", "Gross margin"}:
            formatted = f"GHS {value:,.0f}"
        elif metric == "Units sold":
            formatted = f"{value:,.0f}"
        else:
            formatted = "—" if pd.isna(value) else f"{value:.1%}"
        rate = row["change_rate"]
        delta = None if pd.isna(rate) else f"{float(rate):+.1%} vs prior period"
        display.append({"metric": metric, "value": formatted, "change": delta})
    return display


def _overview_snapshot(data: AnalyticsData, filters: Filters) -> dict[str, Any]:
    kpis = overview_kpis(data, filters)
    return {
        "filters": _json_filters(filters),
        "kpis": frame_snapshot(kpis),
        "kpi_display": _display_kpis(kpis),
        "revenue_trend": frame_snapshot(revenue(data, filters)),
        "revenue_by_branch": frame_snapshot(revenue_by_branch(data, filters)),
        "gross_margin_by_model": frame_snapshot(gross_margin_by_model(data, filters)),
    }


def _json_filters(filters: Filters) -> dict[str, Any]:
    return {key: _scalar(value) if not isinstance(value, tuple) else list(value) for key, value in asdict(filters).items()}


def _metadata(connection: duckdb.DuckDBPyConnection) -> dict[str, Any]:
    row_counts = {
        table: connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
        for table in (*TABLE_NAMES, "cleaning_log")
    }
    update_dates: dict[str, Any] = {}
    for table in TABLE_NAMES:
        columns = {
            row[0] for row in connection.execute(f'DESCRIBE "{table}"').fetchall()
        }
        if "record_updated_at" in columns:
            update_dates[table] = _scalar(
                connection.execute(
                    f'SELECT MAX(record_updated_at) FROM "{table}"'
                ).fetchone()[0]
            )
    package_versions = {}
    for package in PACKAGE_NAMES:
        try:
            package_versions[package] = version(package)
        except PackageNotFoundError:
            package_versions[package] = None
    return {
        "source_git_commit": _git_commit(),
        "database_path": "data/business.duckdb",
        "database_bytes": DATABASE_PATH.stat().st_size,
        "database_sha256": _file_sha256(DATABASE_PATH),
        "raw_source_sha256": {
            path.name: _file_sha256(path) for path in sorted(RAW_DIR.glob("*.csv"))
        },
        "table_row_counts": row_counts,
        "source_update_dates": update_dates,
        "maximum_source_update_date": max(update_dates.values(), default=None),
        "python_version": sys.version.split()[0],
        "package_versions": package_versions,
    }


def _ask_snapshot(connection: duckdb.DuckDBPyConnection) -> dict[str, Any]:
    valid = "COALESCE(_row_quality_status, 'VALID') <> 'ERROR'"
    summary_queries = {
        "revenue": f"SELECT COALESCE(SUM(net_sale_price),0) FROM sales WHERE sale_status='completed' AND {valid}",
        "completed_sales": f"SELECT COUNT(*) FROM sales WHERE sale_status='completed' AND {valid}",
        "branches": "SELECT COUNT(*) FROM branches WHERE branch_name IS NOT NULL",
        "available_over_90_days": (
            "SELECT COUNT(*) FROM inventory WHERE inventory_status='available' "
            "AND arrival_date IS NOT NULL "
            "AND date_diff('day',arrival_date,record_updated_at)>90 "
            f"AND {valid}"
        ),
    }
    summary = {
        key: _scalar(connection.execute(query).fetchone()[0])
        for key, query in summary_queries.items()
    }
    summary_display = {
        "revenue": f"GHS {float(summary['revenue']) / 1_000_000_000:.2f}B",
        "completed_sales": f"{int(summary['completed_sales']):,}",
        "branches": f"{int(summary['branches']):,}",
        "available_over_90_days": f"{int(summary['available_over_90_days']):,}",
    }
    questions = {}
    for key, question in ASK_QUESTIONS.items():
        sql, _ = fallback_sql_for_question(question)
        if not sql:
            raise AssertionError(f"Reviewed SQL missing for {key}")
        result = connection.execute(sql).fetchdf()
        evidence = build_fallback_evidence(question, result)
        questions[key] = {
            "question": question,
            "result": frame_snapshot(result),
            "answer": fallback_response(question, evidence),
            "evidence": _json_safe(evidence),
        }
    return {"summary": summary, "summary_display": summary_display, "questions": questions}


def _management_snapshot(connection: duckdb.DuckDBPyConnection) -> dict[str, Any]:
    del connection
    start_date, end_date = "2024-01-01", "2024-12-31"
    try:
        kpis = get_kpis_for_period(start_date, end_date)
    finally:
        # get_kpis_for_period uses the repository's thread-local connection.
        # Release it so this test helper cannot affect later tests that open the
        # same file with a different DuckDB configuration.
        close_connection()
    evidence = build_evidence(kpis, start_date, end_date)
    exports = _management_exports(start_date, end_date, kpis, evidence)
    return {
        "start_date": start_date,
        "end_date": end_date,
        "kpis": {
            "revenue": _scalar(kpis["revenue"]),
            "sales": _scalar(kpis["sales"]),
            "avg_ticket": _scalar(kpis["avg_ticket"]),
            "low_stock": _scalar(kpis["low_stock"]),
            "branch_df": frame_snapshot(kpis["branch_df"]),
            "monthly_df": frame_snapshot(kpis["monthly_df"]),
        },
        "evidence": [
            {
                "id": item["id"],
                "label": item["label"],
                "value": item["value"],
                "number": _scalar(item["number"]),
                "data": frame_snapshot(item["df"]),
            }
            for item in evidence
        ],
        "exports": exports,
    }


def _brief_markdown(
    start_date: str, end_date: str, kpis: dict[str, Any], evidence: list[dict[str, Any]]
) -> str:
    rows = pd.DataFrame(
        [
            {"Evidence ID": item["id"], "Description": item["label"], "Value": item["value"]}
            for item in evidence
        ]
    )
    return (
        f"# Management Brief {start_date} to {end_date}\n\n"
        f"Revenue: GHS {kpis['revenue']:,.2f}\n\n"
        f"Sales: {kpis['sales']:,}\n\n"
        "## Supporting Evidence\n"
        f"{rows.to_markdown(index=False)}\n"
    )


def _management_exports(
    start_date: str,
    end_date: str,
    kpis: dict[str, Any],
    evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    """Capture the current export outcome, including a missing optional package."""
    try:
        markdown = _brief_markdown(start_date, end_date, kpis, evidence)
    except ImportError as exc:
        message = str(exc)
        return {
            "markdown": {
                "available": False,
                "error_type": type(exc).__name__,
                "error": message,
            },
            "pdf": {
                "available": False,
                "blocked_by": "markdown_export",
                "error_type": type(exc).__name__,
                "error": message,
            },
        }
    pdf_bytes = text_to_pdf(
        f"VersalMotors management brief: {start_date} to {end_date}", markdown
    )
    return {
        "markdown": {
            "available": True,
            "sha256": sha256(markdown.encode("utf-8")).hexdigest(),
            "bytes": len(markdown.encode("utf-8")),
        },
        "pdf": {
            "available": True,
            "sha256": sha256(pdf_bytes).hexdigest(),
            "bytes": len(pdf_bytes),
        },
    }


def _quality_checks(connection: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    results: list[dict[str, Any]] = []
    tables = [row[0] for row in connection.execute("SHOW TABLES").fetchall()]
    primary_keys = {
        "branches": "branch_id",
        "models": "model_id",
        "salespeople": "salesperson_id",
        "inventory": "inventory_id",
        "sales": "sale_id",
        "service_records": "service_id",
        "warranty_claims": "claim_id",
        "complaints": "complaint_id",
        "satisfaction": "survey_id",
    }

    def add(table: str, issue: str, count: int, total: int, impact: str) -> None:
        results.append(
            {
                "table": table,
                "issue": issue,
                "count": int(count),
                "total_rows": int(total),
                "share_pct": round(count / total * 100, 2) if total else 0,
                "impact": impact,
            }
        )

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
                add(
                    table,
                    f"Missing values in {column}",
                    missing,
                    total,
                    f"Affects KPIs if {column} is revenue/date. Analyses filtering on {column} will undercount [EV-001].",
                )
        primary_key = primary_keys.get(table.lower())
        if primary_key and primary_key in columns:
            duplicates = connection.execute(
                f'SELECT COUNT(*) - COUNT(DISTINCT "{primary_key}") FROM "{table}"'
            ).fetchone()[0]
            if duplicates:
                add(
                    table,
                    "Duplicate primary keys",
                    duplicates,
                    total,
                    "Can inflate counts and financial totals if not resolved.",
                )
        lowered = [column.lower() for column in columns]
        if "model" in lowered:
            model_column = columns[lowered.index("model")]
            unknown = connection.execute(
                f"SELECT COUNT(*) FROM \"{table}\" WHERE "
                f"LOWER(\"{model_column}\") IN ('unknown','unk','n/a','na','') "
                f"OR \"{model_column}\" IS NULL"
            ).fetchone()[0]
            if unknown:
                add(
                    table,
                    f"Unknown models in {model_column}",
                    unknown,
                    total,
                    "Affects Product / Inventory conclusions. Model breakdown will be inaccurate.",
                )
        for date_column in [column for column in columns if "date" in column.lower()]:
            try:
                invalid = connection.execute(
                    f'SELECT COUNT(*) FROM "{table}" WHERE "{date_column}"::DATE '
                    f"> CURRENT_DATE OR \"{date_column}\"::DATE < '2000-01-01'"
                ).fetchone()[0]
                issue = f"Invalid dates in {date_column}"
                impact = (
                    "Affects monthly revenue trends, June drop analysis, and Management Brief "
                    "period filter [EV-005]."
                )
            except duckdb.Error:
                invalid = connection.execute(
                    f'SELECT COUNT(*) FROM "{table}" WHERE '
                    f'TRY_CAST("{date_column}" AS DATE) IS NULL AND "{date_column}" IS NOT NULL'
                ).fetchone()[0]
                issue = f"Unparsable dates in {date_column}"
                impact = "Breaks time-series. Rows excluded from period KPIs."
            if invalid:
                add(table, issue, invalid, total, impact)
        if table.lower() == "sales" and "branches" in [name.lower() for name in tables]:
            orphans = connection.execute(
                "SELECT COUNT(*) FROM sales s LEFT JOIN branches b "
                "ON s.branch_id=b.branch_id WHERE b.branch_id IS NULL"
            ).fetchone()[0]
            if orphans:
                add(
                    table,
                    "Orphan records: branch_id not in branches",
                    orphans,
                    total,
                    "Branch performance conclusions (best branch) will be incomplete [EV-004].",
                )
    return pd.DataFrame(results)


def _quality_snapshot(connection: duckdb.DuckDBPyConnection) -> dict[str, Any]:
    checks = _quality_checks(connection)
    if checks.empty:
        summary = {
            "issues_found": 0,
            "tables_affected": 0,
            "total_affected": 0,
            "highest_share": 0.0,
        }
    else:
        summary = {
            "issues_found": len(checks),
            "tables_affected": int(checks["table"].nunique()),
            "total_affected": int(checks["count"].sum()),
            "highest_share": float(checks["share_pct"].max()),
        }
    csv_bytes = checks.to_csv(index=False).encode("utf-8")
    cleaning_log = connection.execute("SELECT * FROM cleaning_log").fetchdf()
    return {
        "summary": summary,
        "checks": frame_snapshot(checks),
        "csv_sha256": sha256(csv_bytes).hexdigest(),
        "csv_bytes": len(csv_bytes),
        "cleaning_log": frame_snapshot(cleaning_log),
    }


def _json_safe(value: Any) -> Any:
    if isinstance(value, pd.DataFrame):
        return frame_snapshot(value)
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return _scalar(value)


def _investigate_snapshot(
    data: AnalyticsData, filters: Filters
) -> dict[str, Any]:
    models = warranty_by_model(data, filters)
    if models.empty:
        return {
            "filters": _json_filters(filters),
            "selected_model": None,
            "selected_branch": None,
            "models": frame_snapshot(models),
            "branches": frame_snapshot(pd.DataFrame()),
            "claims": frame_snapshot(pd.DataFrame()),
        }
    selected_model = str(models.iloc[0]["model"])
    branches = warranty_by_branch(data, filters, selected_model)
    selected_branch = str(branches.iloc[0]["branch"]) if not branches.empty else None
    claims = (
        warranty_claim_records(data, filters, selected_model, selected_branch)
        if selected_branch
        else pd.DataFrame()
    )
    return {
        "filters": _json_filters(filters),
        "selected_model": selected_model,
        "selected_branch": selected_branch,
        "models": frame_snapshot(models),
        "branches": frame_snapshot(branches),
        "claims": frame_snapshot(claims),
    }


def capture_current_baseline() -> dict[str, Any]:
    """Capture current public-function behavior without modifying any data."""
    if not DATABASE_PATH.is_file():
        raise FileNotFoundError("data/business.duckdb is required for Phase 0 capture")
    connection = duckdb.connect(str(DATABASE_PATH), read_only=True)
    try:
        data = _load_data(connection)
        scenarios = scenario_filters(connection)
        baseline = {
            "schema_version": 1,
            "metadata": _metadata(connection),
            "scenarios": {
                name: _overview_snapshot(data, filters)
                for name, filters in scenarios.items()
            },
            "investigate": _investigate_snapshot(data, scenarios["default_90_days"]),
            "ask_the_business": _ask_snapshot(connection),
            "management_brief": _management_snapshot(connection),
            "data_quality": _quality_snapshot(connection),
        }
    finally:
        connection.close()
    return baseline


def _filter_sql(filters: Filters, *, alias: str = "s") -> tuple[str, list[Any]]:
    clauses: list[str] = []
    params: list[Any] = []
    if filters.start_date is not None:
        clauses.append(f"{alias}.sale_date >= ?")
        params.append(filters.start_date)
    if filters.end_date is not None:
        clauses.append(f"{alias}.sale_date <= ?")
        params.append(filters.end_date)

    dimensions = {
        "branch": ["b.branch_id", "b.branch_code", "b.branch_name", "b.branch_name_raw", "b.city"],
        "model": ["m.model_id", "m.model_name", "m.model_name_raw"],
        "brand": ["m.manufacturer"],
        "salesperson": ["p.salesperson_id", "p.employee_code", "TRIM(COALESCE(p.first_name,'') || ' ' || COALESCE(p.last_name,''))"],
        "status": [f"{alias}.sale_status"],
    }
    for field, columns in dimensions.items():
        values = tuple(getattr(filters, field))
        if not values:
            continue
        wanted = [str(value).strip().casefold() for value in values]
        placeholders = ",".join("?" for _ in wanted)
        alternatives = []
        for column in columns:
            alternatives.append(
                f"LOWER(TRIM(CAST({column} AS VARCHAR))) IN ({placeholders})"
            )
            params.extend(wanted)
        clauses.append("(" + " OR ".join(alternatives) + ")")
    if not filters.status:
        clauses.append(f"{alias}.sale_status = 'completed'")
    return (" AND ".join(clauses) if clauses else "TRUE"), params


SALES_CTES = """
WITH inv AS (
    SELECT * EXCLUDE (_parity_row)
    FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY inventory_id ORDER BY rowid) AS _parity_row FROM inventory)
    WHERE _parity_row = 1
), model_dim AS (
    SELECT * EXCLUDE (_parity_row)
    FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY model_id ORDER BY rowid) AS _parity_row FROM models)
    WHERE _parity_row = 1
), branch_dim AS (
    SELECT * EXCLUDE (_parity_row)
    FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY branch_id ORDER BY rowid) AS _parity_row FROM branches)
    WHERE _parity_row = 1
), people_dim AS (
    SELECT * EXCLUDE (_parity_row)
    FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY salesperson_id ORDER BY rowid) AS _parity_row FROM salespeople)
    WHERE _parity_row = 1
), base AS (
    SELECT s.sale_id, s.inventory_id, s.branch_id, s.salesperson_id, s.sale_date,
           s.sale_status, s.net_sale_price, s.gross_price, s.discount_amount,
           i.acquisition_cost, i.model_id, i.model_id_orphan_flag,
           m.model_name, m.model_name_raw, m.manufacturer,
           b.branch_code, b.branch_name, b.branch_name_raw, b.city,
           p.employee_code, p.first_name, p.last_name
    FROM sales s
    LEFT JOIN inv i ON s.inventory_id = i.inventory_id
    LEFT JOIN model_dim m ON i.model_id = m.model_id
    LEFT JOIN branch_dim b ON s.branch_id = b.branch_id
    LEFT JOIN people_dim p ON s.salesperson_id = p.salesperson_id
    WHERE COALESCE(s._row_quality_status, 'VALID') <> 'ERROR'
      AND UPPER(CAST(i._row_quality_status AS VARCHAR)) <> 'ERROR'
      AND i.model_id_orphan_flag IS DISTINCT FROM TRUE
)
"""


WARRANTY_CTES = """
WITH inv AS (
    SELECT * EXCLUDE (_parity_row)
    FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY inventory_id ORDER BY rowid) AS _parity_row FROM inventory)
    WHERE _parity_row = 1
), model_dim AS (
    SELECT * EXCLUDE (_parity_row)
    FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY model_id ORDER BY rowid) AS _parity_row FROM models)
    WHERE _parity_row = 1
), branch_dim AS (
    SELECT * EXCLUDE (_parity_row)
    FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY branch_id ORDER BY rowid) AS _parity_row FROM branches)
    WHERE _parity_row = 1
), sale_dim AS (
    SELECT * EXCLUDE (_parity_row)
    FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY sale_id ORDER BY rowid) AS _parity_row FROM sales)
    WHERE _parity_row = 1
), people_dim AS (
    SELECT * EXCLUDE (_parity_row)
    FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY salesperson_id ORDER BY rowid) AS _parity_row FROM salespeople)
    WHERE _parity_row = 1
), warranty_base AS (
    SELECT c.claim_id, c.claim_date, c.failure_category, c.claim_description,
           c.claim_status, c.claim_amount, c.approved_amount,
           c.manufacturer_recovery_amount, c.sale_id, c.service_id,
           c.inventory_id, c.branch_id, c._row_quality_status,
           inv.model_id, inv.model_id_orphan_flag,
           m.model_name AS model, m.manufacturer,
           b.branch_name AS branch, b.branch_code,
           s.salesperson_id, s.sale_status,
           p.employee_code, p.first_name, p.last_name
    FROM warranty_claims c
    LEFT JOIN inv ON c.inventory_id = inv.inventory_id
    LEFT JOIN model_dim m ON inv.model_id = m.model_id
    LEFT JOIN branch_dim b ON c.branch_id = b.branch_id
    LEFT JOIN sale_dim s ON c.sale_id = s.sale_id
    LEFT JOIN people_dim p ON s.salesperson_id = p.salesperson_id
    WHERE COALESCE(c._row_quality_status, 'VALID') <> 'ERROR'
      AND UPPER(CAST(inv._row_quality_status AS VARCHAR)) <> 'ERROR'
      AND inv.model_id_orphan_flag IS DISTINCT FROM TRUE
      AND m.model_name IS NOT NULL
      AND b.branch_name IS NOT NULL
      AND NOT REGEXP_MATCHES(m.model_name, '(?i)Model ID|Unmapped')
      AND NOT REGEXP_MATCHES(b.branch_name, '(?i)Model ID|Unmapped')
)
"""


def _warranty_where(filters: Filters) -> tuple[str, list[Any]]:
    clauses: list[str] = []
    params: list[Any] = []
    if filters.start_date is not None:
        clauses.append("claim_date >= ?")
        params.append(filters.start_date)
    if filters.end_date is not None:
        clauses.append("claim_date <= ?")
        params.append(filters.end_date)
    dimensions = {
        "branch": ["branch_id", "branch", "branch_code"],
        "model": ["model_id", "model"],
        "brand": ["manufacturer"],
        "salesperson": [
            "salesperson_id",
            "employee_code",
            "TRIM(COALESCE(first_name,'') || ' ' || COALESCE(last_name,''))",
        ],
        "status": ["sale_status"],
    }
    for field, columns in dimensions.items():
        values = tuple(getattr(filters, field))
        if not values:
            continue
        wanted = [str(value).strip().casefold() for value in values]
        placeholders = ",".join("?" for _ in wanted)
        alternatives = []
        for column in columns:
            alternatives.append(
                f"LOWER(TRIM(CAST({column} AS VARCHAR))) IN ({placeholders})"
            )
            params.extend(wanted)
        clauses.append("(" + " OR ".join(alternatives) + ")")
    return (" AND ".join(clauses) if clauses else "TRUE"), params


def _sql_warranty_models(
    connection: duckdb.DuckDBPyConnection, filters: Filters
) -> pd.DataFrame:
    where, params = _warranty_where(filters)
    current = connection.execute(
        WARRANTY_CTES
        + f"""
        SELECT model, COUNT(claim_id) AS claim_count,
               COALESCE(SUM(approved_amount), 0) AS claim_cost
        FROM warranty_base
        WHERE {where} AND claim_date IS NOT NULL
        GROUP BY model
        """,
        params,
    ).fetchdf()
    previous = pd.DataFrame(columns=["model", "previous_claim_cost"])
    if filters.start_date is not None and filters.end_date is not None:
        start, end = pd.Timestamp(filters.start_date), pd.Timestamp(filters.end_date)
        if end >= start:
            duration = end - start
            previous_filters = replace(
                filters,
                start_date=start - duration - pd.Timedelta(days=1),
                end_date=start - pd.Timedelta(days=1),
            )
            previous_where, previous_params = _warranty_where(previous_filters)
            previous = connection.execute(
                WARRANTY_CTES
                + f"""
                SELECT model, COALESCE(SUM(approved_amount), 0) AS previous_claim_cost
                FROM warranty_base
                WHERE {previous_where} AND claim_date IS NOT NULL
                GROUP BY model
                """,
                previous_params,
            ).fetchdf()
    result = current.merge(previous, on="model", how="left")
    result["previous_claim_cost"] = result["previous_claim_cost"].fillna(0.0)
    result["cost_change"] = result["claim_cost"] - result["previous_claim_cost"]
    result["cost_change_rate"] = result["cost_change"].div(
        result["previous_claim_cost"].where(result["previous_claim_cost"] != 0)
    )
    columns = [
        "model",
        "claim_count",
        "claim_cost",
        "previous_claim_cost",
        "cost_change",
        "cost_change_rate",
    ]
    return result[columns].sort_values("claim_cost", ascending=False, ignore_index=True)


def _sql_investigate(
    connection: duckdb.DuckDBPyConnection, filters: Filters
) -> dict[str, Any]:
    models = _sql_warranty_models(connection, filters)
    if models.empty:
        return {
            "filters": _json_filters(filters),
            "selected_model": None,
            "selected_branch": None,
            "models": frame_snapshot(models),
            "branches": frame_snapshot(pd.DataFrame()),
            "claims": frame_snapshot(pd.DataFrame()),
        }
    selected_model = str(models.iloc[0]["model"])
    where, params = _warranty_where(filters)
    branches = connection.execute(
        WARRANTY_CTES
        + f"""
        SELECT branch, COUNT(claim_id) AS claim_count,
               COALESCE(SUM(approved_amount), 0) AS claim_cost
        FROM warranty_base
        WHERE {where}
          AND LOWER(TRIM(model)) = LOWER(TRIM(?))
        GROUP BY branch
        ORDER BY claim_cost DESC
        """,
        [*params, selected_model],
    ).fetchdf()
    total = branches["claim_cost"].sum() if not branches.empty else 0.0
    branches["share_of_model_cost"] = branches["claim_cost"].div(
        total if total else float("nan")
    )
    branches = branches[
        ["branch", "claim_count", "claim_cost", "share_of_model_cost"]
    ]
    selected_branch = str(branches.iloc[0]["branch"]) if not branches.empty else None
    claims = pd.DataFrame()
    if selected_branch:
        claims = connection.execute(
            WARRANTY_CTES
            + f"""
            SELECT claim_id, claim_date, model, branch, failure_category,
                   claim_description, claim_status, claim_amount, approved_amount,
                   manufacturer_recovery_amount, sale_id, service_id, inventory_id,
                   _row_quality_status
            FROM warranty_base
            WHERE {where}
              AND LOWER(TRIM(model)) = LOWER(TRIM(?))
              AND LOWER(TRIM(branch)) = LOWER(TRIM(?))
            ORDER BY claim_date DESC, claim_id ASC
            """,
            [*params, selected_model, selected_branch],
        ).fetchdf()
    return {
        "filters": _json_filters(filters),
        "selected_model": selected_model,
        "selected_branch": selected_branch,
        "models": frame_snapshot(models),
        "branches": frame_snapshot(branches),
        "claims": frame_snapshot(claims),
    }


def _sql_overview(
    connection: duckdb.DuckDBPyConnection, filters: Filters
) -> dict[str, Any]:
    where, params = _filter_sql(filters)
    current = _sql_kpi_values(connection, filters)
    previous = {key: None for key in current}
    if filters.start_date is not None and filters.end_date is not None:
        start, end = pd.Timestamp(filters.start_date), pd.Timestamp(filters.end_date)
        if end >= start:
            duration = end - start
            previous = _sql_kpi_values(
                connection,
                replace(
                    filters,
                    start_date=start - duration - pd.Timedelta(days=1),
                    end_date=start - pd.Timedelta(days=1),
                ),
            )
    kpi_rows = []
    for metric in ("Revenue", "Gross margin", "Units sold", "Discount rate"):
        value = current[metric]
        prior = previous[metric]
        change = value - prior if prior is not None else None
        rate = change / abs(prior) if prior not in (None, 0) else None
        kpi_rows.append(
            {
                "metric": metric,
                "value": value,
                "previous_value": prior,
                "change": change,
                "change_rate": rate,
            }
        )
    kpi_frame = pd.DataFrame(kpi_rows)
    trend = connection.execute(
        SALES_CTES
        + f"""
        SELECT DATE_TRUNC('month', sale_date) AS period,
               SUM(net_sale_price) AS revenue,
               COUNT(sale_id) AS transaction_count
        FROM base s LEFT JOIN branch_dim b USING (branch_id)
        LEFT JOIN model_dim m USING (model_id)
        LEFT JOIN people_dim p USING (salesperson_id)
        WHERE {where} AND sale_date IS NOT NULL AND net_sale_price IS NOT NULL
        GROUP BY 1 ORDER BY 1
        """,
        params,
    ).fetchdf()
    branches = connection.execute(
        SALES_CTES
        + f"""
        SELECT s.branch_name AS branch, SUM(net_sale_price) AS revenue,
               COUNT(DISTINCT inventory_id) AS units_sold
        FROM base s LEFT JOIN branch_dim b USING (branch_id)
        LEFT JOIN model_dim m USING (model_id)
        LEFT JOIN people_dim p USING (salesperson_id)
        WHERE {where} AND sale_date IS NOT NULL AND net_sale_price IS NOT NULL
          AND s.branch_name IS NOT NULL
        GROUP BY 1 ORDER BY revenue DESC
        """,
        params,
    ).fetchdf()
    models = connection.execute(
        SALES_CTES
        + f"""
        SELECT COALESCE(s.model_name, s.model_name_raw) AS model,
               SUM(net_sale_price) AS revenue,
               SUM(net_sale_price - acquisition_cost) AS gross_margin,
               SUM(net_sale_price - acquisition_cost) / NULLIF(SUM(net_sale_price), 0) AS gross_margin_rate
        FROM base s LEFT JOIN branch_dim b USING (branch_id)
        LEFT JOIN model_dim m USING (model_id)
        LEFT JOIN people_dim p USING (salesperson_id)
        WHERE {where} AND sale_date IS NOT NULL AND net_sale_price IS NOT NULL
          AND acquisition_cost IS NOT NULL
          AND COALESCE(s.model_name, s.model_name_raw) IS NOT NULL
          AND NOT REGEXP_MATCHES(COALESCE(s.model_name, s.model_name_raw), '(?i)Model ID|Unmapped')
        GROUP BY 1 ORDER BY gross_margin DESC
        """,
        params,
    ).fetchdf()
    return {
        "filters": _json_filters(filters),
        "kpis": frame_snapshot(kpi_frame),
        "kpi_display": _display_kpis(kpi_frame),
        "revenue_trend": frame_snapshot(trend),
        "revenue_by_branch": frame_snapshot(branches),
        "gross_margin_by_model": frame_snapshot(models),
    }


def _sql_kpi_values(
    connection: duckdb.DuckDBPyConnection, filters: Filters
) -> dict[str, float | None]:
    where, params = _filter_sql(filters)
    row = connection.execute(
        SALES_CTES
        + f"""
        SELECT
          COALESCE(SUM(net_sale_price) FILTER (
            WHERE sale_date IS NOT NULL AND net_sale_price IS NOT NULL
          ), 0) AS revenue,
          COALESCE(SUM(net_sale_price - acquisition_cost) FILTER (
            WHERE sale_date IS NOT NULL AND net_sale_price IS NOT NULL AND acquisition_cost IS NOT NULL
          ), 0) AS gross_margin,
          COALESCE(COUNT(DISTINCT inventory_id) FILTER (
            WHERE sale_date IS NOT NULL AND inventory_id IS NOT NULL
          ), 0) AS units_sold,
          SUM(discount_amount) FILTER (
            WHERE sale_date IS NOT NULL AND gross_price IS NOT NULL AND discount_amount IS NOT NULL
          ) / NULLIF(SUM(gross_price) FILTER (
            WHERE sale_date IS NOT NULL AND gross_price IS NOT NULL AND discount_amount IS NOT NULL
          ), 0) AS discount_rate
        FROM base s LEFT JOIN branch_dim b USING (branch_id)
        LEFT JOIN model_dim m USING (model_id)
        LEFT JOIN people_dim p USING (salesperson_id)
        WHERE {where}
        """,
        params,
    ).fetchone()
    return {
        "Revenue": float(row[0] or 0),
        "Gross margin": float(row[1] or 0),
        "Units sold": float(row[2] or 0),
        "Discount rate": None if row[3] is None else float(row[3]),
    }


def capture_direct_sql_verification() -> dict[str, Any]:
    """Independently reproduce every stored numeric baseline through DuckDB SQL."""
    connection = duckdb.connect(str(DATABASE_PATH), read_only=True)
    try:
        scenarios = scenario_filters(connection)
        return {
            "scenarios": {
                name: _sql_overview(connection, filters)
                for name, filters in scenarios.items()
            },
            "investigate": _sql_investigate(
                connection, scenarios["default_90_days"]
            ),
            "ask_the_business": _ask_snapshot(connection),
            "management_brief": _sql_management_snapshot(connection),
            "data_quality": _quality_snapshot(connection),
        }
    finally:
        connection.close()


def _sql_management_snapshot(connection: duckdb.DuckDBPyConnection) -> dict[str, Any]:
    start_date, end_date = "2024-01-01", "2024-12-31"
    revenue_value, sales_count = connection.execute(
        "SELECT COALESCE(SUM(total_sale_price),0), COUNT(*) FROM sales "
        "WHERE sale_date BETWEEN ? AND ?",
        [start_date, end_date],
    ).fetchone()
    revenue_value = float(revenue_value)
    sales_count = int(sales_count)
    branch_df = connection.execute(
        "SELECT branch_id, SUM(total_sale_price) AS rev, COUNT(*) AS cnt "
        "FROM sales WHERE sale_date BETWEEN ? AND ? GROUP BY branch_id ORDER BY rev DESC",
        [start_date, end_date],
    ).fetchdf()
    monthly_df = connection.execute(
        "SELECT DATE_TRUNC('month', sale_date)::DATE AS month, SUM(total_sale_price) AS rev "
        "FROM sales WHERE sale_date BETWEEN ? AND ? GROUP BY 1 ORDER BY 1",
        [start_date, end_date],
    ).fetchdf()
    inventory_columns = {
        row[0] for row in connection.execute("DESCRIBE inventory").fetchall()
    }
    low_stock = (
        connection.execute("SELECT COUNT(*) FROM inventory WHERE quantity < 10").fetchone()[0]
        if "quantity" in inventory_columns
        else 0
    )
    kpis = {
        "revenue": revenue_value,
        "sales": sales_count,
        "avg_ticket": revenue_value / sales_count if sales_count else 0.0,
        "low_stock": int(low_stock),
        "branch_df": branch_df,
        "monthly_df": monthly_df,
        "rev_col": "total_sale_price",
        "date_col": "sale_date",
    }
    evidence = build_evidence(kpis, start_date, end_date)
    exports = _management_exports(start_date, end_date, kpis, evidence)
    return {
        "start_date": start_date,
        "end_date": end_date,
        "kpis": {
            "revenue": revenue_value,
            "sales": sales_count,
            "avg_ticket": kpis["avg_ticket"],
            "low_stock": int(low_stock),
            "branch_df": frame_snapshot(branch_df),
            "monthly_df": frame_snapshot(monthly_df),
        },
        "evidence": [
            {
                "id": item["id"],
                "label": item["label"],
                "value": item["value"],
                "number": _scalar(item["number"]),
                "data": frame_snapshot(item["df"]),
            }
            for item in evidence
        ],
        "exports": exports,
    }


def assert_nested_equal(
    actual: Any, expected: Any, *, path: str = "root", tolerance: float = 1e-9
) -> None:
    """Compare nested parity data with explicit numeric tolerances."""
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            raise AssertionError(f"{path}: expected dict, got {type(actual).__name__}")
        if set(actual) != set(expected):
            raise AssertionError(
                f"{path}: keys differ; actual={sorted(actual)}, expected={sorted(expected)}"
            )
        for key in expected:
            assert_nested_equal(actual[key], expected[key], path=f"{path}.{key}", tolerance=tolerance)
        return
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            raise AssertionError(
                f"{path}: list shape differs; actual={len(actual) if isinstance(actual, list) else type(actual).__name__}, expected={len(expected)}"
            )
        for index, item in enumerate(expected):
            assert_nested_equal(actual[index], item, path=f"{path}[{index}]", tolerance=tolerance)
        return
    if isinstance(expected, (int, float)) and not isinstance(expected, bool):
        if not isinstance(actual, (int, float)) or isinstance(actual, bool):
            raise AssertionError(f"{path}: expected numeric {expected!r}, got {actual!r}")
        if not math.isclose(float(actual), float(expected), rel_tol=tolerance, abs_tol=tolerance):
            raise AssertionError(f"{path}: {actual!r} != {expected!r}")
        return
    if actual != expected:
        raise AssertionError(f"{path}: {actual!r} != {expected!r}")


def write_baseline(path: Path = BASELINE_PATH) -> dict[str, Any]:
    baseline = capture_current_baseline()
    path.write_text(
        json.dumps(baseline, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return baseline


def load_baseline(path: Path = BASELINE_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
