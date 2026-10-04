import duckdb
import os
import glob
from pathlib import Path
import streamlit as st
import threading
import pandas as pd
import re

# Allowlisted tables to prevent arbitrary file reading (e.g. read_csv)
ALLOWED_TABLES = {
    'sales', 'inventory', 'models', 'branches', 'salespeople',
    'service_records', 'warranty_claims', 'complaints', 'satisfaction'
}

# Thread-local storage to hold the DuckDB connection
_thread_local = threading.local()

def get_db_path() -> str:
    """Find the database path."""
    possible = ["data/business.duckdb", "business.duckdb", "./data/business.duckdb", "VersalMotors/data/business.duckdb"]
    possible += glob.glob("**/*.duckdb", recursive=True)
    for p in possible:
        if os.path.exists(p):
            return p
    return "data/business.duckdb"

def get_connection(read_only: bool = True) -> duckdb.DuckDBPyConnection:
    """Get or create a DuckDB connection for the current thread."""
    if not hasattr(_thread_local, "con"):
        _thread_local.con = duckdb.connect(get_db_path(), read_only=read_only)
    return _thread_local.con

def close_connection():
    """Close the DuckDB connection for the current thread."""
    if hasattr(_thread_local, "con"):
        try:
            _thread_local.con.close()
        except:
            pass
        finally:
            del _thread_local.con

def run_readonly_sql(query: str, params: list = None) -> pd.DataFrame:
    """Safely run read-only SQL, blocking filesystem access."""
    cleaned = query.strip().removesuffix(";").strip()
    q_lower = cleaned.lower()
    if not re.match(r"^(select|with)\b", q_lower) or ";" in cleaned:
        raise ValueError("Only one SELECT or WITH query is allowed")

    # 1. Block prohibited functions/keywords
    prohibited_functions = [
        "read_csv", "read_parquet", "read_json", "read_text", "glob",
        "sqlite_scan", "postgres_scan",
    ]
    prohibited_keywords = [
        "attach", "pragma", "copy", "insert", "update", "delete", "drop",
        "create", "alter", "install", "load",
    ]
    for function_name in prohibited_functions:
        if re.search(rf"\b{re.escape(function_name)}\s*\(", q_lower):
            raise ValueError(f"Blocked function detected: {function_name}")
    for keyword in prohibited_keywords:
        if re.search(rf"\b{re.escape(keyword)}\b", q_lower):
            raise ValueError(f"Blocked keyword detected: {keyword}")
    if re.search(r"\bhttpfs\b", q_lower):
        raise ValueError("Blocked extension detected: httpfs")

    referenced = re.findall(r"\b(?:from|join)\s+[\"']?([a-z_][a-z0-9_]*)", q_lower)
    cte_names = set(
        re.findall(r"(?:\bwith\b|,)\s*([a-z_][a-z0-9_]*)\s+as\s*\(", q_lower)
    )
    unknown = sorted({
        table for table in referenced
        if table not in ALLOWED_TABLES and table not in cte_names
    })
    if unknown:
        raise ValueError(f"Query references disallowed tables: {', '.join(unknown)}")

    con = get_connection(read_only=True)
    if params:
        return con.execute(cleaned, params).fetchdf()
    return con.execute(cleaned).fetchdf()
