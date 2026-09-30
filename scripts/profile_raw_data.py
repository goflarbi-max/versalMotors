"""Read-only profiler for the versalMotors raw CSV extracts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from datetime import date, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NULLS = {"", "null", "none", "na", "n/a"}
TEXT_HINTS = ("code", "ref", "vin", "name", "text", "description", "address")


def rows_for(table: str):
    with (RAW / f"{table}.csv").open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def non_null(values):
    return [v for v in values if v.strip().lower() not in NULLS]


def numeric(value: str):
    try:
        return float(value)
    except ValueError:
        return None


def parsed_date(value: str):
    try:
        return date.fromisoformat(value[:10])
    except (ValueError, TypeError):
        return None


def infer(column: str, values: list[str]):
    present = non_null(values)
    low = column.lower()
    if not present:
        return "empty"
    if low.endswith("_date") or low.endswith("_at"):
        good = [parsed_date(v) for v in present]
        return "datetime" if low.endswith("_at") else "date"
    if low.endswith("_flag") or set(v.lower() for v in present) <= {"true", "false"}:
        return "boolean"
    nums = [numeric(v) for v in present]
    if all(v is not None for v in nums) and not any(hint in low for hint in TEXT_HINTS):
        if all(float(v).is_integer() for v in nums if v is not None):
            return "integer"
        return "decimal"
    return "string"


def profile(table: str):
    fields, rows = rows_for(table)
    row_tuples = [tuple(row[f] for f in fields) for row in rows]
    duplicate_groups = [count for count in Counter(row_tuples).values() if count > 1]
    normalized_without_pk = [tuple(row[f].strip() for f in fields[1:]) for row in rows]
    normalized_duplicate_extras = sum(
        count - 1 for count in Counter(normalized_without_pk).values() if count > 1
    )
    columns = []
    for field in fields:
        values = [row[field] for row in rows]
        present = non_null(values)
        kind = infer(field, values)
        item = {
            "name": field,
            "type": kind,
            "nulls": len(values) - len(present),
            "distinct": len(set(present)),
        }
        if kind in {"integer", "decimal"}:
            nums = [numeric(v) for v in present]
            valid = [v for v in nums if v is not None]
            item.update(min=min(valid) if valid else None, max=max(valid) if valid else None,
                        invalid=len(nums) - len(valid), negatives=sum(v < 0 for v in valid))
        elif kind in {"date", "datetime"}:
            dates = [parsed_date(v) for v in present]
            valid = [v for v in dates if v is not None]
            item.update(min=min(valid).isoformat() if valid else None,
                        max=max(valid).isoformat() if valid else None,
                        invalid=len(dates) - len(valid))
        if kind in {"string", "boolean"} and 0 < len(set(present)) <= 30:
            item["values"] = sorted(Counter(present).items(), key=lambda pair: (-pair[1], pair[0]))
        columns.append(item)
    pk = fields[0]
    pk_counts = Counter(row[pk] for row in rows)
    return {
        "table": table,
        "rows": len(rows),
        "columns": columns,
        "exact_duplicate_rows": sum(count - 1 for count in duplicate_groups),
        "duplicate_groups": len(duplicate_groups),
        "duplicate_pk_values": sum(1 for count in pk_counts.values() if count > 1),
        "duplicate_pk_extra_rows": sum(count - 1 for count in pk_counts.values() if count > 1),
        "normalized_non_pk_duplicate_extra_rows": normalized_duplicate_extras,
    }


def relationship_report():
    tables = {path.stem: rows_for(path.stem)[1] for path in RAW.glob("*.csv")}
    keys = {name: {row[next(iter(row))] for row in rows} for name, rows in tables.items()}
    relations = [
        ("salespeople", "branch_id", "branches"),
        ("inventory", "model_id", "models"), ("inventory", "branch_id", "branches"),
        ("sales", "inventory_id", "inventory"), ("sales", "branch_id", "branches"), ("sales", "salesperson_id", "salespeople"),
        ("service_records", "inventory_id", "inventory"), ("service_records", "branch_id", "branches"), ("service_records", "sale_id", "sales"),
        ("warranty_claims", "service_id", "service_records"), ("warranty_claims", "inventory_id", "inventory"), ("warranty_claims", "sale_id", "sales"), ("warranty_claims", "branch_id", "branches"),
        ("complaints", "branch_id", "branches"), ("complaints", "sale_id", "sales"), ("complaints", "service_id", "service_records"), ("complaints", "claim_id", "warranty_claims"),
        ("satisfaction", "branch_id", "branches"), ("satisfaction", "sale_id", "sales"), ("satisfaction", "service_id", "service_records"), ("satisfaction", "complaint_id", "complaints"),
    ]
    output = []
    for child, field, parent in relations:
        vals = [row[field] for row in tables[child] if row[field].strip().lower() not in NULLS]
        orphan_values = [value for value in vals if value not in keys[parent]]
        output.append({"child": child, "field": field, "parent": parent,
                       "non_null": len(vals), "orphan_rows": len(orphan_values),
                       "orphan_values": sorted(set(orphan_values))})
    return output


def suspicious_report():
    tables = {path.stem: rows_for(path.stem)[1] for path in RAW.glob("*.csv")}
    out = {}
    inv = {r["inventory_id"]: r for r in tables["inventory"]}
    service = {r["service_id"]: r for r in tables["service_records"]}
    complaints = tables["complaints"]
    claims = tables["warranty_claims"]
    sales = tables["sales"]
    sat = tables["satisfaction"]
    out["vin_invalid_format_rows"] = sum(not re.fullmatch(r"[A-HJ-NPR-Z0-9]{17}", r["vin"]) for r in tables["inventory"])
    vin_counts = Counter(r["vin"] for r in tables["inventory"])
    out["duplicate_vin_extra_rows"] = sum(n - 1 for n in vin_counts.values() if n > 1)
    out["sale_before_arrival_rows"] = sum(bool(r["inventory_id"] in inv and parsed_date(r["sale_date"]) and parsed_date(inv[r["inventory_id"]]["arrival_date"]) and parsed_date(r["sale_date"]) < parsed_date(inv[r["inventory_id"]]["arrival_date"])) for r in sales)
    out["service_close_before_open_rows"] = sum(bool(parsed_date(r["service_close_date"]) and parsed_date(r["service_open_date"]) and parsed_date(r["service_close_date"]) < parsed_date(r["service_open_date"])) for r in tables["service_records"])
    out["complaint_resolution_before_open_rows"] = sum(bool(parsed_date(r["resolution_date"]) and parsed_date(r["complaint_date"]) and parsed_date(r["resolution_date"]) < parsed_date(r["complaint_date"])) for r in complaints)
    out["resolved_complaint_without_date_rows"] = sum(r["resolution_status"] == "resolved" and not r["resolution_date"] for r in complaints)
    out["approved_claim_without_decision_date_rows"] = sum(r["claim_status"] == "approved" and not r["decision_date"] for r in claims)
    out["available_inventory_with_sold_date_rows"] = sum(r["inventory_status"] == "available" and bool(r["sold_date"]) for r in tables["inventory"])
    out["sales_arithmetic_mismatch_rows"] = sum(all(numeric(r[f]) is not None for f in ["gross_price","discount_amount","net_sale_price"]) and abs(numeric(r["gross_price"])-numeric(r["discount_amount"])-numeric(r["net_sale_price"])) > .02 for r in sales)
    out["service_arithmetic_mismatch_rows"] = sum(all(numeric(r[f]) is not None for f in ["labor_cost","parts_cost","misc_cost","total_service_cost"]) and abs(numeric(r["labor_cost"])+numeric(r["parts_cost"])+numeric(r["misc_cost"])-numeric(r["total_service_cost"])) > .03 for r in tables["service_records"])
    out["invalid_satisfaction_score_rows"] = sum(any(numeric(r[f]) is not None and not ((0 <= numeric(r[f]) <= 10) if f == "nps_score" else (1 <= numeric(r[f]) <= (10 if f == "overall_score" else 5))) for f in ["overall_score","nps_score","product_score","staff_score","timeliness_score","value_score"] if r[f] != "") for r in sat)
    out["negative_odometer_rows"] = sum(numeric(r["odometer_km"]) is not None and numeric(r["odometer_km"]) < 0 for r in tables["service_records"])
    out["labor_hours_over_100_rows"] = sum(numeric(r["labor_hours"]) is not None and numeric(r["labor_hours"]) > 100 for r in tables["service_records"])
    out["claim_before_service_open_rows"] = sum(
        bool(r["service_id"] in service and parsed_date(r["claim_date"]) and parsed_date(service[r["service_id"]]["service_open_date"])
             and parsed_date(r["claim_date"]) < parsed_date(service[r["service_id"]]["service_open_date"]))
        for r in claims
    )
    out["finance_sale_missing_term_rows"] = sum(r["payment_method"] == "finance" and not r["finance_term_months"] for r in sales)
    out["non_finance_sale_with_term_rows"] = sum(r["payment_method"] != "finance" and bool(r["finance_term_months"]) for r in sales)
    out["trade_in_flag_value_mismatch_rows"] = sum((r["trade_in_flag"] == "True") != bool(r["trade_in_value"]) for r in sales)
    out["service_payment_components_mismatch_rows"] = sum(
        all(numeric(r[f]) is not None for f in ["customer_pay_amount", "warranty_pay_amount", "total_service_cost"])
        and abs(numeric(r["customer_pay_amount"]) + numeric(r["warranty_pay_amount"]) - numeric(r["total_service_cost"])) > .02
        for r in tables["service_records"]
    )
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("table", nargs="?")
    parser.add_argument("--relationships", action="store_true")
    parser.add_argument("--suspicious", action="store_true")
    args = parser.parse_args()
    if args.relationships:
        result = relationship_report()
    elif args.suspicious:
        result = suspicious_report()
    elif args.table:
        result = profile(args.table)
    else:
        result = [profile(path.stem) for path in sorted(RAW.glob("*.csv"))]
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
