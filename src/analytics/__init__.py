"""Pure analytical functions for versalMotors business metrics."""

from .metrics import (
    AnalyticsData,
    Filters,
    average_satisfaction,
    complaint_counts,
    days_in_inventory,
    discount_rate,
    gross_margin,
    gross_margin_by_model,
    overview_kpis,
    revenue,
    revenue_by_branch,
    service_cost,
    units_sold,
    warranty_claims,
)
from .drilldown import warranty_by_branch, warranty_by_model, warranty_claim_records

__all__ = [
    "AnalyticsData", "Filters", "revenue", "gross_margin", "discount_rate",
    "units_sold", "days_in_inventory", "warranty_claims", "complaint_counts",
    "service_cost", "average_satisfaction",
    "overview_kpis", "revenue_by_branch", "gross_margin_by_model",
    "warranty_by_model", "warranty_by_branch", "warranty_claim_records",
]
