## Metrics verification - Oct 1 2026
Checked for double-counting, list_price vs net_sale_price mix, nulls dropped.
Result: Fixed import path and schema. Verified revenue via raw SQL vs metrics.py - exact match. 3/3 tests passed.

## Decisions confirmed - Oct 2 2026
1. Complaint co-occurrence: Combined rule - same sale_id OR same customer_id within 30 days.
2. Default scan: Report latest complete month, use up to 12 prior months as context for trends.
3. Severity threshold: Suppress <40 from management output, retain when include_low_severity=True.
4. Inventory categories: Use vehicle_segment + condition only, exclude branch initially for stronger sample sizes.

## AI Mistakes Log - Day 3 onwards
Format: Date | Prompt | Wrong Answer | Correct Answer | Fix


