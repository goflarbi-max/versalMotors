"""Pure pandas metric functions for the versalMotors analytical layer.

No function reads files, opens a database, mutates an input DataFrame, or imports
UI code. Callers supply an :class:`AnalyticsData` bundle and a :class:`Filters`
value. Every public function returns a newly allocated pandas DataFrame.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Iterable, Literal

import pandas as pd


Period = Literal["D", "W", "M", "Q", "Y"]


def _missing_columns(frame: pd.DataFrame, required: Iterable[str]) -> bool:
    """Return True when a degraded source cannot support a metric formula."""
    return not set(required).issubset(frame.columns)


@dataclass(frozen=True)
class Filters:
    """Immutable dashboard-independent filter specification.

    Each dimensional field accepts one or more exact values. IDs and names are
    both supported where the relevant dimension provides them. Empty tuples mean
    "all values." Dates are inclusive. ``period`` controls result aggregation and
    defaults to calendar month.
    """

    start_date: date | str | pd.Timestamp | None = None
    end_date: date | str | pd.Timestamp | None = None
    branch: tuple[str | int, ...] = field(default_factory=tuple)
    model: tuple[str | int, ...] = field(default_factory=tuple)
    brand: tuple[str, ...] = field(default_factory=tuple)
    salesperson: tuple[str | int, ...] = field(default_factory=tuple)
    status: tuple[str, ...] = field(default_factory=tuple)
    period: Period = "M"


@dataclass(frozen=True)
class AnalyticsData:
    """In-memory cleaned tables required by the metric functions."""

    branches: pd.DataFrame
    models: pd.DataFrame
    salespeople: pd.DataFrame
    inventory: pd.DataFrame
    sales: pd.DataFrame
    service_records: pd.DataFrame
    warranty_claims: pd.DataFrame
    complaints: pd.DataFrame
    satisfaction: pd.DataFrame


def _values(value: Any) -> tuple[Any, ...]:
    if value is None:
        return ()
    if isinstance(value, tuple):
        return value
    if isinstance(value, (list, set, frozenset)):
        return tuple(value)
    return (value,)


def _normalized(values: Iterable[Any]) -> set[str]:
    return {str(value).strip().casefold() for value in values if value is not None}


def _exact_match(frame: pd.DataFrame, columns: list[str], selected: Iterable[Any]) -> pd.Series:
    wanted = _normalized(selected)
    result = pd.Series(False, index=frame.index)
    if not wanted:
        return ~result
    for column in columns:
        if column in frame.columns:
            result |= frame[column].astype("string").str.strip().str.casefold().isin(wanted).fillna(False)
    return result


def _valid_fact(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy(deep=True)
    if "_row_quality_status" in result.columns:
        result = result[result["_row_quality_status"].astype("string").str.upper() != "ERROR"]
    return result.copy()


def _dimension_subset(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    available = [column for column in columns if column in frame.columns]
    return frame.loc[:, available].drop_duplicates(available[0]).copy() if available else pd.DataFrame()


def _add_dimensions(
    frame: pd.DataFrame,
    data: AnalyticsData,
    *,
    resolve_salesperson_from_sale: bool = False,
) -> pd.DataFrame:
    """Return a copy enriched with inventory, model, branch, and salesperson labels."""
    result = frame.copy(deep=True)

    if resolve_salesperson_from_sale and "sale_id" in result.columns and "salesperson_id" not in result.columns:
        sales_lookup = _dimension_subset(data.sales, ["sale_id", "salesperson_id", "inventory_id"])
        if not sales_lookup.empty:
            result = result.merge(sales_lookup, on="sale_id", how="left", suffixes=("", "_from_sale"))
            if "inventory_id_from_sale" in result.columns:
                if "inventory_id" in result.columns:
                    result["inventory_id"] = result["inventory_id"].combine_first(result["inventory_id_from_sale"])
                else:
                    result["inventory_id"] = result["inventory_id_from_sale"]

    if "inventory_id" in result.columns:
        inventory = _dimension_subset(
            data.inventory,
            [
                "inventory_id", "vin", "model_id", "acquisition_cost", "arrival_date",
                "sold_date", "inventory_status", "_row_quality_status",
                "model_id_orphan_flag",
            ],
        )
        inventory = inventory.rename(columns={"_row_quality_status": "inventory_row_quality_status"})
        result = result.merge(inventory, on="inventory_id", how="left", suffixes=("", "_inventory"))
        if "model_id_orphan_flag" in result.columns:
            result = result[result["model_id_orphan_flag"] != True]
        if "model_id_inventory" in result.columns:
            result["model_id"] = result.get("model_id", pd.Series(index=result.index, dtype="float64")).combine_first(result["model_id_inventory"])

    if "model_id" in result.columns:
        models = _dimension_subset(
            data.models,
            ["model_id", "model_name", "model_name_raw", "manufacturer", "model_year", "trim_name", "_row_quality_status"],
        )
        models = models.rename(columns={"_row_quality_status": "model_row_quality_status"})
        result = result.merge(models, on="model_id", how="left", suffixes=("", "_model"))
        if "model_name" in result.columns:
            raw_model = result["model_name_raw"] if "model_name_raw" in result.columns else pd.Series(pd.NA, index=result.index, dtype="string")
            result["model_display"] = result["model_name"].combine_first(raw_model)

    if "branch_id" in result.columns:
        branches = _dimension_subset(
            data.branches,
            ["branch_id", "branch_code", "branch_name", "branch_name_raw", "city", "region", "_row_quality_status"],
        )
        branches = branches.rename(columns={"_row_quality_status": "branch_row_quality_status"})
        result = result.merge(branches, on="branch_id", how="left", suffixes=("", "_branch"))
        if "branch_name" in result.columns:
            raw_branch = result["branch_name_raw"] if "branch_name_raw" in result.columns else pd.Series(pd.NA, index=result.index, dtype="string")
            result["branch_display"] = result["branch_name"].combine_first(raw_branch)

    if "salesperson_id" in result.columns:
        people = _dimension_subset(
            data.salespeople,
            ["salesperson_id", "employee_code", "first_name", "last_name"],
        )
        result = result.merge(people, on="salesperson_id", how="left", suffixes=("", "_salesperson"))
        if {"first_name", "last_name"}.issubset(result.columns):
            result["salesperson_name"] = (
                result["first_name"].fillna("").astype(str).str.strip()
                + " "
                + result["last_name"].fillna("").astype(str).str.strip()
            ).str.strip().replace("", pd.NA)
    if "inventory_row_quality_status" in result.columns:
        result = result[
            result["inventory_row_quality_status"].astype("string").str.upper() != "ERROR"
        ]
    return result


def _apply_filters(
    frame: pd.DataFrame,
    filters: Filters,
    *,
    date_column: str,
    status_column: str | None,
) -> pd.DataFrame:
    result = frame.copy(deep=True)
    result[date_column] = pd.to_datetime(result[date_column], errors="coerce")
    if filters.start_date is not None:
        result = result[result[date_column] >= pd.Timestamp(filters.start_date)]
    if filters.end_date is not None:
        result = result[result[date_column] <= pd.Timestamp(filters.end_date)]
    if _values(filters.branch):
        result = result[_exact_match(result, ["branch_id", "branch_code", "branch_name", "branch_name_raw", "branch_display", "city"], _values(filters.branch))]
    if _values(filters.model):
        result = result[_exact_match(result, ["model_id", "model_name", "model_name_raw", "model_display"], _values(filters.model))]
    if _values(filters.brand):
        result = result[_exact_match(result, ["manufacturer"], _values(filters.brand))]
    if _values(filters.salesperson):
        result = result[_exact_match(result, ["salesperson_id", "employee_code", "salesperson_name"], _values(filters.salesperson))]
    if status_column and _values(filters.status):
        result = result[_exact_match(result, [status_column], _values(filters.status))]
    return result.copy()


def _period(series: pd.Series, frequency: Period) -> pd.Series:
    parsed = pd.to_datetime(series, errors="coerce")
    if frequency == "W":
        return parsed.dt.to_period("W-MON").dt.start_time
    return parsed.dt.to_period(frequency).dt.start_time


def _sales_for_metric(data: AnalyticsData, filters: Filters) -> pd.DataFrame:
    frame = _add_dimensions(_valid_fact(data.sales), data)
    if "inventory_row_quality_status" in frame.columns:
        frame = frame[
            frame["inventory_row_quality_status"].astype("string").str.upper() != "ERROR"
        ]
    frame = _apply_filters(frame, filters, date_column="sale_date", status_column="sale_status")
    if not _values(filters.status):
        frame = frame[frame["sale_status"] == "completed"]
    return frame.copy()


def revenue(data: AnalyticsData, filters: Filters) -> pd.DataFrame:
    """Return revenue by period.

    Formula: ``revenue = SUM(net_sale_price)`` and ``transaction_count = COUNT(sale_id)``.
    ``net_sale_price`` is the selling price before tax and fees. Completed sales are
    used unless ``filters.status`` explicitly requests other sale statuses. Exact
    duplicates have already been removed upstream. Fact rows with
    ``_row_quality_status == 'ERROR'`` and rows with null date or selling price are
    excluded; WARNING rows are included. Null prices are never treated as zero.
    """
    frame = _sales_for_metric(data, filters)
    if _missing_columns(frame, ["sale_date", "net_sale_price", "sale_id"]):
        return pd.DataFrame(columns=["period", "revenue", "transaction_count"])
    frame = frame.dropna(subset=["sale_date", "net_sale_price"])
    if frame.empty:
        return pd.DataFrame(columns=["period", "revenue", "transaction_count"])
    frame["period"] = _period(frame["sale_date"], filters.period)
    return (
        frame.groupby("period", as_index=False)
        .agg(revenue=("net_sale_price", "sum"), transaction_count=("sale_id", "count"))
        .sort_values("period", ignore_index=True)
    )


def gross_margin(data: AnalyticsData, filters: Filters) -> pd.DataFrame:
    """Return gross margin by period.

    Row formula: ``gross_margin = net_sale_price - acquisition_cost``. Aggregated
    margin is the sum of row margins; ``gross_margin_rate`` is aggregated margin
    divided by aggregated selling price. Completed sales are the default. ERROR
    sale rows and rows missing sale date, selling price, or acquisition cost are
    excluded. WARNING rows remain included. Flagged/null acquisition costs are not
    imputed and do not contribute to either margin or its denominator.
    """
    frame = _sales_for_metric(data, filters)
    if _missing_columns(frame, ["sale_date", "net_sale_price", "acquisition_cost"]):
        return pd.DataFrame(columns=["period", "selling_price", "acquisition_cost", "gross_margin", "gross_margin_rate"])
    frame = frame.dropna(subset=["sale_date", "net_sale_price", "acquisition_cost"])
    if frame.empty:
        return pd.DataFrame(columns=["period", "selling_price", "acquisition_cost", "gross_margin", "gross_margin_rate"])
    frame["gross_margin"] = frame["net_sale_price"] - frame["acquisition_cost"]
    frame["period"] = _period(frame["sale_date"], filters.period)
    result = frame.groupby("period", as_index=False).agg(
        selling_price=("net_sale_price", "sum"),
        acquisition_cost=("acquisition_cost", "sum"),
        gross_margin=("gross_margin", "sum"),
    )
    result["gross_margin_rate"] = result["gross_margin"].div(result["selling_price"].where(result["selling_price"] != 0))
    return result.sort_values("period", ignore_index=True)


def discount_rate(data: AnalyticsData, filters: Filters) -> pd.DataFrame:
    """Return the weighted discount rate by period.

    Formula: ``SUM(discount_amount) / SUM(gross_price)``. This is a weighted rate,
    not the mean of transaction-level percentages. Completed sales are used unless
    status is filtered explicitly. ERROR rows and rows missing date, gross price,
    or discount are excluded; WARNING rows are included. A zero gross-price total
    yields a null rate rather than division by zero.
    """
    frame = _sales_for_metric(data, filters).dropna(subset=["sale_date", "gross_price", "discount_amount"])
    if frame.empty:
        return pd.DataFrame(columns=["period", "gross_price", "discount_amount", "discount_rate"])
    frame["period"] = _period(frame["sale_date"], filters.period)
    result = frame.groupby("period", as_index=False).agg(
        gross_price=("gross_price", "sum"), discount_amount=("discount_amount", "sum")
    )
    result["discount_rate"] = result["discount_amount"].div(result["gross_price"].where(result["gross_price"] != 0))
    return result.sort_values("period", ignore_index=True)


def units_sold(data: AnalyticsData, filters: Filters) -> pd.DataFrame:
    """Return units sold by period.

    Formula: ``COUNT(DISTINCT inventory_id)``. Completed sales are used by default,
    enforcing the approved one-completed-sale-per-VIN intent without double-counting
    repeated transactions. ERROR sale rows and rows missing sale date or inventory
    ID are excluded; WARNING rows are included.
    """
    frame = _sales_for_metric(data, filters).dropna(subset=["sale_date", "inventory_id"])
    if frame.empty:
        return pd.DataFrame(columns=["period", "units_sold"])
    frame["period"] = _period(frame["sale_date"], filters.period)
    return (
        frame.groupby("period", as_index=False)
        .agg(units_sold=("inventory_id", "nunique"))
        .sort_values("period", ignore_index=True)
    )


def days_in_inventory(data: AnalyticsData, filters: Filters) -> pd.DataFrame:
    """Return vehicle-level inventory aging with age buckets.

    Formula: ``effective_end_date - arrival_date``. The effective end is sold date
    for sold vehicles and the filter end date (or latest ``record_updated_at``) for
    unsold vehicles. Date filters apply to arrival date. ERROR inventory rows and
    rows without a valid arrival/effective-end date are excluded; WARNING rows are
    included. Negative calculated ages are excluded rather than coerced to zero.
    ``days_in_inventory`` from the source is not used or overwritten.
    """
    frame = _add_dimensions(_valid_fact(data.inventory), data)
    frame = _apply_filters(frame, filters, date_column="arrival_date", status_column="inventory_status")
    if frame.empty:
        return pd.DataFrame(columns=["inventory_id", "vin", "branch", "model", "inventory_status", "arrival_date", "effective_end_date", "aging_days", "aging_bucket"])
    frame["arrival_date"] = pd.to_datetime(frame["arrival_date"], errors="coerce")
    frame["sold_date"] = pd.to_datetime(frame.get("sold_date"), errors="coerce")
    updated = pd.to_datetime(frame.get("record_updated_at"), errors="coerce")
    fallback_as_of = updated.max()
    as_of = pd.Timestamp(filters.end_date) if filters.end_date is not None else fallback_as_of
    frame["effective_end_date"] = frame["sold_date"].fillna(as_of)
    frame["aging_days"] = (frame["effective_end_date"] - frame["arrival_date"]).dt.days
    frame = frame.dropna(subset=["arrival_date", "effective_end_date", "aging_days"])
    frame = frame[frame["aging_days"] >= 0]
    frame["aging_bucket"] = pd.cut(
        frame["aging_days"], bins=[-1, 30, 60, 90, 180, float("inf")],
        labels=["0-30", "31-60", "61-90", "91-180", "181+"],
    ).astype("string")
    result = pd.DataFrame({
        "inventory_id": frame["inventory_id"], "vin": frame.get("vin"),
        "branch": frame.get("branch_display"), "model": frame.get("model_display"),
        "inventory_status": frame["inventory_status"], "arrival_date": frame["arrival_date"],
        "effective_end_date": frame["effective_end_date"], "aging_days": frame["aging_days"],
        "aging_bucket": frame["aging_bucket"],
    })
    return result.sort_values(["aging_days", "inventory_id"], ascending=[False, True], ignore_index=True)


def warranty_claims(data: AnalyticsData, filters: Filters) -> pd.DataFrame:
    """Return warranty claim count and approved cost by model and period.

    Formulas: ``claim_count = COUNT(claim_id)`` and
    ``claim_cost = SUM(approved_amount)``. Model display uses the approved canonical
    model when available and otherwise the preserved raw name; this is display
    fallback, not fuzzy mapping. ERROR claim rows and rows with null claim date are
    excluded. Claims with null approved amount still count but contribute nothing
    to cost; the result also reports ``costed_claim_count``. WARNING rows remain.
    """
    frame = _add_dimensions(_valid_fact(data.warranty_claims), data, resolve_salesperson_from_sale=True)
    frame = _apply_filters(frame, filters, date_column="claim_date", status_column="claim_status")
    frame = frame.dropna(subset=["claim_date"])
    if frame.empty:
        return pd.DataFrame(columns=["period", "model", "claim_count", "costed_claim_count", "claim_cost"])
    frame["period"] = _period(frame["claim_date"], filters.period)
    frame["model"] = frame.get("model_display", pd.Series(pd.NA, index=frame.index))
    frame = frame.dropna(subset=["model"])
    frame["costed"] = frame["approved_amount"].notna().astype(int)
    return (
        frame.groupby(["period", "model"], as_index=False, dropna=False)
        .agg(claim_count=("claim_id", "count"), costed_claim_count=("costed", "sum"), claim_cost=("approved_amount", "sum"))
        .sort_values(["period", "model"], ignore_index=True)
    )


def complaint_counts(data: AnalyticsData, filters: Filters) -> pd.DataFrame:
    """Return complaint counts by category and period.

    Formula: ``complaint_count = COUNT(complaint_id)``. ERROR complaint rows and
    rows with null complaint date or cleaned category are excluded. WARNING rows are
    included. No missing category is relabeled or guessed. Status filters apply to
    ``resolution_status``.
    """
    frame = _add_dimensions(_valid_fact(data.complaints), data, resolve_salesperson_from_sale=True)
    frame = _apply_filters(frame, filters, date_column="complaint_date", status_column="resolution_status")
    frame = frame.dropna(subset=["complaint_date", "complaint_category"])
    if frame.empty:
        return pd.DataFrame(columns=["period", "complaint_category", "complaint_count"])
    frame["period"] = _period(frame["complaint_date"], filters.period)
    return (
        frame.groupby(["period", "complaint_category"], as_index=False)
        .agg(complaint_count=("complaint_id", "count"))
        .sort_values(["period", "complaint_category"], ignore_index=True)
    )


def service_cost(data: AnalyticsData, filters: Filters) -> pd.DataFrame:
    """Return service cost by service category and period.

    Formula: ``service_cost = SUM(total_service_cost)``. ERROR service rows and rows
    missing open date, cleaned service type, or source total are excluded. The
    calculated companion is not substituted for a missing source total. WARNING
    rows are included. Status filters apply to ``service_status``.
    """
    frame = _add_dimensions(_valid_fact(data.service_records), data, resolve_salesperson_from_sale=True)
    frame = _apply_filters(frame, filters, date_column="service_open_date", status_column="service_status")
    frame = frame.dropna(subset=["service_open_date", "service_type", "total_service_cost"])
    if frame.empty:
        return pd.DataFrame(columns=["period", "service_type", "service_count", "service_cost"])
    frame["period"] = _period(frame["service_open_date"], filters.period)
    return (
        frame.groupby(["period", "service_type"], as_index=False)
        .agg(service_count=("service_id", "count"), service_cost=("total_service_cost", "sum"))
        .sort_values(["period", "service_type"], ignore_index=True)
    )


def average_satisfaction(data: AnalyticsData, filters: Filters) -> pd.DataFrame:
    """Return average overall satisfaction by survey type and period.

    Formula: ``average_satisfaction = MEAN(overall_score)`` with
    ``response_count = COUNT(overall_score)``. Scores are already cleaned to the
    approved 1-5 range. ERROR survey rows and rows with null survey date or score
    are excluded; WARNING rows are included. Status has no equivalent satisfaction
    field and is therefore ignored for this metric. Branch, model, brand, and
    salesperson filters are resolved through the survey's source transaction where
    possible; unresolved context cannot match a requested dimensional filter.
    """
    frame = _valid_fact(data.satisfaction)
    sales_lookup = _dimension_subset(data.sales, ["sale_id", "inventory_id", "salesperson_id"])
    service_lookup = _dimension_subset(data.service_records, ["service_id", "inventory_id", "sale_id"])
    complaint_lookup = _dimension_subset(data.complaints, ["complaint_id", "sale_id", "service_id"])
    if not service_lookup.empty:
        frame = frame.merge(service_lookup, on="service_id", how="left", suffixes=("", "_service"))
    if not complaint_lookup.empty:
        frame = frame.merge(complaint_lookup, on="complaint_id", how="left", suffixes=("", "_complaint"))
    if "sale_id_service" in frame.columns:
        frame["sale_id"] = frame["sale_id"].combine_first(frame["sale_id_service"])
    if "sale_id_complaint" in frame.columns:
        frame["sale_id"] = frame["sale_id"].combine_first(frame["sale_id_complaint"])
    if not sales_lookup.empty:
        frame = frame.merge(sales_lookup, on="sale_id", how="left", suffixes=("", "_sale"))
    if "inventory_id_sale" in frame.columns:
        frame["inventory_id"] = frame.get("inventory_id", pd.Series(index=frame.index, dtype="float64")).combine_first(frame["inventory_id_sale"])
    if "inventory_id_service" in frame.columns:
        frame["inventory_id"] = frame.get("inventory_id", pd.Series(index=frame.index, dtype="float64")).combine_first(frame["inventory_id_service"])
    frame = _add_dimensions(frame, data)
    frame = _apply_filters(frame, filters, date_column="survey_date", status_column=None)
    frame = frame.dropna(subset=["survey_date", "overall_score"])
    if frame.empty:
        return pd.DataFrame(columns=["period", "survey_type", "response_count", "average_satisfaction"])
    frame["period"] = _period(frame["survey_date"], filters.period)
    return (
        frame.groupby(["period", "survey_type"], as_index=False)
        .agg(response_count=("overall_score", "count"), average_satisfaction=("overall_score", "mean"))
        .sort_values(["period", "survey_type"], ignore_index=True)
    )


def overview_kpis(data: AnalyticsData, filters: Filters) -> pd.DataFrame:
    """Return current and prior-period values for the Overview KPI cards.

    The comparison is the immediately preceding inclusive range with the same
    number of days. Each value uses the formula and quality rules documented by
    its underlying public metric. Change is current minus previous; change rate
    divides that change by the absolute prior value. Without a complete selected
    range, comparison values remain null rather than being inferred.
    """
    def totals(target: Filters) -> dict[str, float]:
        revenue_frame = revenue(data, target)
        margin_frame = gross_margin(data, target)
        units_frame = units_sold(data, target)
        discount_frame = discount_rate(data, target)
        gross_price = discount_frame["gross_price"].sum() if not discount_frame.empty else 0.0
        discount_amount = discount_frame["discount_amount"].sum() if not discount_frame.empty else 0.0
        return {
            "Revenue": revenue_frame["revenue"].sum() if not revenue_frame.empty else 0.0,
            "Gross margin": margin_frame["gross_margin"].sum() if not margin_frame.empty else 0.0,
            "Units sold": units_frame["units_sold"].sum() if not units_frame.empty else 0.0,
            "Discount rate": discount_amount / gross_price if gross_price else float("nan"),
        }

    current = totals(filters)
    previous = {metric: float("nan") for metric in current}
    if filters.start_date is not None and filters.end_date is not None:
        start, end = pd.Timestamp(filters.start_date), pd.Timestamp(filters.end_date)
        if end >= start:
            duration = end - start
            previous = totals(Filters(
                start_date=start - duration - pd.Timedelta(days=1),
                end_date=start - pd.Timedelta(days=1),
                branch=filters.branch, model=filters.model, brand=filters.brand,
                salesperson=filters.salesperson, status=filters.status, period=filters.period,
            ))

    rows = []
    for metric, value in current.items():
        prior = previous[metric]
        change = value - prior if pd.notna(prior) else float("nan")
        rate = change / abs(prior) if pd.notna(prior) and prior != 0 else float("nan")
        rows.append({"metric": metric, "value": value, "previous_value": prior, "change": change, "change_rate": rate})
    return pd.DataFrame(rows)


def revenue_by_branch(data: AnalyticsData, filters: Filters) -> pd.DataFrame:
    """Return revenue and units by branch for the selected period.

    Revenue is ``SUM(net_sale_price)`` and units are distinct inventory IDs. The
    completed-sale default, exact filters, null handling, and ERROR-row exclusion
    match :func:`revenue`. Rows without a valid canonical branch are excluded.
    """
    frame = _sales_for_metric(data, filters)
    if _missing_columns(frame, ["sale_date", "net_sale_price", "inventory_id"]):
        return pd.DataFrame(columns=["branch", "revenue", "units_sold"])
    frame = frame.dropna(subset=["sale_date", "net_sale_price", "inventory_id"])
    if frame.empty:
        return pd.DataFrame(columns=["branch", "revenue", "units_sold"])
    frame["branch"] = frame.get("branch_display", pd.Series(pd.NA, index=frame.index))
    frame = frame.dropna(subset=["branch"])
    if frame.empty:
        return pd.DataFrame(columns=["branch", "revenue", "units_sold"])
    return (frame.groupby("branch", as_index=False)
            .agg(revenue=("net_sale_price", "sum"), units_sold=("inventory_id", "nunique"))
            .sort_values("revenue", ascending=False, ignore_index=True))


def gross_margin_by_model(data: AnalyticsData, filters: Filters) -> pd.DataFrame:
    """Return gross margin and margin rate by model for the selected period.

    Margin is ``SUM(net_sale_price - acquisition_cost)`` and the rate divides it
    by model revenue. Sales status, quality, and null rules match
    :func:`gross_margin`; rows without a valid canonical model are excluded.
    """
    frame = _sales_for_metric(data, filters)
    if _missing_columns(frame, ["sale_date", "net_sale_price", "acquisition_cost"]):
        return pd.DataFrame(columns=["model", "revenue", "gross_margin", "gross_margin_rate"])
    frame = frame.dropna(subset=["sale_date", "net_sale_price", "acquisition_cost"])
    if "model_id_orphan_flag" in frame.columns:
        frame = frame[~frame["model_id_orphan_flag"].fillna(False).astype(bool)]
    if frame.empty:
        return pd.DataFrame(columns=["model", "revenue", "gross_margin", "gross_margin_rate"])
    frame["gross_margin"] = frame["net_sale_price"] - frame["acquisition_cost"]
    frame["model"] = frame.get("model_display", pd.Series(pd.NA, index=frame.index))
    frame = frame.dropna(subset=["model"])
    frame = frame[
        ~frame["model"].astype("string").str.contains(
            r"Model ID|Unmapped", case=False, regex=True, na=False
        )
    ]
    if frame.empty:
        return pd.DataFrame(columns=["model", "revenue", "gross_margin", "gross_margin_rate"])
    result = frame.groupby("model", as_index=False).agg(
        revenue=("net_sale_price", "sum"), gross_margin=("gross_margin", "sum"))
    result["gross_margin_rate"] = result["gross_margin"].div(result["revenue"].where(result["revenue"] != 0))
    return result.sort_values("gross_margin", ascending=False, ignore_index=True)
