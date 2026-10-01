# VersalMotors Cleaning Decisions - APPROVED by Kwabena - 2026-10-01

1. Negative monetary values as credits? NO. FLAG is_negative_value=True, keep _raw, NULL for calc.
2. Missing totals filled? NO. Keep NULL original, create total_amount_calculated + is_total_estimated=True.
3. GHS 0.02 tolerance? YES APPROVED for pesewa rounding.
4. Branch/model mapping? Explicit mapping only in data/mapping_tables.csv. Branch: Accra, Kumasi, Tema, Takoradi, Tamale. Model: Hilux, Corolla, Camry, Prado, Yaris, Hiace. No fuzzy.
5. Unmapped canonical names? NULL canonical + raw kept in _raw column + is_unmapped=True.
6. Truncated categories: ful=full_payment, sol=sold, ava=available, sch=scheduled, rec=received, rep=repaired, pro=processing, ser=service, sta=staff, war=warranty, ema=email.
7. Unknown dimension member for orphan keys? NO. FK remains NULL + is_orphan_fk=True + original_fk_raw kept.
8. One completed sale per VIN? YES. FLAG is_duplicate_sale=True for extras, keep earliest.
9. Service records for vehicles not sold by us? YES VALID. Keep, flag is_external_vehicle=True.
10. One service multiple warranties? YES ALLOWED.
11. Pre-2023 transactions? YES VALID lead-in, flag is_pre_2023_lead_in=True.
12. Authoritative date? Sales: sale_completed_date > invoice_date > order_date. Service: service_completed_date. Gap >30 days FLAG.
13. Calculated durations replace source? NO. Keep source + companion + FLAG if mismatch >1 day.
14. Negative odometers? YES ALWAYS INVALID. NULL + _raw + FLAG.
15. Labor-hour and mileage thresholds? Labor >80h FLAG is_implausible_labor. Odometer >600k FLAG, negative delta FLAG rollback, jump >100k FLAG.
16. Satisfaction score ranges? YES 1-5 APPROVED. 0 and >5 invalid.
17. product_score only for post-sale? YES. Required for post_sale, optional for service.
18. Finance terms valid for lease required for financed? YES. Financed mandatory, lease valid, cash must be NULL.
19. Returned vehicles available with sold date? YES LEGITIMATE. Keep sold_date + returned_date + is_returned=True + is_resale=True.
20. Mandatory vs optional fields? MANDATORY: vin, inventory_id, model_canonical, branch_canonical, sale_completed_date, sale_status, customer_id, total_amount. OPTIONAL: notes, email, etc. NULL mandatory = FLAG.
21. fuel_efficiency unit? Combustion L/100km, EV kWh/100km, lower is better. >50 L/100km or >80 kWh/100km FLAG.
22. Exact duplicate removal keep first physical source row? YES APPROVED. Keep first occurrence by physical row order / file line number, even if rows indistinguishable. Log duplicate removal with reason=exact duplicate.
23. Near-duplicate candidate groups? Rule: Group by same vin + same branch_canonical + sale_completed_date within +/-1 day + total_amount within GHS 0.02 OR same customer_id + same model + same date +/-1 day. Create near_duplicate_group_id, FLAG is_near_duplicate=True, do NOT auto-delete, require manual review.
24. _row_quality_status severity precedence or multiple statuses? Use SEVERITY PRECEDENCE for single status: ERROR > WARNING > VALID. ERROR = mandatory missing, negative odometer, negative money, duplicate sale. WARNING = orphan, unmapped, ambiguous date, tolerance breach, implausible values, near-duplicate, external vehicle, pre-2023. VALID = clean. But ALSO keep all independent boolean flag columns for audit.