"""Pure analytical functions for versalMotors business metrics."""

from .metrics import (
    AnalyticsData,
    Filters,
    average_satisfaction,
    complaint_counts,
    days_in_inventory,
    discount_rate,
    gross_margin,
    revenue,
    service_cost,
    units_sold,
    warranty_claims,
)

__all__ = [
    "AnalyticsData", "Filters", "revenue", "gross_margin", "discount_rate",
    "units_sold", "days_in_inventory", "warranty_claims", "complaint_counts",
    "service_cost", "average_satisfaction",
]
