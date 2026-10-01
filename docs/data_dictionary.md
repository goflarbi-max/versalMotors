# versalMotors raw data dictionary

Last profiled: **2026-10-01**, directly from all nine CSV files in `data/raw/` using `scripts/profile_raw_data.py`.

## Profiling scope and conventions

This document profiles the nine CSV files in `data/raw/` as observed, without using the private generator truth file. The profile was produced from the current files and should be refreshed if they change.

- A null is a blank field (the files contain no observed literal `NULL`, `None`, `NA`, or `N/A` values).
- Types are inferred storage types, not yet-approved warehouse types.
- Numeric and date ranges exclude nulls and unparseable values.
- An exact duplicate is a byte-equivalent data row. “Normalized non-PK duplicate extras” groups rows after excluding the first ID column and trimming surrounding whitespace; these are candidates, not proven duplicates.
- Categorical counts below preserve raw spelling, capitalization, punctuation, and whitespace. That is why apparent synonyms are listed separately.

## Table-level profile

| Table | Rows | Columns | Exact duplicate extras | Duplicate PK extras | Normalized non-PK duplicate extras |
|---|---:|---:|---:|---:|---:|
| `branches` | 15 | 13 | 0 | 0 | 0 |
| `models` | 54 | 18 | 0 | 0 | 0 |
| `salespeople` | 225 | 14 | 0 | 0 | 0 |
| `inventory` | 25,000 | 18 | 0 | 0 | 0 |
| `sales` | 20,540 | 22 | 20 | 20 | 40 |
| `service_records` | 48,060 | 20 | 35 | 35 | 60 |
| `warranty_claims` | 3,070 | 16 | 12 | 12 | 20 |
| `complaints` | 1,863 | 17 | 8 | 8 | 13 |
| `satisfaction` | 15,022 | 17 | 15 | 15 | 24 |

Normalized candidate counts include exact duplicates. The excess over exact duplicates is 20 in `sales`, 25 in `service_records`, 8 in `warranty_claims`, 5 in `complaints`, and 9 in `satisfaction`. The last figure may include naturally identical responses, so none should be removed without an agreed matching rule.

## `branches`

Grain: one apparent branch master record. Candidate primary key: `branch_id`.

| Column | Inferred type | Nulls | Observed range or cardinality |
|---|---|---:|---|
| `branch_id` | integer | 0 | 1–15; 15 distinct |
| `branch_code` | string | 0 | 15 distinct |
| `branch_name` | string | 0 | 15 distinct; inconsistent versalMotors spelling/case/spacing |
| `branch_type` | categorical string | 0 | 9 raw values |
| `address_line` | string | 0 | 15 distinct |
| `city` | categorical string | 0 | 13 distinct |
| `region` | categorical string | 0 | 11 distinct |
| `country_code` | categorical string | 0 | `GH` only |
| `opened_date` | date | 0 | 2008-09-28–2021-05-25 |
| `floor_capacity` | integer | 0 | 18–63 |
| `service_bay_count` | integer | 0 | 0–16 |
| `manager_name` | string | 8 | 7 populated, all distinct |
| `active_flag` | boolean | 0 | `True` 15 |

Categorical values:

- `branch_type`: `full_service` 3, `FULL_SERVICE` 2, `full_service ` 2, `sales_only` 2, `service_only` 2, `Full_Service` 1, `Sales_Only` 1, `ful` 1, `full-service` 1.
- `city`: Accra 2, Kumasi 2; Bolgatanga, Cape Coast, Ho, Kasoa, Koforidua, Sunyani, Takoradi, Tamale, Techiman, Tema, and Wa 1 each.
- `region`: Greater Accra 3, Ashanti 2, Central 2; Bono, Bono East, Eastern, Northern, Upper East, Upper West, Volta, and Western 1 each.

Suspicious observations: eight missing managers; ten branch-name formatting variants; six apparent noncanonical `branch_type` values. Whether a zero service-bay count is valid depends on the intended branch-type mapping.

## `models`

Grain: one model/model-year/trim record. Candidate primary key: `model_id`.

| Column | Inferred type | Nulls | Observed range or cardinality |
|---|---|---:|---|
| `model_id` | integer | 0 | 1–54; 54 distinct |
| `manufacturer` | categorical string | 12 | 6 populated values |
| `model_name` | string | 0 | 39 raw values |
| `model_year` | integer | 0 | 2023–2025 |
| `trim_name` | categorical string | 0 | 3 values |
| `vehicle_segment` | categorical string | 0 | 5 values |
| `body_style` | categorical string | 0 | 8 values |
| `powertrain` | categorical string | 0 | 4 values |
| `transmission` | categorical string | 0 | 4 values |
| `engine_size_l` | decimal | 9 | 1.5–3.0 |
| `battery_capacity_kwh` | decimal | 45 | 52–78 |
| `fuel_efficiency` | decimal | 0 | 5.22–21.80; unit not supplied |
| `seating_capacity` | integer | 0 | 3–8 |
| `msrp` | decimal | 0 | GHS 137,750–448,500 |
| `currency_code` | categorical string | 0 | `GHS` only |
| `launch_date` | date | 0 | 2022-09-01–2024-09-01 |
| `discontinued_date` | date/empty | 54 | no populated values |
| `active_flag` | boolean | 0 | `True` 18, `False` 36 |

Categorical values:

- `manufacturer`: Aster 8, Crest 8, Boreal 7, Dune 7, Elara 6, Forge 6, plus 12 nulls.
- `trim_name`: Comfort 18, Core 18, Premium 18.
- `vehicle_segment`: SUV 18; Hatchback, Pickup, Sedan, and Van 9 each.
- `body_style`: Crossover 12; Hatchback 9; Sedan 9; Double-cab pickup 6; Minivan 6; SUV 6; Panel van 3; Single-cab pickup 3.
- `powertrain`: Petrol 27, Diesel 9, EV 9, Hybrid 9.
- `transmission`: Automatic 32, CVT 11, Single-speed 9, Manual 2.

Suspicious observations: 12 missing manufacturers; 39 raw model names for 18 apparent product lines, suggesting name variants; no discontinued dates despite 36 inactive records. Engine size is null for nine EV rows and battery capacity is populated for nine EV rows, which appears structurally reasonable but needs confirmation. Fuel-efficiency values cannot be safely compared across powertrains without a unit definition.

## `salespeople`

Grain: one employee record. Candidate primary key: `salesperson_id`; alternate key: `employee_code`.

| Column | Inferred type | Nulls | Observed range or cardinality |
|---|---|---:|---|
| `salesperson_id` | integer | 0 | 1–225; unique |
| `employee_code` | string | 0 | 225 distinct |
| `branch_id` | integer/FK | 0 | 1–13 and 9001 |
| `first_name` | string | 0 | 20 distinct |
| `last_name` | string | 0 | 55 raw values |
| `gender` | categorical string | 0 | Female 108, Male 117 |
| `hire_date` | date | 0 | 2014-01-10–2025-02-12 |
| `termination_date` | date | 191 | 2023-01-13–2025-06-26 |
| `job_title` | categorical string | 20 | 4 populated values |
| `experience_years_at_hire` | integer | 0 | 0–13 |
| `monthly_target_units` | integer | 0 | 7–15 |
| `commission_rate` | decimal ratio | 0 | 0.0120–0.0349 |
| `active_flag` | boolean | 0 | `True` 191, `False` 34 |

`job_title` values: Sales Consultant 136, Senior Sales Consultant 44, Fleet Specialist 13, Sales Supervisor 12, null 20.

Suspicious observations: eight rows use nonexistent `branch_id=9001`; 20 titles are missing; surname spelling/case variants appear likely. Active counts align numerically with null termination dates, but row-level semantics should still be validated before enforcing the rule.

## `inventory`

Grain: one physical vehicle record. Candidate primary key: `inventory_id`; expected alternate key: `vin`.

| Column | Inferred type | Nulls | Observed range or cardinality |
|---|---|---:|---|
| `inventory_id` | integer | 0 | 1–25,000; unique |
| `vin` | string | 7 | 24,941 distinct non-null raw values |
| `model_id` | integer/FK | 0 | 55 distinct; includes 9002 |
| `branch_id` | integer/FK | 0 | 1–13 and 9003 |
| `exterior_color` | categorical string | 15 | 8 populated values |
| `interior_color` | categorical string | 0 | 4 values |
| `manufacture_date` | date | 0 | 2022-06-01–2025-05-15 |
| `acquisition_date` | date | 0 | 2022-10-01–2025-06-10 |
| `arrival_date` | date | 0 | 2022-10-13–2025-06-30 |
| `condition` | categorical string | 0 | 3 values |
| `odometer_km` | integer | 0 | 0–94,965 |
| `acquisition_cost` | decimal | 30 | GHS -352,206.43–385,693.45; 20 negative |
| `listed_price` | decimal | 35 | GHS 135,028.75–473,134.06 |
| `currency_code` | categorical string | 0 | `GHS` only |
| `inventory_status` | categorical string | 0 | 7 raw values |
| `sold_date` | date | 5,140 | 2023-01-01–2025-06-30 |
| `days_in_inventory` | integer | 0 | 0–991 |
| `record_updated_at` | datetime | 0 | 2025-06-30T23:59:59 only |

Categorical values:

- `condition`: new 22,020, used 1,721, demo 1,259.
- `exterior_color`: White 6,058, Black 4,495, Silver 4,443, Grey 3,767, Blue 2,451, Red 2,030, Green 1,000, Bronze 741, null 15.
- `interior_color`: Black 13,757, Grey 5,743, Tan 3,741, Brown 1,759.
- `inventory_status`: sold 19,821, available 5,159, SOLD 5, Sold 5, `sold ` 5, sol 4, ava 1.

Suspicious observations: 12 rows reference missing model 9002; 10 reference missing branch 9003; 35 VINs fail the 17-character allowed-character pattern; repeated malformed placeholders plus reused valid VINs produce 58 duplicate-VIN extra rows; 20 negative acquisition costs; 65 missing cost/price values; 20 vehicles say `available` while having a sold date. Status variants require normalization.

## `sales`

Grain: apparent sale transaction. Candidate primary key: `sale_id` after deduplication.

| Column | Inferred type | Nulls | Observed range or cardinality |
|---|---|---:|---|
| `sale_id` | integer | 0 | 1–20,520; 20 duplicate-ID extras |
| `inventory_id` | integer/FK | 0 | 20,500 distinct |
| `branch_id` | integer/FK | 0 | 1–13 |
| `salesperson_id` | integer/FK | 0 | 226 distinct; includes 9004 |
| `customer_ref` | string/link key | 0 | 11,477 distinct |
| `sale_date` | date | 0 | 2022-11-10–2025-06-30 |
| `delivery_date` | date | 431 | 2023-01-10–2025-06-30 |
| `sale_status` | categorical string | 0 | 3 values |
| `sales_channel` | categorical string | 0 | 15 raw values |
| `customer_type` | categorical string | 15 | 4 populated values |
| `gross_price` | decimal | 0 | GHS 133,396.49–474,450.84 |
| `discount_amount` | decimal | 0 | GHS 0–85,201.38 |
| `net_sale_price` | decimal | 0 | GHS -393,746.42–470,456.50; 15 negative |
| `tax_amount` | decimal | 0 | GHS 16,453.80–70,568.47 |
| `fees_amount` | decimal | 0 | GHS 850.26–2,599.99 |
| `total_sale_price` | decimal | 55 | GHS 128,008.41–542,329.21 |
| `currency_code` | categorical string | 0 | `GHS` only |
| `payment_method` | categorical string | 0 | 3 values |
| `finance_term_months` | integer | 6,396 | 24–60 |
| `trade_in_flag` | boolean | 0 | False 16,234, True 4,306 |
| `trade_in_value` | decimal | 16,234 | GHS 22,039.30–134,972.12 |
| `created_at` | datetime | 0 | 2023-01-01–2025-06-30 |

Categorical values:

- `sale_status`: completed 19,897, cancelled 431, returned 212.
- `sales_channel` canonical-looking values: showroom 12,735, website_lead 3,754, fleet 2,630, telephone 1,396. There are 25 additional rows across uppercase, title-case, trailing-space, hyphenated, and truncated variants.
- `customer_type`: individual 14,721, business 3,120, fleet 1,899, government 785, null 15.
- `payment_method`: finance 12,380, cash 6,368, lease 1,792.

Suspicious observations: 20 exact duplicate rows/PK extras; 40 normalized non-PK duplicate extras; 15 rows reference nonexistent salesperson 9004; 35 sales precede their vehicle arrival; 65 rows fail `gross_price - discount_amount = net_sale_price`; 15 negative net prices; 55 missing totals. There are 3,933 finance sales with no term and 5,697 non-finance sales with a term. Trade-in flags and values are internally consistent. The earliest sale predates the stated 2023 analysis window.

## `service_records`

Grain: apparent workshop visit/work order. Candidate primary key: `service_id` after deduplication.

| Column | Inferred type | Nulls | Observed range or cardinality |
|---|---|---:|---|
| `service_id` | integer | 0 | 1–48,025; 35 duplicate-ID extras |
| `inventory_id` | integer/FK | 0 | 15,006 distinct |
| `branch_id` | integer/FK | 0 | 1–15 |
| `sale_id` | integer/FK | 0 | 15,006 distinct |
| `customer_ref` | string/link key | 0 | 9,663 distinct |
| `service_open_date` | date | 0 | 2023-01-23–2025-06-30 |
| `service_close_date` | date | 3,560 | 2023-01-24–2025-06-30 |
| `service_type` | categorical string | 0 | 17 raw values |
| `service_status` | categorical string | 0 | completed 44,498, open 3,562 |
| `odometer_km` | integer | 0 | -48,632–57,849; 24 negative |
| `labor_hours` | decimal | 0 | 0.5–399.47 |
| `labor_cost` | decimal | 0 | GHS 85.01–6,596.54 |
| `parts_cost` | decimal | 0 | GHS -14,306.83–34,404.63; 20 negative |
| `misc_cost` | decimal | 0 | GHS 15.01–180.00 |
| `total_service_cost` | decimal | 40 | GHS 185.40–34,870.12 |
| `customer_pay_amount` | decimal | 0 | GHS 0–34,870.12 |
| `warranty_pay_amount` | decimal | 0 | GHS 0–30,389.98 |
| `currency_code` | categorical string | 0 | `GHS` only |
| `technician_team` | categorical string | 15 | TEAM-01 through TEAM-24 |
| `repeat_repair_flag` | boolean-like string | 0 | False 46,900, True 1,135, `False ` 25 |

`service_type` canonical-looking values: scheduled 24,974, repair 12,849, inspection 5,409, recall 2,427, bodywork 2,377. Twenty-four additional rows use case, whitespace, or truncated variants.

Suspicious observations: 35 exact duplicates and 60 normalized non-PK duplicate extras; 30 close dates precede open dates; 24 negative odometers; 24 labor-hour values exceed 100; 20 negative parts costs; 40 missing total costs; 50 component-total mismatches; 30 customer-pay plus warranty-pay mismatches. No observed FK orphan exists for `inventory_id`, `branch_id`, or `sale_id`.

## `warranty_claims`

Grain: apparent warranty claim. Candidate primary key: `claim_id` after deduplication.

| Column | Inferred type | Nulls | Observed range or cardinality |
|---|---|---:|---|
| `claim_id` | integer | 0 | 1–3,058; 12 duplicate-ID extras |
| `service_id` | integer/FK | 0 | 3,040 distinct |
| `inventory_id` | integer/FK | 0 | 2,591 distinct |
| `sale_id` | integer/FK | 0 | 2,591 distinct |
| `branch_id` | integer/FK | 0 | 1–15 |
| `claim_date` | date | 0 | 2022-12-15–2025-06-30 |
| `failure_category` | categorical string | 0 | 7 values |
| `claim_description` | string | 8 | 7 populated templates |
| `claim_amount` | decimal | 20 | GHS 206.09–22,554.44 |
| `approved_amount` | decimal | 0 | GHS -4,194.28–22,554.44; 10 negative |
| `claim_status` | categorical string | 0 | 3 values |
| `decision_date` | date | 20 | 2023-03-26–2025-06-30 |
| `manufacturer_recovery_amount` | decimal | 0 | GHS 0–20,940.98 |
| `currency_code` | categorical string | 0 | `GHS` only |
| `days_to_resolution` | integer | 0 | 0–52 |
| `repeat_claim_flag` | boolean-like string | 0 | False 2,826, True 236, `False ` 8 |

Categorical values:

- `failure_category`: electrical 727, engine 559, infotainment 386, transmission 380, suspension 354, battery 337, body_hardware 327.
- `claim_status`: approved 2,013, denied 626, partially_approved 431.

Suspicious observations: 12 exact duplicates and 20 normalized non-PK duplicate extras; 20 claims precede the analysis window and 24 precede their linked service opening date; 20 missing claim amounts; 10 negative approved amounts; 20 approved claims lack a decision date. No observed FK orphans exist in this table.

## `complaints`

Grain: apparent customer complaint. Candidate primary key: `complaint_id` after deduplication.

| Column | Inferred type | Nulls | Observed range or cardinality |
|---|---|---:|---|
| `complaint_id` | integer | 0 | 1–1,855; 8 duplicate-ID extras |
| `customer_ref` | string/link key | 0 | 1,628 distinct |
| `branch_id` | integer/FK | 0 | 1–15 |
| `sale_id` | integer/FK | 0 | 1,722 distinct |
| `service_id` | integer/FK | 703 | 37–47,944 |
| `claim_id` | integer/FK | 1,544 | 30–9,007 |
| `complaint_date` | date | 0 | 2023-01-22–2025-06-30 |
| `complaint_channel` | categorical string | 0 | 5 values |
| `complaint_category` | categorical string | 7 | 21 raw values |
| `severity` | categorical string | 0 | 4 values |
| `complaint_text` | string | 0 | 24 templates |
| `resolution_status` | categorical string | 0 | 4 values |
| `resolution_date` | date | 358 | 2023-01-29–2025-06-30 |
| `resolution_cost` | decimal | 0 | GHS -3,592.31–3,996.37; 10 negative |
| `currency_code` | categorical string | 0 | `GHS` only |
| `escalated_flag` | boolean | 0 | False 1,534, True 329 |
| `days_to_resolution` | integer | 348 | 0–22 |

Categorical values:

- `complaint_channel`: phone 706, email 504, website 329, in_person 246, social 78.
- `complaint_category` canonical-looking values: product 435, warranty 314, billing 312, service_delay 311, delivery 251, staff 215. Eighteen additional rows comprise case, trailing-space, and truncated variants; 7 are null.
- `severity`: medium 845, low 568, high 371, critical 79.
- `resolution_status`: resolved 1,399, open 185, investigating 160, rejected 119.

Suspicious observations: 8 exact duplicates and 13 normalized non-PK duplicate extras; 8 claim references use nonexistent claim 9007; 15 resolution dates precede complaint dates; 20 resolved complaints have no resolution date; 10 negative resolution costs. `resolution_date` has 358 nulls while `days_to_resolution` has 348, so ten rows contain a duration without a resolution date or vice versa.

## `satisfaction`

Grain: apparent survey response. Candidate primary key: `survey_id` after deduplication.

| Column | Inferred type | Nulls | Observed range or cardinality |
|---|---|---:|---|
| `survey_id` | integer | 0 | 1–15,007; 15 duplicate-ID extras |
| `customer_ref` | string/link key | 0 | 7,211 distinct |
| `branch_id` | integer/FK | 0 | 1–15 |
| `sale_id` | integer/FK | 9,001 | 11–20,500 |
| `service_id` | integer/FK | 7,819 | 20–47,997 |
| `complaint_id` | integer/FK | 13,224 | 1–9,008 |
| `survey_date` | date | 0 | 2023-01-10–2025-06-30; 10 unparseable dates |
| `survey_type` | categorical string | 0 | 3 values |
| `overall_score` | integer | 0 | -1–99 |
| `nps_score` | integer | 0 | -1–99 |
| `product_score` | integer | 9,001 | -1–99 |
| `staff_score` | integer | 0 | -1–99 |
| `timeliness_score` | integer | 0 | -1–99 |
| `value_score` | integer | 0 | -1–99 |
| `recommend_flag` | boolean | 0 | True 11,539, False 3,483 |
| `response_channel` | categorical string | 0 | 13 raw values |
| `comment_text` | string | 9,054 | 3 raw values |

Categorical values:

- `survey_type`: post_service 7,203, post_sale 6,021, complaint_follow_up 1,798.
- `response_channel` canonical-looking values: sms 6,245, email 4,964, web 2,739, phone 1,060. Fourteen additional rows use case, trailing-space, or truncated variants.
- `comment_text`: “Very positive experience.” 5,595; “Service did not meet expectations.” 371; the positive text with trailing whitespace 2; null 9,054.

Suspicious observations: 15 exact duplicates and 24 normalized non-PK duplicate extras; 7 complaint references use nonexistent complaint 9008; 10 survey dates are invalid calendar dates; 41 rows have at least one score outside its likely scale. The observed score extrema are -1 and 99, but permitted scales require confirmation. Product scores are null on 9,001 responses, apparently by survey type.

## Observed cross-table key integrity

| Proposed child FK | Proposed parent PK | Non-null child rows | Observed orphan rows | Orphan raw value |
|---|---|---:|---:|---|
| `salespeople.branch_id` | `branches.branch_id` | 225 | 8 | 9001 |
| `inventory.model_id` | `models.model_id` | 25,000 | 12 | 9002 |
| `inventory.branch_id` | `branches.branch_id` | 25,000 | 10 | 9003 |
| `sales.inventory_id` | `inventory.inventory_id` | 20,540 | 0 | — |
| `sales.branch_id` | `branches.branch_id` | 20,540 | 0 | — |
| `sales.salesperson_id` | `salespeople.salesperson_id` | 20,540 | 15 | 9004 |
| `service_records.inventory_id` | `inventory.inventory_id` | 48,060 | 0 | — |
| `service_records.branch_id` | `branches.branch_id` | 48,060 | 0 | — |
| `service_records.sale_id` | `sales.sale_id` | 48,060 | 0 | — |
| `warranty_claims.service_id` | `service_records.service_id` | 3,070 | 0 | — |
| `warranty_claims.inventory_id` | `inventory.inventory_id` | 3,070 | 0 | — |
| `warranty_claims.sale_id` | `sales.sale_id` | 3,070 | 0 | — |
| `warranty_claims.branch_id` | `branches.branch_id` | 3,070 | 0 | — |
| `complaints.branch_id` | `branches.branch_id` | 1,863 | 0 | — |
| `complaints.sale_id` | `sales.sale_id` | 1,863 | 0 | — |
| `complaints.service_id` | `service_records.service_id` | 1,160 | 0 | — |
| `complaints.claim_id` | `warranty_claims.claim_id` | 319 | 8 | 9007 |
| `satisfaction.branch_id` | `branches.branch_id` | 15,022 | 0 | — |
| `satisfaction.sale_id` | `sales.sale_id` | 6,021 | 0 | — |
| `satisfaction.service_id` | `service_records.service_id` | 7,203 | 0 | — |
| `satisfaction.complaint_id` | `complaints.complaint_id` | 1,798 | 7 | 9008 |

These counts are calculated against raw parent-key sets. Duplicate parent PKs make the raw joins many-to-many unless parent tables are deduplicated first.
