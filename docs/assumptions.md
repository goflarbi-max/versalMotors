# versalMotors relationship proposal and open questions

## Status

This document intentionally distinguishes observed evidence from decisions that require confirmation. No ambiguous cleaning rule below is treated as approved.

## Proposed logical relationships

The following model best fits the field names and observed values, subject to the questions below:

| Parent | Child | Proposed cardinality | Join |
|---|---|---|---|
| `branches` | `salespeople` | one-to-many | `branches.branch_id = salespeople.branch_id` |
| `branches` | `inventory` | one-to-many | `branches.branch_id = inventory.branch_id` |
| `branches` | `sales` | one-to-many | `branches.branch_id = sales.branch_id` |
| `branches` | `service_records` | one-to-many | `branches.branch_id = service_records.branch_id` |
| `branches` | `warranty_claims` | one-to-many | `branches.branch_id = warranty_claims.branch_id` |
| `branches` | `complaints` | one-to-many | `branches.branch_id = complaints.branch_id` |
| `branches` | `satisfaction` | one-to-many | `branches.branch_id = satisfaction.branch_id` |
| `models` | `inventory` | one-to-many | `models.model_id = inventory.model_id` |
| `inventory` | `sales` | one-to-zero/one after deduplication | `inventory.inventory_id = sales.inventory_id` |
| `salespeople` | `sales` | one-to-many | `salespeople.salesperson_id = sales.salesperson_id` |
| `sales` | `service_records` | one-to-many | `sales.sale_id = service_records.sale_id` |
| `inventory` | `service_records` | one-to-many | `inventory.inventory_id = service_records.inventory_id` |
| `service_records` | `warranty_claims` | one-to-zero/many | `service_records.service_id = warranty_claims.service_id` |
| `sales` / `service_records` / `warranty_claims` | `complaints` | transaction-to-zero/many | nullable complaint link columns |
| `sales` / `service_records` / `complaints` | `satisfaction` | transaction-to-zero/many | nullable survey link columns |

`customer_ref` appears to be a shared pseudonymous customer identifier across sales, service, complaints, and satisfaction. It could support customer-level analysis, but it is not backed by a customer master table and should not be declared a foreign key without confirmation.

### Suggested dependency path

```text
models ──< inventory ──< sales ──< service_records ──< warranty_claims
                 │          │              │                  │
branches ────────┼──────────┼──────────────┼──────────────────┤
                 │          └──────────────┴───────────> complaints
                 │                                  │
salespeople ─────┘                                  └──> satisfaction
```

The diagram is conceptual. `complaints` and `satisfaction` can link to different source transaction types, not only the immediately preceding node.

## Safe observations, not business assumptions

- All monetary records use raw `currency_code=GHS`.
- The main activity range is 2023-01-01 through 2025-06-30, but raw sales reach 2022-11-10 and claims reach 2022-12-15.
- Exact duplicate rows exist in all five event/response tables and repeat their primary key values.
- Branch, model, salesperson, and inventory master IDs are unique, but some child references are orphaned.
- Raw categorical variants must be preserved in a landing layer. Canonical values should be added in a curated layer only after mappings are approved.
- Negative money, impossible chronology, invalid scores, malformed VINs, and arithmetic inconsistencies should be flagged or quarantined rather than silently corrected.

## Questions requiring your decision

### Identity and duplicate handling

1. Should exact duplicate rows be removed by retaining the first occurrence, or must source order/timestamps determine the survivor?
2. What matching rule should define a near duplicate? Is “all non-PK fields equal after trimming” acceptable, or should monetary/date tolerances and a time window be used?
3. For duplicate or malformed VINs, is there an authoritative source column or external system that determines the correct vehicle identity?
4. Is `customer_ref` stable across all systems and time, or can one customer have multiple references or a reference be shared?

### Foreign keys and transaction grain

5. Should orphan records be quarantined, retained with an “unknown” dimension member, or rejected? Observed orphan values are 9001, 9002, 9003, 9004, 9007, and 9008.
6. Is one completed sale per `inventory_id` the intended rule, while allowing earlier cancellations/returns, or is every row an independent sale event?
7. Must every service record correspond to a versalMotors sale? Raw `service_records.sale_id` is always populated, but real workshops often service externally purchased vehicles.
8. Can one service visit create multiple warranty claims? The proposed model permits it, but the intended claim grain is not stated.
9. In complaints, is `sale_id` the primary source link with optional service/claim detail, or should exactly one of `sale_id`, `service_id`, and `claim_id` identify the source interaction?
10. In satisfaction, should exactly one of `sale_id`, `service_id`, or `complaint_id` be populated according to `survey_type`?

### Dates, status, and derived fields

11. Should transactions before 2023-01-01 be excluded, corrected, or retained as valid lead-in history?
12. For invalid chronology, which date is authoritative: arrival versus sale, service open versus close, complaint versus resolution, and service versus claim?
13. Should `days_in_inventory` and `days_to_resolution` always be recomputed from accepted dates, or preserved as source-system measures?
14. What does `active_flag` mean in `models`? All 2023–2024 rows are inactive while every `discontinued_date` is null.
15. Can an inventory row be `available` with a populated `sold_date` because a sale was returned, or is that always an error?
16. Should `active_flag=False` on a salesperson require a termination date, and should a termination date require inactive status?

### Measures and allowed values

17. What is the unit and direction of `fuel_efficiency`? Are combustion values km/L and EV values kWh/100 km, or is a single comparable measure intended?
18. Are negative costs ever legitimate credits/reversals, or should all negative acquisition, sale, service, warranty, and resolution amounts be treated as defects?
19. Which sales-price identity is authoritative: `gross - discount = net`, and does `net + tax + fees = total` always apply?
20. Should `labor + parts + misc = total_service_cost` and `customer_pay + warranty_pay = total_service_cost` hold on every completed service?
21. Are finance terms required only for `payment_method=finance`? Raw data has 3,933 finance rows without a term and 5,697 cash/lease rows with a term.
22. What are the approved scales: `overall_score` 1–10, `nps_score` 0–10, and the four component scores 1–5?
23. Is `product_score` intentionally applicable only to post-sale surveys? Its 9,001 nulls roughly align with non-sale survey types.

### Canonical categories and organizational meaning

24. Please confirm the canonical mappings for truncated values such as `ful`, `sol`, `ava`, `sch`, `rec`, `rep`, `pro`, `ser`, `sta`, `war`, and `ema`. Some are likely obvious, but the cleaning pipeline should not infer them without approval.
25. Is `branch_id` on a sale the transaction branch, while the salesperson’s branch is their current/home branch? If they differ after cleaning, which should drive branch sales reporting?
26. Is `branch_id` on a service or warranty claim the servicing branch, even when it differs from the selling or inventory branch?
27. Are manager, manufacturer, job title, color, technician team, claim description, complaint category, and customer type required fields, or may their observed blanks remain valid nulls?
28. Should case, punctuation, hyphens/underscores, and surrounding whitespace be normalized globally, or do any fields require case-sensitive preservation?

Until these questions are answered, a cleaning pipeline should produce quality flags and curated candidate columns while retaining the untouched raw values.
