"""Pure drill-down analytics from warranty summary to claim-level evidence."""

from __future__ import annotations

from dataclasses import replace

import pandas as pd

from .metrics import AnalyticsData, Filters, _exact_match, _values, _valid_fact


SUMMARY_COLUMNS = [
    "model", "claim_count", "claim_cost", "previous_claim_cost", "cost_change", "cost_change_rate",
]
BRANCH_COLUMNS = ["branch", "claim_count", "claim_cost", "share_of_model_cost"]
RECORD_COLUMNS = [
    "claim_id", "claim_date", "model", "branch", "failure_category",
    "claim_description", "claim_status", "claim_amount", "approved_amount",
    "manufacturer_recovery_amount", "sale_id", "service_id", "inventory_id",
    "_row_quality_status",
]


def _warranty_rows(data: AnalyticsData, filters: Filters) -> pd.DataFrame:
    """Return quality-approved claims enriched for exact global filtering."""
    claims = _valid_fact(data.warranty_claims)
    inventory_columns = [column for column in ["inventory_id", "model_id", "_row_quality_status", "model_id_orphan_flag"] if column in data.inventory.columns]
    if inventory_columns:
        inventory = data.inventory[inventory_columns].drop_duplicates("inventory_id").rename(
            columns={"_row_quality_status": "inventory_row_quality_status"})
        claims = claims.merge(
            inventory,
            on="inventory_id", how="left", suffixes=("", "_inventory"),
        )
    model_columns = [column for column in ["model_id", "model_name", "manufacturer", "_row_quality_status"] if column in data.models.columns]
    if model_columns and "model_id" in claims.columns:
        models = data.models[model_columns].drop_duplicates("model_id").rename(
            columns={"_row_quality_status": "model_row_quality_status"})
        claims = claims.merge(
            models, on="model_id", how="left",
        )
    branch_columns = [column for column in ["branch_id", "branch_name", "branch_code", "_row_quality_status"] if column in data.branches.columns]
    if branch_columns:
        branches = data.branches[branch_columns].drop_duplicates("branch_id").rename(
            columns={"_row_quality_status": "branch_row_quality_status"})
        claims = claims.merge(
            branches, on="branch_id", how="left",
        )
    sale_columns = [column for column in ["sale_id", "salesperson_id", "sale_status"] if column in data.sales.columns]
    if sale_columns:
        claims = claims.merge(
            data.sales[sale_columns].drop_duplicates("sale_id"), on="sale_id", how="left",
        )
    people_columns = [column for column in ["salesperson_id", "employee_code", "first_name", "last_name"] if column in data.salespeople.columns]
    if people_columns and "salesperson_id" in claims.columns:
        claims = claims.merge(
            data.salespeople[people_columns].drop_duplicates("salesperson_id"),
            on="salesperson_id", how="left",
        )
        if {"first_name", "last_name"}.issubset(claims.columns):
            claims["salesperson_name"] = (
                claims["first_name"].fillna("").astype(str).str.strip() + " "
                + claims["last_name"].fillna("").astype(str).str.strip()
            ).str.strip().replace("", pd.NA)

    claims["claim_date"] = pd.to_datetime(claims["claim_date"], errors="coerce")
    if filters.start_date is not None:
        claims = claims[claims["claim_date"] >= pd.Timestamp(filters.start_date)]
    if filters.end_date is not None:
        claims = claims[claims["claim_date"] <= pd.Timestamp(filters.end_date)]
    if _values(filters.branch):
        claims = claims[_exact_match(claims, ["branch_id", "branch_name", "branch_code"], filters.branch)]
    if _values(filters.model):
        claims = claims[_exact_match(claims, ["model_id", "model_name"], filters.model)]
    if _values(filters.brand):
        claims = claims[_exact_match(claims, ["manufacturer"], filters.brand)]
    if _values(filters.salesperson):
        claims = claims[_exact_match(claims, ["salesperson_id", "employee_code", "salesperson_name"], filters.salesperson)]
    if _values(filters.status):
        claims = claims[_exact_match(claims, ["sale_status"], filters.status)]
    if "inventory_row_quality_status" in claims.columns:
        claims = claims[
            claims["inventory_row_quality_status"].astype("string").str.upper() != "ERROR"
        ]
    if "model_id_orphan_flag" in claims.columns:
        claims = claims[~claims["model_id_orphan_flag"].fillna(False).astype(bool)]
    claims["model"] = claims.get("model_name", pd.Series(pd.NA, index=claims.index))
    claims["branch"] = claims.get("branch_name", pd.Series(pd.NA, index=claims.index))
    claims = claims.dropna(subset=["model", "branch"])
    forbidden = r"Model ID|Unmapped"
    claims = claims[
        ~claims["model"].astype("string").str.contains(forbidden, case=False, regex=True, na=False)
        & ~claims["branch"].astype("string").str.contains(forbidden, case=False, regex=True, na=False)
    ]
    return claims.copy()


def _cost_by_model(data: AnalyticsData, filters: Filters) -> pd.DataFrame:
    rows = _warranty_rows(data, filters).dropna(subset=["claim_date"])
    if rows.empty:
        return pd.DataFrame(columns=["model", "claim_count", "claim_cost"])
    return (rows.groupby("model", as_index=False)
            .agg(claim_count=("claim_id", "count"), claim_cost=("approved_amount", "sum")))


def warranty_by_model(data: AnalyticsData, filters: Filters) -> pd.DataFrame:
    """Return claim count/cost by model with a same-length prior comparison.

    Cost is ``SUM(approved_amount)`` and count is ``COUNT(claim_id)``. Claims with
    missing approved amounts still count and add no cost. ERROR rows and invalid
    claim dates are excluded; WARNING rows remain. Prior dates are the immediately
    preceding inclusive range. All global exact filters are preserved.
    """
    current = _cost_by_model(data, filters)
    if current.empty:
        return pd.DataFrame(columns=SUMMARY_COLUMNS)
    previous = pd.DataFrame(columns=["model", "previous_claim_cost"])
    if filters.start_date is not None and filters.end_date is not None:
        start, end = pd.Timestamp(filters.start_date), pd.Timestamp(filters.end_date)
        if end >= start:
            duration = end - start
            prior_filters = replace(
                filters, start_date=start - duration - pd.Timedelta(days=1),
                end_date=start - pd.Timedelta(days=1),
            )
            previous = _cost_by_model(data, prior_filters)[["model", "claim_cost"]].rename(
                columns={"claim_cost": "previous_claim_cost"})
    result = current.merge(previous, on="model", how="left")
    result["previous_claim_cost"] = result["previous_claim_cost"].fillna(0.0)
    result["cost_change"] = result["claim_cost"] - result["previous_claim_cost"]
    result["cost_change_rate"] = result["cost_change"].div(
        result["previous_claim_cost"].where(result["previous_claim_cost"] != 0))
    return result[SUMMARY_COLUMNS].sort_values("claim_cost", ascending=False, ignore_index=True)


def warranty_by_branch(data: AnalyticsData, filters: Filters, model: str) -> pd.DataFrame:
    """Return claim cost/count by branch for one exact model selection."""
    rows = _warranty_rows(data, filters)
    rows = rows[_exact_match(rows, ["model"], (model,))]
    if rows.empty:
        return pd.DataFrame(columns=BRANCH_COLUMNS)
    result = rows.groupby("branch", as_index=False).agg(
        claim_count=("claim_id", "count"), claim_cost=("approved_amount", "sum"))
    total = result["claim_cost"].sum()
    result["share_of_model_cost"] = result["claim_cost"].div(total if total else float("nan"))
    return result[BRANCH_COLUMNS].sort_values("claim_cost", ascending=False, ignore_index=True)


def warranty_claim_records(
    data: AnalyticsData, filters: Filters, model: str, branch: str,
) -> pd.DataFrame:
    """Return individual warranty claims for exact selected model and branch.

    The records use the same filters and quality policy as the summary functions,
    guaranteeing that displayed evidence reconciles to its branch total.
    """
    rows = _warranty_rows(data, filters)
    rows = rows[
        _exact_match(rows, ["model"], (model,))
        & _exact_match(rows, ["branch"], (branch,))
    ]
    available = [column for column in RECORD_COLUMNS if column in rows.columns]
    return rows[available].sort_values(["claim_date", "claim_id"], ascending=[False, True], ignore_index=True)
