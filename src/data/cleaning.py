"""Deterministic, auditable cleaning pipeline for versalMotors raw CSVs.

The pipeline preserves raw values beside transformed fields, removes only exact
duplicate rows, and favors flags over destructive correction.  All mappings are
exact lookups from reviewed CSV mapping tables; no fuzzy matching is used.
"""

from __future__ import annotations

import csv
import re
import shutil
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable

from .cleaning_log import CleaningLog


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
CLEAN_DIR = ROOT / "data" / "cleaned"
LOG_PATH = ROOT / "docs" / "cleaning_log.csv"
MAPPING_DIR = ROOT / "config" / "mappings"

TABLES = [
    "branches", "models", "salespeople", "inventory", "sales",
    "service_records", "warranty_claims", "complaints", "satisfaction",
]

PRIMARY_KEYS = {
    "branches": "branch_id", "models": "model_id", "salespeople": "salesperson_id",
    "inventory": "inventory_id", "sales": "sale_id", "service_records": "service_id",
    "warranty_claims": "claim_id", "complaints": "complaint_id", "satisfaction": "survey_id",
}

DATE_COLUMNS = {
    "branches": ["opened_date"],
    "models": ["launch_date", "discontinued_date"],
    "salespeople": ["hire_date", "termination_date"],
    "inventory": ["manufacture_date", "acquisition_date", "arrival_date", "sold_date", "record_updated_at"],
    "sales": ["sale_date", "delivery_date", "created_at"],
    "service_records": ["service_open_date", "service_close_date"],
    "warranty_claims": ["claim_date", "decision_date"],
    "complaints": ["complaint_date", "resolution_date"],
    "satisfaction": ["survey_date"],
}

INTEGER_COLUMNS = {
    "branches": ["branch_id", "floor_capacity", "service_bay_count"],
    "models": ["model_id", "model_year", "seating_capacity"],
    "salespeople": ["salesperson_id", "branch_id", "experience_years_at_hire", "monthly_target_units"],
    "inventory": ["inventory_id", "model_id", "branch_id", "odometer_km", "days_in_inventory"],
    "sales": ["sale_id", "inventory_id", "branch_id", "salesperson_id", "finance_term_months"],
    "service_records": ["service_id", "inventory_id", "branch_id", "sale_id", "odometer_km"],
    "warranty_claims": ["claim_id", "service_id", "inventory_id", "sale_id", "branch_id", "days_to_resolution"],
    "complaints": ["complaint_id", "branch_id", "sale_id", "service_id", "claim_id", "days_to_resolution"],
    "satisfaction": ["survey_id", "branch_id", "sale_id", "service_id", "complaint_id", "overall_score", "nps_score", "product_score", "staff_score", "timeliness_score", "value_score"],
}

DECIMAL_COLUMNS = {
    "models": ["engine_size_l", "battery_capacity_kwh", "fuel_efficiency", "msrp"],
    "salespeople": ["commission_rate"],
    "inventory": ["acquisition_cost", "listed_price"],
    "sales": ["gross_price", "discount_amount", "net_sale_price", "tax_amount", "fees_amount", "total_sale_price", "trade_in_value"],
    "service_records": ["labor_hours", "labor_cost", "parts_cost", "misc_cost", "total_service_cost", "customer_pay_amount", "warranty_pay_amount"],
    "warranty_claims": ["claim_amount", "approved_amount", "manufacturer_recovery_amount"],
    "complaints": ["resolution_cost"],
}

AMOUNT_COLUMNS = {
    "models": ["msrp"],
    "inventory": ["acquisition_cost", "listed_price"],
    "sales": ["gross_price", "discount_amount", "net_sale_price", "tax_amount", "fees_amount", "total_sale_price", "trade_in_value"],
    "service_records": ["labor_cost", "parts_cost", "misc_cost", "total_service_cost", "customer_pay_amount", "warranty_pay_amount"],
    "warranty_claims": ["claim_amount", "approved_amount", "manufacturer_recovery_amount"],
    "complaints": ["resolution_cost"],
}

BOOLEAN_COLUMNS = {
    "branches": ["active_flag"], "models": ["active_flag"],
    "salespeople": ["active_flag"], "sales": ["trade_in_flag"],
    "service_records": ["repeat_repair_flag"],
    "warranty_claims": ["repeat_claim_flag"],
    "complaints": ["escalated_flag"], "satisfaction": ["recommend_flag"],
}

MANDATORY_FIELDS = {
    "branches": ["branch_id", "branch_code", "branch_name", "branch_type", "city", "region", "country_code", "opened_date", "active_flag"],
    "models": ["model_id", "manufacturer", "model_name", "model_year", "trim_name", "vehicle_segment", "body_style", "powertrain", "transmission", "seating_capacity", "msrp", "currency_code", "launch_date", "active_flag"],
    "salespeople": ["salesperson_id", "employee_code", "branch_id", "first_name", "last_name", "hire_date", "job_title", "monthly_target_units", "commission_rate", "active_flag"],
    "inventory": ["inventory_id", "vin", "model_id", "branch_id", "manufacture_date", "acquisition_date", "arrival_date", "condition", "acquisition_cost", "listed_price", "currency_code", "inventory_status"],
    "sales": ["sale_id", "inventory_id", "branch_id", "salesperson_id", "customer_ref", "sale_date", "sale_status", "sales_channel", "customer_type", "gross_price", "discount_amount", "net_sale_price", "tax_amount", "fees_amount", "currency_code", "payment_method", "trade_in_flag"],
    "service_records": ["service_id", "inventory_id", "branch_id", "customer_ref", "service_open_date", "service_type", "service_status", "odometer_km", "labor_hours", "labor_cost", "parts_cost", "misc_cost", "currency_code", "technician_team", "repeat_repair_flag"],
    "warranty_claims": ["claim_id", "service_id", "inventory_id", "branch_id", "claim_date", "failure_category", "claim_description", "claim_status", "currency_code", "repeat_claim_flag"],
    "complaints": ["complaint_id", "customer_ref", "branch_id", "sale_id", "complaint_date", "complaint_channel", "complaint_category", "severity", "complaint_text", "resolution_status", "currency_code", "escalated_flag"],
    "satisfaction": ["survey_id", "customer_ref", "branch_id", "survey_date", "survey_type", "overall_score", "nps_score", "staff_score", "timeliness_score", "value_score", "recommend_flag", "response_channel"],
}

FOREIGN_KEYS = [
    ("salespeople", "branch_id", "branches"),
    ("inventory", "model_id", "models"), ("inventory", "branch_id", "branches"),
    ("sales", "inventory_id", "inventory"), ("sales", "branch_id", "branches"), ("sales", "salesperson_id", "salespeople"),
    ("service_records", "inventory_id", "inventory"), ("service_records", "branch_id", "branches"), ("service_records", "sale_id", "sales"),
    ("warranty_claims", "service_id", "service_records"), ("warranty_claims", "inventory_id", "inventory"), ("warranty_claims", "sale_id", "sales"), ("warranty_claims", "branch_id", "branches"),
    ("complaints", "branch_id", "branches"), ("complaints", "sale_id", "sales"), ("complaints", "service_id", "service_records"), ("complaints", "claim_id", "warranty_claims"),
    ("satisfaction", "branch_id", "branches"), ("satisfaction", "sale_id", "sales"), ("satisfaction", "service_id", "service_records"), ("satisfaction", "complaint_id", "complaints"),
]

MONEY_TOLERANCE = 0.02
VIN_PATTERN = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")


def _is_missing(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _as_date(value: Any) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _sum_if_complete(row: dict[str, Any], columns: Iterable[str]) -> float | None:
    values = [row.get(column) for column in columns]
    if any(value is None for value in values):
        return None
    return round(sum(float(value) for value in values), 2)


class CleaningPipeline:
    """Clean all raw tables and write audited CSV outputs."""

    def __init__(
        self,
        raw_dir: Path = RAW_DIR,
        clean_dir: Path = CLEAN_DIR,
        log_path: Path = LOG_PATH,
        mapping_dir: Path = MAPPING_DIR,
    ) -> None:
        self.raw_dir = raw_dir
        self.clean_dir = clean_dir
        self.log_path = log_path
        self.mapping_dir = mapping_dir
        self.log = CleaningLog()
        self.tables: dict[str, list[dict[str, Any]]] = {}
        self.source_fields: dict[str, list[str]] = {}
        self.branch_map = self._load_two_column_mapping("branch_names.csv")
        self.model_map = self._load_two_column_mapping("model_names.csv")
        self.category_maps = self._load_category_mappings()

    def _load_two_column_mapping(self, filename: str) -> dict[str, str]:
        mapping: dict[str, str] = {}
        with (self.mapping_dir / filename).open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                if row["review_status"] == "approved":
                    mapping[row["raw_value"]] = row["canonical_value"]
        return mapping

    def _load_category_mappings(self) -> dict[tuple[str, str], dict[str, str]]:
        mappings: dict[tuple[str, str], dict[str, str]] = defaultdict(dict)
        with (self.mapping_dir / "categories.csv").open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                if row["review_status"] == "approved":
                    mappings[(row["table"], row["column"])][row["raw_value"]] = row["canonical_value"]
        return dict(mappings)

    def _load_table(self, table: str) -> list[dict[str, Any]]:
        with (self.raw_dir / f"{table}.csv").open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            self.source_fields[table] = list(reader.fieldnames or [])
            rows = []
            for source_row_number, row in enumerate(reader, start=2):
                clean_row: dict[str, Any] = dict(row)
                clean_row["_source_file"] = f"{table}.csv"
                clean_row["_source_row_number"] = source_row_number
                rows.append(clean_row)
        self.log.append(step="load_raw", table=table, rows_affected=len(rows), reason="Load source without type coercion", action_taken="loaded_all_columns_as_text_and_added_source_metadata")
        return rows

    def _remove_exact_duplicates(self, table: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        fields = self.source_fields[table]
        seen: set[tuple[str, ...]] = set()
        output = []
        removed = 0
        for row in rows:
            signature = tuple(row.get(field, "") for field in fields)
            if signature in seen:
                removed += 1
                continue
            seen.add(signature)
            output.append(row)
        self.log.append(step="remove_exact_duplicates", table=table, rows_affected=removed, reason="Exact byte-equivalent business rows are redundant", action_taken="kept_first_physical_source_row_removed_later_exact_matches")
        return output

    def _normalize_blanks(self, table: str, rows: list[dict[str, Any]]) -> None:
        affected = 0
        for row in rows:
            changed = False
            for field in self.source_fields[table]:
                if isinstance(row.get(field), str) and row[field] == "":
                    row[field] = None
                    changed = True
            affected += changed
        self.log.append(step="normalize_blank_nulls", table=table, rows_affected=affected, reason="Blank CSV fields represent missing values", action_taken="converted_empty_strings_to_null")

    def _apply_exact_mapping(self, table: str, rows: list[dict[str, Any]], column: str, mapping: dict[str, str], label: str) -> None:
        affected = 0
        for row in rows:
            raw = row.get(column)
            row[f"{column}_raw"] = raw
            if raw is None:
                row[column] = None
                row[f"{column}_unmapped_flag"] = False
                continue
            canonical = mapping.get(str(raw))
            row[column] = canonical
            row[f"{column}_unmapped_flag"] = canonical is None
            if canonical != raw:
                affected += 1
        self.log.append(step=f"map_{label}", table=table, rows_affected=affected, reason="Use reviewed exact mappings without fuzzy guessing", action_taken="set_approved_canonical_value_else_null_preserved_raw_and_flagged")

    def _apply_mappings(self, table: str, rows: list[dict[str, Any]]) -> None:
        if table == "branches":
            self._apply_exact_mapping(table, rows, "branch_name", self.branch_map, "branch_name")
        if table == "models":
            self._apply_exact_mapping(table, rows, "model_name", self.model_map, "model_name")
        for (mapped_table, column), mapping in self.category_maps.items():
            if mapped_table == table:
                self._apply_exact_mapping(table, rows, column, mapping, column)

    @staticmethod
    def _parse_date_value(raw: Any, is_datetime: bool) -> tuple[str | None, bool, bool]:
        if raw is None:
            return None, False, False
        value = str(raw).strip()
        ddmmyyyy = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", value)
        if ddmmyyyy:
            day, month, year = map(int, ddmmyyyy.groups())
            ambiguous = day <= 12 and month <= 12
            try:
                parsed = date(year, month, day)
                return parsed.isoformat(), False, ambiguous
            except ValueError:
                return None, True, ambiguous
        try:
            if is_datetime:
                parsed_datetime = datetime.fromisoformat(value)
                return parsed_datetime.isoformat(timespec="seconds"), False, False
            parsed = date.fromisoformat(value)
            return parsed.isoformat(), False, False
        except ValueError:
            return None, True, False

    def _parse_dates(self, table: str, rows: list[dict[str, Any]]) -> None:
        invalid_rows: set[int] = set()
        ambiguous_rows: set[int] = set()
        future_rows: set[int] = set()
        for row in rows:
            for column in DATE_COLUMNS.get(table, []):
                raw = row.get(column)
                row[f"{column}_raw"] = raw
                parsed, invalid, ambiguous = self._parse_date_value(raw, column.endswith("_at"))
                row[column] = parsed
                row[f"{column}_invalid_flag"] = invalid
                row[f"{column}_ambiguous_flag"] = ambiguous
                parsed_date = _as_date(parsed)
                row[f"{column}_future_flag"] = bool(parsed_date and parsed_date > date.today())
                if invalid:
                    invalid_rows.add(id(row))
                if ambiguous:
                    ambiguous_rows.add(id(row))
                if row[f"{column}_future_flag"]:
                    future_rows.add(id(row))
        self.log.append(step="parse_dates", table=table, rows_affected=len(invalid_rows | ambiguous_rows | future_rows), reason="DD/MM/YYYY is primary; invalid, ambiguous, and future dates require explicit flags", action_taken=f"parsed_dd_mm_primary_and_iso_fallback_invalid_to_null; invalid_rows={len(invalid_rows)}; ambiguous_rows={len(ambiguous_rows)}; future_rows={len(future_rows)}")

    def _parse_numbers(self, table: str, rows: list[dict[str, Any]]) -> None:
        parse_errors: set[int] = set()
        negative_amounts: set[int] = set()
        missing_amounts: set[int] = set()
        integer_fields = set(INTEGER_COLUMNS.get(table, []))
        decimal_fields = set(DECIMAL_COLUMNS.get(table, []))
        amount_fields = set(AMOUNT_COLUMNS.get(table, []))
        for row in rows:
            for column in integer_fields | decimal_fields:
                raw = row.get(column)
                row[f"{column}_raw"] = raw
                missing = raw is None
                if column in amount_fields:
                    row[f"{column}_missing_flag"] = missing
                    if missing:
                        missing_amounts.add(id(row))
                if missing:
                    row[column] = None
                    row[f"{column}_parse_error_flag"] = False
                    if column in amount_fields:
                        row[f"{column}_negative_flag"] = False
                    continue
                try:
                    parsed: int | float = int(str(raw)) if column in integer_fields else float(str(raw))
                    row[f"{column}_parse_error_flag"] = False
                except (TypeError, ValueError):
                    row[column] = None
                    row[f"{column}_parse_error_flag"] = True
                    if column in amount_fields:
                        row[f"{column}_negative_flag"] = False
                    parse_errors.add(id(row))
                    continue
                if column in amount_fields and parsed < 0:
                    row[column] = None
                    row[f"{column}_negative_flag"] = True
                    negative_amounts.add(id(row))
                else:
                    row[column] = parsed
                    if column in amount_fields:
                        row[f"{column}_negative_flag"] = False
        self.log.append(step="parse_numeric_fields", table=table, rows_affected=len(parse_errors), reason="Invalid numeric text cannot be analyzed safely", action_taken="parsed_nullable_numeric_invalid_to_null_and_flagged")
        self.log.append(step="flag_negative_amounts", table=table, rows_affected=len(negative_amounts), reason="Approved decision: negative monetary values are errors, not credits", action_taken="set_clean_amount_to_null_preserved_raw_and_flagged")
        self.log.append(step="flag_missing_amounts", table=table, rows_affected=len(missing_amounts), reason="Approved decision: missing amounts remain null", action_taken="retained_null_added_missing_flag_no_statistical_imputation")

    def _parse_booleans(self, table: str, rows: list[dict[str, Any]]) -> None:
        affected = 0
        for row in rows:
            for column in BOOLEAN_COLUMNS.get(table, []):
                raw = row.get(column)
                row[f"{column}_raw"] = raw
                if raw is None:
                    row[column] = None
                    row[f"{column}_parse_error_flag"] = False
                    continue
                normalized = str(raw).strip().lower()
                if normalized in {"true", "false"}:
                    parsed = normalized == "true"
                    affected += parsed != raw
                    row[column] = parsed
                    row[f"{column}_parse_error_flag"] = False
                else:
                    row[column] = None
                    row[f"{column}_parse_error_flag"] = True
                    affected += 1
        self.log.append(step="parse_boolean_fields", table=table, rows_affected=affected, reason="Boolean variants require consistent typed values", action_taken="trimmed_and_parsed_true_false_invalid_to_null_and_flagged")

    def _validate_mandatory(self, table: str, rows: list[dict[str, Any]]) -> None:
        affected = 0
        for row in rows:
            missing = [field for field in MANDATORY_FIELDS[table] if _is_missing(row.get(field))]
            row["_missing_required_fields_flag"] = bool(missing)
            row["_missing_required_fields"] = "|".join(missing) if missing else None
            affected += bool(missing)
        self.log.append(step="validate_mandatory_fields", table=table, rows_affected=affected, reason="Approved mandatory-field definitions must be visible", action_taken="retained_rows_and_added_missing_required_fields_flag")

    def _clean_vins(self) -> None:
        rows = self.tables["inventory"]
        invalid = 0
        missing = 0
        for row in rows:
            raw = row.get("vin")
            row["vin_raw"] = raw
            if raw is None:
                row["vin"] = None
                row["vin_missing_flag"] = True
                row["vin_invalid_flag"] = False
                missing += 1
                continue
            canonical = str(raw).strip().upper()
            valid = bool(VIN_PATTERN.fullmatch(canonical))
            row["vin"] = canonical if valid else None
            row["vin_missing_flag"] = False
            row["vin_invalid_flag"] = not valid
            invalid += not valid
        counts: dict[str, int] = defaultdict(int)
        for row in rows:
            if row.get("vin"):
                counts[row["vin"]] += 1
        duplicate_rows = 0
        for row in rows:
            row["vin_duplicate_flag"] = bool(row.get("vin") and counts[row["vin"]] > 1)
            duplicate_rows += row["vin_duplicate_flag"]
        self.log.append(step="validate_vin", table="inventory", rows_affected=invalid + missing, reason="VIN must be a valid unique 17-character identifier", action_taken=f"uppercased_valid_vins_invalid_to_null_preserved_raw_and_flagged; missing={missing}; invalid={invalid}")
        self.log.append(step="flag_duplicate_vin", table="inventory", rows_affected=duplicate_rows, reason="Duplicate valid VINs need source review", action_taken="retained_all_rows_and_flagged_duplicate_valid_vins")

    def _validate_scores(self) -> None:
        rows = self.tables["satisfaction"]
        fields = ["overall_score", "nps_score", "product_score", "staff_score", "timeliness_score", "value_score"]
        affected: set[int] = set()
        for row in rows:
            for field in fields:
                value = row.get(field)
                invalid = value is not None and not 1 <= value <= 5
                row[f"{field}_out_of_range_flag"] = invalid
                if invalid:
                    row[field] = None
                    affected.add(id(row))
            product_required = row.get("survey_type") == "post_sale"
            row["product_score_required_missing_flag"] = product_required and row.get("product_score") is None
            row["product_score_not_applicable_flag"] = not product_required and row.get("product_score") is not None
        self.log.append(step="validate_satisfaction_scores", table="satisfaction", rows_affected=len(affected), reason="Approved score scale is 1 through 5", action_taken="out_of_range_clean_scores_to_null_preserved_raw_and_flagged")

    def _validate_numeric_thresholds(self) -> None:
        rows = self.tables["service_records"]
        affected = 0
        for row in rows:
            odometer = row.get("odometer_km")
            negative = odometer is not None and odometer < 0
            row["odometer_km_negative_flag"] = negative
            if negative:
                row["odometer_km"] = None
            labor = row.get("labor_hours")
            row["labor_hours_over_80_flag"] = labor is not None and labor > 80
            row["mileage_over_600000_flag"] = odometer is not None and odometer > 600_000
            affected += negative or row["labor_hours_over_80_flag"] or row["mileage_over_600000_flag"]
        self.log.append(step="validate_service_thresholds", table="service_records", rows_affected=affected, reason="Approved thresholds: negative odometer invalid, labor over 80h and mileage over 600k questionable", action_taken="negative_odometer_to_null; retained_high_values_and_flagged")

    def _calculate_financial_companions(self) -> None:
        sales_affected = 0
        for row in self.tables["sales"]:
            net_calc = _sum_if_complete(row, ["gross_price", "discount_amount"])
            if net_calc is not None:
                net_calc = round(float(row["gross_price"]) - float(row["discount_amount"]), 2)
            row["net_sale_price_calculated"] = net_calc
            row["net_sale_price_mismatch_flag"] = row.get("net_sale_price") is not None and net_calc is not None and abs(row["net_sale_price"] - net_calc) > MONEY_TOLERANCE
            total_calc = _sum_if_complete(row, ["net_sale_price", "tax_amount", "fees_amount"])
            row["total_sale_price_calculated"] = total_calc
            row["total_sale_price_mismatch_flag"] = row.get("total_sale_price") is not None and total_calc is not None and abs(row["total_sale_price"] - total_calc) > MONEY_TOLERANCE
            sales_affected += row["net_sale_price_mismatch_flag"] or row["total_sale_price_mismatch_flag"] or row.get("total_sale_price") is None
        self.log.append(step="calculate_sales_amounts", table="sales", rows_affected=sales_affected, reason="Missing totals stay null and GHS 0.02 is the approved reconciliation tolerance", action_taken="created_calculated_companions_preserved_source_amounts_and_flagged_mismatches")

        service_affected = 0
        for row in self.tables["service_records"]:
            total_calc = _sum_if_complete(row, ["labor_cost", "parts_cost", "misc_cost"])
            pay_calc = _sum_if_complete(row, ["customer_pay_amount", "warranty_pay_amount"])
            row["total_service_cost_calculated"] = total_calc
            row["service_component_total_mismatch_flag"] = row.get("total_service_cost") is not None and total_calc is not None and abs(row["total_service_cost"] - total_calc) > MONEY_TOLERANCE
            row["service_payment_total_mismatch_flag"] = row.get("total_service_cost") is not None and pay_calc is not None and abs(row["total_service_cost"] - pay_calc) > MONEY_TOLERANCE
            service_affected += row["service_component_total_mismatch_flag"] or row["service_payment_total_mismatch_flag"] or row.get("total_service_cost") is None
        self.log.append(step="calculate_service_amounts", table="service_records", rows_affected=service_affected, reason="Missing totals stay null and GHS 0.02 is the approved reconciliation tolerance", action_taken="created_calculated_companions_preserved_source_amounts_and_flagged_mismatches")

    def _validate_conditional_fields(self) -> None:
        affected = 0
        for row in self.tables["sales"]:
            method = row.get("payment_method")
            term = row.get("finance_term_months")
            row["finance_term_required_missing_flag"] = method == "finance" and term is None
            row["finance_term_not_applicable_flag"] = method == "cash" and term is not None
            row["trade_in_value_mismatch_flag"] = bool(row.get("trade_in_flag")) != (row.get("trade_in_value") is not None)
            affected += any((row["finance_term_required_missing_flag"], row["finance_term_not_applicable_flag"], row["trade_in_value_mismatch_flag"]))
        self.log.append(step="validate_sales_conditional_fields", table="sales", rows_affected=affected, reason="Finance terms are required for finance, allowed for lease, and not applicable to cash", action_taken="retained_values_and_added_conditional_flags")

        model_affected = 0
        for row in self.tables["models"]:
            is_ev = row.get("powertrain") == "EV"
            row["fuel_efficiency_unit"] = "kWh/100km" if is_ev else "L/100km"
            row["fuel_efficiency_lower_is_better"] = True
            row["ev_engine_size_contradiction_flag"] = is_ev and row.get("engine_size_l") is not None
            row["non_ev_battery_contradiction_flag"] = not is_ev and row.get("battery_capacity_kwh") is not None
            row["inactive_without_discontinued_date_flag"] = row.get("active_flag") is False and row.get("discontinued_date") is None
            model_affected += any((row["ev_engine_size_contradiction_flag"], row["non_ev_battery_contradiction_flag"], row["inactive_without_discontinued_date_flag"]))
        self.log.append(step="validate_model_conditional_fields", table="models", rows_affected=model_affected, reason="Fuel units and model status rules require explicit interpretation", action_taken="assigned_powertrain_specific_efficiency_unit_and_flagged_contradictions")

    def _validate_chronology(self) -> None:
        inventory_by_id = {row.get("inventory_id"): row for row in self.tables["inventory"]}
        service_by_id = {row.get("service_id"): row for row in self.tables["service_records"]}
        sale_by_id = {row.get("sale_id"): row for row in self.tables["sales"]}
        complaint_by_id = {row.get("complaint_id"): row for row in self.tables["complaints"]}

        pre_2023 = 0
        affected = 0
        returned_inventory = {row.get("inventory_id") for row in self.tables["sales"] if row.get("sale_status") == "returned"}
        for row in self.tables["sales"]:
            sale_date = _as_date(row.get("sale_date")); delivery = _as_date(row.get("delivery_date"))
            inventory = inventory_by_id.get(row.get("inventory_id"), {})
            arrival = _as_date(inventory.get("arrival_date"))
            acquisition = _as_date(inventory.get("acquisition_date"))
            row["sale_before_arrival_flag"] = bool(sale_date and arrival and sale_date < arrival)
            row["sale_before_acquisition_flag"] = bool(sale_date and acquisition and sale_date < acquisition)
            row["delivery_before_sale_flag"] = bool(delivery and sale_date and delivery < sale_date)
            row["authoritative_event_date"] = row.get("delivery_date") if row.get("sale_status") == "completed" and delivery else row.get("sale_date")
            pre_2023 += bool(sale_date and sale_date < date(2023, 1, 1))
            affected += row["sale_before_arrival_flag"] or row["sale_before_acquisition_flag"] or row["delivery_before_sale_flag"]
        self.log.append(step="validate_sales_chronology", table="sales", rows_affected=affected, reason="Completed-date hierarchy is authoritative while contradictions remain reviewable", action_taken="retained_dates_added_chronology_flags_and_authoritative_companion")
        self.log.append(step="retain_pre_2023_lead_in", table="sales", rows_affected=pre_2023, reason="Approved decision: pre-2023 records are valid lead-in history", action_taken="retained_without_error_flag")

        inventory_affected = 0
        for row in self.tables["inventory"]:
            legitimate_return = row.get("inventory_id") in returned_inventory
            row["available_with_sold_date_contradiction_flag"] = row.get("inventory_status") == "available" and row.get("sold_date") is not None and not legitimate_return
            row["returned_vehicle_available_flag"] = row.get("inventory_status") == "available" and row.get("sold_date") is not None and legitimate_return
            inventory_affected += row["available_with_sold_date_contradiction_flag"]
        self.log.append(step="validate_inventory_status_dates", table="inventory", rows_affected=inventory_affected, reason="Returned vehicles may legitimately be available with a sold date", action_taken="retained_rows_and_flagged_only_non_return_contradictions")

        service_affected = 0
        for row in self.tables["service_records"]:
            opened = _as_date(row.get("service_open_date")); closed = _as_date(row.get("service_close_date"))
            row["service_close_before_open_flag"] = bool(opened and closed and closed < opened)
            row["completed_service_missing_close_flag"] = row.get("service_status") == "completed" and closed is None
            row["authoritative_event_date"] = row.get("service_close_date") if row.get("service_status") == "completed" and closed else row.get("service_open_date")
            row["days_to_resolution_calculated"] = (closed - opened).days if opened and closed and closed >= opened else None
            service_affected += row["service_close_before_open_flag"] or row["completed_service_missing_close_flag"]
        self.log.append(step="validate_service_chronology", table="service_records", rows_affected=service_affected, reason="Completed service date is authoritative and calculated duration is a companion", action_taken="retained_source_dates_added_flags_authoritative_date_and_calculated_duration")

        claim_affected = 0; claim_pre_2023 = 0
        for row in self.tables["warranty_claims"]:
            claim = _as_date(row.get("claim_date")); decision = _as_date(row.get("decision_date"))
            opened = _as_date(service_by_id.get(row.get("service_id"), {}).get("service_open_date"))
            sale_date = _as_date(sale_by_id.get(row.get("sale_id"), {}).get("sale_date"))
            row["claim_before_service_flag"] = bool(claim and opened and claim < opened)
            row["claim_before_sale_flag"] = bool(claim and sale_date and claim < sale_date)
            row["approved_claim_missing_decision_flag"] = row.get("claim_status") == "approved" and decision is None
            row["authoritative_event_date"] = row.get("decision_date") if decision else row.get("claim_date")
            row["days_to_resolution_calculated"] = (decision - claim).days if claim and decision and decision >= claim else None
            claim_pre_2023 += bool(claim and claim < date(2023, 1, 1))
            claim_affected += row["claim_before_service_flag"] or row["claim_before_sale_flag"] or row["approved_claim_missing_decision_flag"]
        self.log.append(step="validate_claim_chronology", table="warranty_claims", rows_affected=claim_affected, reason="Completed decision date is authoritative and one service may have multiple claims", action_taken="retained_claims_added_flags_authoritative_date_and_calculated_duration")
        self.log.append(step="retain_pre_2023_lead_in", table="warranty_claims", rows_affected=claim_pre_2023, reason="Approved decision: pre-2023 records are valid lead-in history", action_taken="retained_without_error_flag")

        complaint_affected = 0
        for row in self.tables["complaints"]:
            opened = _as_date(row.get("complaint_date")); resolved = _as_date(row.get("resolution_date"))
            row["resolution_before_complaint_flag"] = bool(opened and resolved and resolved < opened)
            row["resolved_complaint_missing_date_flag"] = row.get("resolution_status") == "resolved" and resolved is None
            row["authoritative_event_date"] = row.get("resolution_date") if resolved else row.get("complaint_date")
            row["days_to_resolution_calculated"] = (resolved - opened).days if opened and resolved and resolved >= opened else None
            complaint_affected += row["resolution_before_complaint_flag"] or row["resolved_complaint_missing_date_flag"]
        self.log.append(step="validate_complaint_chronology", table="complaints", rows_affected=complaint_affected, reason="Completed resolution date is authoritative and calculated duration is a companion", action_taken="retained_source_dates_added_flags_authoritative_date_and_calculated_duration")

        survey_affected = 0
        for row in self.tables["satisfaction"]:
            survey = _as_date(row.get("survey_date")); source = None
            if row.get("survey_type") == "post_sale": source = _as_date(sale_by_id.get(row.get("sale_id"), {}).get("sale_date"))
            elif row.get("survey_type") == "post_service": source = _as_date(service_by_id.get(row.get("service_id"), {}).get("service_open_date"))
            elif row.get("survey_type") == "complaint_follow_up": source = _as_date(complaint_by_id.get(row.get("complaint_id"), {}).get("complaint_date"))
            row["survey_before_source_event_flag"] = bool(survey and source and survey < source)
            survey_affected += row["survey_before_source_event_flag"]
        self.log.append(step="validate_survey_chronology", table="satisfaction", rows_affected=survey_affected, reason="Survey should not precede its source interaction", action_taken="retained_rows_and_flagged_chronology_conflicts")

    def _flag_near_duplicates(self) -> None:
        inventory_by_id = {row.get("inventory_id"): row for row in self.tables["inventory"]}
        sale_by_id = {row.get("sale_id"): row for row in self.tables["sales"]}
        specs = {
            "sales": ("sale_date", "total_sale_price"),
            "service_records": ("service_open_date", "total_service_cost"),
            "warranty_claims": ("claim_date", "claim_amount"),
            "complaints": ("complaint_date", "resolution_cost"),
        }
        for table, (date_field, amount_field) in specs.items():
            rows = self.tables[table]
            candidates: list[tuple[int, str, Any, date, float]] = []
            for index, row in enumerate(rows):
                inventory_id = row.get("inventory_id")
                if inventory_id is None and table == "complaints":
                    inventory_id = sale_by_id.get(row.get("sale_id"), {}).get("inventory_id")
                vin = inventory_by_id.get(inventory_id, {}).get("vin")
                event_date = _as_date(row.get(date_field)); amount = row.get(amount_field)
                if vin and row.get("branch_id") is not None and event_date and amount is not None:
                    candidates.append((index, vin, row.get("branch_id"), event_date, float(amount)))
                row["_possible_near_duplicate_flag"] = False
                row["_near_duplicate_group_id"] = None
            parent = list(range(len(rows)))
            def find(value: int) -> int:
                while parent[value] != value:
                    parent[value] = parent[parent[value]]; value = parent[value]
                return value
            def union(left: int, right: int) -> None:
                left_root, right_root = find(left), find(right)
                if left_root != right_root: parent[right_root] = left_root
            grouped: dict[tuple[str, Any], list[tuple[int, date, float]]] = defaultdict(list)
            for index, vin, branch, event_date, amount in candidates:
                grouped[(vin, branch)].append((index, event_date, amount))
            for group in grouped.values():
                group.sort(key=lambda item: item[1])
                for left_pos, (left_index, left_date, left_amount) in enumerate(group):
                    for right_index, right_date, right_amount in group[left_pos + 1:]:
                        day_gap = (right_date - left_date).days
                        if day_gap > 1: break
                        if abs(right_amount - left_amount) <= MONEY_TOLERANCE:
                            union(left_index, right_index)
            components: dict[int, list[int]] = defaultdict(list)
            for index, *_ in candidates: components[find(index)].append(index)
            duplicate_groups = [members for members in components.values() if len(members) > 1]
            for group_number, members in enumerate(duplicate_groups, 1):
                group_id = f"{table}-near-{group_number:05d}"
                for index in members:
                    rows[index]["_possible_near_duplicate_flag"] = True
                    rows[index]["_near_duplicate_group_id"] = group_id
            flagged = sum(len(members) for members in duplicate_groups)
            self.log.append(step="flag_near_duplicates", table=table, rows_affected=flagged, reason="Approved candidate rule: same VIN and branch, date within one day, amount within GHS 0.02", action_taken="retained_rows_and_assigned_near_duplicate_group_id")

    def _validate_completed_sales_per_vin(self) -> None:
        inventory_by_id = {row.get("inventory_id"): row for row in self.tables["inventory"]}
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in self.tables["sales"]:
            vin = inventory_by_id.get(row.get("inventory_id"), {}).get("vin")
            if vin and row.get("sale_status") == "completed": groups[vin].append(row)
        affected = 0
        for row in self.tables["sales"]:
            vin = inventory_by_id.get(row.get("inventory_id"), {}).get("vin")
            row["multiple_completed_sale_per_vin_flag"] = bool(vin and len(groups[vin]) > 1)
            affected += row["multiple_completed_sale_per_vin_flag"]
        self.log.append(step="validate_one_completed_sale_per_vin", table="sales", rows_affected=affected, reason="Approved business rule: one completed sale per VIN", action_taken="retained_questionable_rows_and_flagged_all_conflicting_sales")

    def _validate_foreign_keys(self) -> None:
        parent_keys = {table: {row.get(pk) for row in self.tables[table] if row.get(pk) is not None} for table, pk in PRIMARY_KEYS.items()}
        for child, field, parent in FOREIGN_KEYS:
            affected = 0
            for row in self.tables[child]:
                value = row.get(field)
                row.setdefault(f"{field}_raw", value)
                orphan = value is not None and value not in parent_keys[parent]
                row[f"{field}_orphan_flag"] = orphan
                if orphan:
                    row[field] = None
                    affected += 1
            self.log.append(step="validate_foreign_key", table=child, rows_affected=affected, reason=f"{field} must resolve to {parent}.{PRIMARY_KEYS[parent]}; no unknown member is allowed", action_taken=f"orphan_{field}_to_null_preserved_raw_and_flagged")

        external = 0
        for row in self.tables["service_records"]:
            row["external_service_record_flag"] = row.get("sale_id") is None and not row.get("sale_id_orphan_flag", False)
            external += row["external_service_record_flag"]
        self.log.append(step="identify_external_service", table="service_records", rows_affected=external, reason="Approved decision: external service records are valid", action_taken="retained_and_marked_informational_not_error")

    def _assign_quality_status(self) -> None:
        source_boolean_fields = {field for fields in BOOLEAN_COLUMNS.values() for field in fields}
        error_markers = (
            "invalid_flag", "parse_error_flag", "negative_flag", "orphan_flag",
            "out_of_range_flag", "missing_required_fields_flag", "unmapped_flag",
            "multiple_completed_sale_per_vin_flag",
        )
        informational = {"external_service_record_flag", "returned_vehicle_available_flag", "fuel_efficiency_lower_is_better"}
        for table, rows in self.tables.items():
            errors = warnings = 0
            for row in rows:
                flags = [key for key, value in row.items() if key.endswith("_flag") and key not in source_boolean_fields and key not in informational and value is True]
                error_flags = [flag for flag in flags if any(marker in flag for marker in error_markers)]
                row["_quality_issue_count"] = len(flags)
                if error_flags:
                    row["_row_quality_status"] = "ERROR"; errors += 1
                elif flags:
                    row["_row_quality_status"] = "WARNING"; warnings += 1
                else:
                    row["_row_quality_status"] = "VALID"
            self.log.append(step="assign_row_quality_status", table=table, rows_affected=errors + warnings, reason="Approved severity precedence is ERROR > WARNING > VALID with independent flags", action_taken=f"assigned_status_from_independent_flags; errors={errors}; warnings={warnings}")

    def _write_cleaned_tables(self) -> None:
        resolved_clean_dir = self.clean_dir.resolve()
        resolved_root = ROOT.resolve()
        if not resolved_clean_dir.is_relative_to(resolved_root) or resolved_clean_dir.name != "cleaned":
            raise RuntimeError(f"Refusing to replace unsafe cleaned-output path: {resolved_clean_dir}")
        if self.clean_dir.exists():
            shutil.rmtree(self.clean_dir)
        self.clean_dir.mkdir(parents=True, exist_ok=True)
        for table, rows in self.tables.items():
            fields: list[str] = []
            for row in rows:
                for field in row:
                    if field not in fields: fields.append(field)
            path = self.clean_dir / f"{table}.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
                writer.writeheader(); writer.writerows(rows)
            self.log.append(step="write_cleaned_table", table=table, rows_affected=len(rows), reason="Publish auditable cleaned output", action_taken=f"wrote_{path.as_posix()}")

    def run(self) -> dict[str, list[dict[str, Any]]]:
        for table in TABLES:
            rows = self._load_table(table)
            rows = self._remove_exact_duplicates(table, rows)
            self._normalize_blanks(table, rows)
            self._apply_mappings(table, rows)
            self._parse_dates(table, rows)
            self._parse_numbers(table, rows)
            self._parse_booleans(table, rows)
            self._validate_mandatory(table, rows)
            self.tables[table] = rows
        self._clean_vins()
        self._validate_scores()
        self._validate_numeric_thresholds()
        self._calculate_financial_companions()
        self._validate_conditional_fields()
        self._validate_chronology()
        self._flag_near_duplicates()
        self._validate_completed_sales_per_vin()
        self._validate_foreign_keys()
        self._assign_quality_status()
        self._write_cleaned_tables()
        self.log.write(self.log_path)
        return self.tables


def clean_all() -> dict[str, list[dict[str, Any]]]:
    """Run the complete cleaning pipeline with repository-default paths."""
    return CleaningPipeline().run()
