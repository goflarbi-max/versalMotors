# versalMotors generator truth

> **PRIVATE QA ARTIFACT.** Do not expose this file to application code, dashboards, prompts, or end users.

- Fixed random seed: `20250301`
- Clean generation window: `2023-01-01` through `2025-06-30` (30 months)
- Currency and market: `GHS`, Ghana
- CSV encoding/newlines: UTF-8, LF

## Output inventory

| Table | Clean base rows | Dirty output rows | SHA-256 |
|---|---:|---:|---|
| `branches` | 15 | 15 | `d076afc9ed4a2edbdc2fe400a0103f1e4d7c757b43107679ec1197fd8c535c29` |
| `models` | 54 | 54 | `c5db978f66ce75f0295fd06991836d5829d892eefd907a613903fa717de9a8df` |
| `salespeople` | 225 | 225 | `cc36850f4f9533e5c95489b275f462913be5c6191cb0451eb4ca220dffc08b0d` |
| `inventory` | 25,000 | 25,000 | `3fb9e9ef9d31f67098f99c5e3c69050757c4bf664580af4e03f0e24708e03900` |
| `sales` | 20,500 | 20,540 | `c06fb8a0720d809bb5e4aca0330205d68b07b1223f4cf2e9bd5772124a53d73f` |
| `service_records` | 48,000 | 48,060 | `00f80898f6ac550e4f96ac736278be028646ae994ed72f15d5fe22669e577229` |
| `warranty_claims` | 3,050 | 3,070 | `61f9f316f4bdad9975b4a61721cd91e669f48f39d0078f29ee3363a78eab4f0f` |
| `complaints` | 1,850 | 1,863 | `91981faa247fc93eb3930f7d235775404754135bb719aa91f8ccc5862320b371` |
| `satisfaction` | 15,000 | 15,022 | `62837d38b03ec63bef4f0f32d8d7aecf02de278f43d9e007cd451a58b7992fba` |

Dirty output exceeds the clean base by 90 exact duplicate rows and 65 near-duplicate rows.

## Seeded business patterns

1. Branch footprint: 15 Ghana locations; branches 1-10 are full-service, 11-13 sales-only, and 14-15 service-only. Branch selection is capacity-weighted, creating persistent size differences.
2. Product catalogue: 18 fictional product lines across model years 2023-2025, producing 54 model/trim rows. SUVs are most popular; vans are lowest volume.
3. Sales seasonality multipliers: Jan .84, Feb .96, Mar 1.10, Apr 1.14, May 1.00, Jun .96, Jul .91, Aug .95, Sep 1.00, Oct 1.04, Nov 1.10, Dec 1.31.
4. Sales trend multipliers: 2023 1.00, 2024 1.08, 2025 H1 1.13. The data therefore contains trend plus random variation, not fixed monthly targets.
5. Apr-May 2024 supply constraint: inventory acquired in these months receives an extra 18-35 arrival lead days.
6. Inventory aging: sale discounts increase after 75 days in stock and are capped at 18%; outgoing/older stock therefore tends to have lower realized prices.
7. Channel mix: showroom dominates; website leads are second; fleet business is concentrated indirectly through the seasonal sales distribution.
8. Service behavior: service likelihood is weighted by vehicle exposure time; scheduled work dominates and repair/body work has longer duration and higher parts cost.
9. Reliability signal: model_ids 14, 15, 31, and 32 have 4.5x warranty-claim selection weight; repair/recall visits have 2x weight and ordinary service .45x.
10. Warranty outcomes: seeded weights are 65% approved, 15% partially approved, and 20% denied; transmission and battery claims receive 10-28 extra resolution days.
11. Complaint drivers: service-delay complaints are common after workshop interactions; warranty-source complaints are explicitly categorized as warranty complaints.
12. Satisfaction drivers: cancelled/returned sales, open or repeat service work, and unresolved complaints lower scores. Interactions from 2024-10-01 gain a +0.35 process-improvement effect.
13. Survey response mix is 40% post-sale, 48% post-service, and 12% complaint follow-up by generation weight; randomness makes realized counts vary.

## Injected defect totals

| Defect type | Exact count | Tables affected |
|---|---:|---|
| `name_variants` | 140 | branches: 10, models: 40, salespeople: 90 |
| `exact_duplicate_rows` | 90 | sales: 20, service_records: 35, warranty_claims: 12, complaints: 8, satisfaction: 15 |
| `near_duplicate_records` | 65 | sales: 20, service_records: 25, warranty_claims: 8, complaints: 5, satisfaction: 7 |
| `missing_prices_or_costs` | 180 | inventory: 65, sales: 55, service_records: 40, warranty_claims: 20 |
| `invalid_dates` | 110 | sales: 35, service_records: 30, warranty_claims: 20, complaints: 15, satisfaction: 10 |
| `negative_costs_or_prices` | 75 | inventory: 20, sales: 15, service_records: 20, warranty_claims: 10, complaints: 10 |
| `orphan_foreign_keys` | 85 | salespeople: 8, inventory: 22, sales: 15, service_records: 15, warranty_claims: 10, complaints: 8, satisfaction: 7 |
| `duplicate_vins` | 28 | inventory: 28 |
| `malformed_vins` | 35 | inventory: 35 |
| `inconsistent_category_labels` | 135 | branches: 8, inventory: 25, sales: 30, service_records: 30, complaints: 22, satisfaction: 20 |
| `missing_required_descriptive_values` | 100 | branches: 8, models: 12, salespeople: 20, inventory: 15, sales: 15, service_records: 15, warranty_claims: 8, complaints: 7 |
| `arithmetic_inconsistencies` | 95 | sales: 50, service_records: 30, warranty_claims: 15 |
| `invalid_satisfaction_scores` | 45 | satisfaction: 45 |
| `status_date_contradictions` | 60 | inventory: 20, warranty_claims: 20, complaints: 20 |
| `implausible_mileage_or_labor_hours` | 48 | service_records: 48 |

Total injected defect instances: **1,291**.

Counts are defect instances, not necessarily distinct rows. Exact duplicates share a primary key with their source row; near duplicates have new surrogate keys.

## Complete injected-defect ledger

Every intentional corruption is listed below. Record IDs refer to the dirty CSV value in that table's primary-key column.

| # | Defect type | Table | Record ID | Field | Detail |
|---:|---|---|---:|---|---|
| 1 | `name_variants` | `branches` | `8` | `branch_name` | 'versalMotors Tamale' -> 'VERSALMOTORS TAMALE' |
| 2 | `name_variants` | `branches` | `13` | `branch_name` | 'versalMotors Wa' -> 'versalmotors wa' |
| 3 | `name_variants` | `branches` | `4` | `branch_name` | 'versalMotors Kumasi Central' -> 'versalMotors-Kumasi-Central' |
| 4 | `name_variants` | `branches` | `7` | `branch_name` | 'versalMotors Cape Coast' -> 'versalMotors Cape Coast ' |
| 5 | `name_variants` | `branches` | `5` | `branch_name` | 'versalMotors Suame' -> 'Versal Motors Suame' |
| 6 | `name_variants` | `branches` | `9` | `branch_name` | 'versalMotors Koforidua' -> 'VERSALMOTORS KOFORIDUA' |
| 7 | `name_variants` | `branches` | `3` | `branch_name` | 'versalMotors East Legon' -> 'versalmotors east legon' |
| 8 | `name_variants` | `branches` | `10` | `branch_name` | 'versalMotors Ho' -> 'versalMotors-Ho' |
| 9 | `name_variants` | `branches` | `6` | `branch_name` | 'versalMotors Takoradi' -> 'versalMotors Takoradi ' |
| 10 | `name_variants` | `branches` | `2` | `branch_name` | 'versalMotors Tema Harbour' -> 'Versal Motors Tema Harbour' |
| 11 | `name_variants` | `models` | `49` | `model_name` | 'Workstar' -> 'WORKSTAR' |
| 12 | `name_variants` | `models` | `21` | `model_name` | 'Metro' -> 'metro' |
| 13 | `name_variants` | `models` | `6` | `model_name` | 'Luma Cross' -> 'Luma-Cross' |
| 14 | `name_variants` | `models` | `33` | `model_name` | 'Sahara' -> 'Sahara ' |
| 15 | `name_variants` | `models` | `51` | `model_name` | 'Workstar' -> 'Workstar' |
| 16 | `name_variants` | `models` | `30` | `model_name` | 'Ranger' -> 'RANGER' |
| 17 | `name_variants` | `models` | `40` | `model_name` | 'Eon X' -> 'eon x' |
| 18 | `name_variants` | `models` | `24` | `model_name` | 'Voyager' -> 'Voyager' |
| 19 | `name_variants` | `models` | `12` | `model_name` | 'Atlas' -> 'Atlas ' |
| 20 | `name_variants` | `models` | `53` | `model_name` | 'Familia' -> 'Familia' |
| 21 | `name_variants` | `models` | `44` | `model_name` | 'Spark' -> 'SPARK' |
| 22 | `name_variants` | `models` | `13` | `model_name` | 'Atlas Sport' -> 'atlas sport' |
| 23 | `name_variants` | `models` | `18` | `model_name` | 'Terra' -> 'Terra' |
| 24 | `name_variants` | `models` | `2` | `model_name` | 'Luma' -> 'Luma ' |
| 25 | `name_variants` | `models` | `25` | `model_name` | 'Pulse' -> 'Pulse' |
| 26 | `name_variants` | `models` | `38` | `model_name` | 'Eon' -> 'EON' |
| 27 | `name_variants` | `models` | `52` | `model_name` | 'Familia' -> 'familia' |
| 28 | `name_variants` | `models` | `1` | `model_name` | 'Luma' -> 'Luma' |
| 29 | `name_variants` | `models` | `9` | `model_name` | 'Vela' -> 'Vela ' |
| 30 | `name_variants` | `models` | `47` | `model_name` | 'Cargo' -> 'Cargo' |
| 31 | `name_variants` | `models` | `50` | `model_name` | 'Workstar' -> 'WORKSTAR' |
| 32 | `name_variants` | `models` | `27` | `model_name` | 'Pulse' -> 'pulse' |
| 33 | `name_variants` | `models` | `10` | `model_name` | 'Atlas' -> 'Atlas' |
| 34 | `name_variants` | `models` | `3` | `model_name` | 'Luma' -> 'Luma ' |
| 35 | `name_variants` | `models` | `35` | `model_name` | 'Trail' -> 'Trail' |
| 36 | `name_variants` | `models` | `17` | `model_name` | 'Terra' -> 'TERRA' |
| 37 | `name_variants` | `models` | `32` | `model_name` | 'Sahara' -> 'sahara' |
| 38 | `name_variants` | `models` | `43` | `model_name` | 'Spark' -> 'Spark' |
| 39 | `name_variants` | `models` | `41` | `model_name` | 'Eon X' -> 'Eon X ' |
| 40 | `name_variants` | `models` | `8` | `model_name` | 'Vela' -> 'Vela' |
| 41 | `name_variants` | `models` | `46` | `model_name` | 'Cargo' -> 'CARGO' |
| 42 | `name_variants` | `models` | `20` | `model_name` | 'Metro' -> 'metro' |
| 43 | `name_variants` | `models` | `54` | `model_name` | 'Familia' -> 'Familia' |
| 44 | `name_variants` | `models` | `5` | `model_name` | 'Luma Cross' -> 'Luma Cross ' |
| 45 | `name_variants` | `models` | `7` | `model_name` | 'Vela' -> 'Vela' |
| 46 | `name_variants` | `models` | `34` | `model_name` | 'Trail' -> 'TRAIL' |
| 47 | `name_variants` | `models` | `16` | `model_name` | 'Terra' -> 'terra' |
| 48 | `name_variants` | `models` | `15` | `model_name` | 'Atlas Sport' -> 'Atlas-Sport' |
| 49 | `name_variants` | `models` | `4` | `model_name` | 'Luma Cross' -> 'Luma Cross ' |
| 50 | `name_variants` | `models` | `42` | `model_name` | 'Eon X' -> 'Eon X' |
| 51 | `name_variants` | `salespeople` | `127` | `last_name` | 'Boateng' -> 'BOATENG' |
| 52 | `name_variants` | `salespeople` | `143` | `last_name` | 'Asare' -> 'asare' |
| 53 | `name_variants` | `salespeople` | `86` | `last_name` | 'Tetteh' -> 'Tetteh' |
| 54 | `name_variants` | `salespeople` | `4` | `last_name` | 'Amankwah' -> 'Amankwah ' |
| 55 | `name_variants` | `salespeople` | `91` | `last_name` | 'Osei' -> 'Osei' |
| 56 | `name_variants` | `salespeople` | `172` | `last_name` | 'Boateng' -> 'BOATENG' |
| 57 | `name_variants` | `salespeople` | `153` | `last_name` | 'Tetteh' -> 'tetteh' |
| 58 | `name_variants` | `salespeople` | `222` | `last_name` | 'Darko' -> 'Darko' |
| 59 | `name_variants` | `salespeople` | `95` | `last_name` | 'Owusu' -> 'Owusu ' |
| 60 | `name_variants` | `salespeople` | `198` | `last_name` | 'Agyeman' -> 'Agyeman' |
| 61 | `name_variants` | `salespeople` | `218` | `last_name` | 'Mensah' -> 'MENSAH' |
| 62 | `name_variants` | `salespeople` | `114` | `last_name` | 'Opoku' -> 'opoku' |
| 63 | `name_variants` | `salespeople` | `147` | `last_name` | 'Frimpong' -> 'Frimpong' |
| 64 | `name_variants` | `salespeople` | `56` | `last_name` | 'Asare' -> 'Asare ' |
| 65 | `name_variants` | `salespeople` | `92` | `last_name` | 'Antwi' -> 'Antwi' |
| 66 | `name_variants` | `salespeople` | `155` | `last_name` | 'Sarpong' -> 'SARPONG' |
| 67 | `name_variants` | `salespeople` | `220` | `last_name` | 'Arthur' -> 'arthur' |
| 68 | `name_variants` | `salespeople` | `73` | `last_name` | 'Addo' -> 'Addo' |
| 69 | `name_variants` | `salespeople` | `1` | `last_name` | 'Acheampong' -> 'Acheampong ' |
| 70 | `name_variants` | `salespeople` | `142` | `last_name` | 'Amankwah' -> 'Amankwah' |
| 71 | `name_variants` | `salespeople` | `51` | `last_name` | 'Boateng' -> 'BOATENG' |
| 72 | `name_variants` | `salespeople` | `72` | `last_name` | 'Gyasi' -> 'gyasi' |
| 73 | `name_variants` | `salespeople` | `3` | `last_name` | 'Sarpong' -> 'Sarpong' |
| 74 | `name_variants` | `salespeople` | `71` | `last_name` | 'Boateng' -> 'Boateng ' |
| 75 | `name_variants` | `salespeople` | `186` | `last_name` | 'Darko' -> 'Darko' |
| 76 | `name_variants` | `salespeople` | `216` | `last_name` | 'Arthur' -> 'ARTHUR' |
| 77 | `name_variants` | `salespeople` | `59` | `last_name` | 'Addo' -> 'addo' |
| 78 | `name_variants` | `salespeople` | `149` | `last_name` | 'Opoku' -> 'Opoku' |
| 79 | `name_variants` | `salespeople` | `89` | `last_name` | 'Appiah' -> 'Appiah ' |
| 80 | `name_variants` | `salespeople` | `87` | `last_name` | 'Asare' -> 'Asare' |
| 81 | `name_variants` | `salespeople` | `38` | `last_name` | 'Sarpong' -> 'SARPONG' |
| 82 | `name_variants` | `salespeople` | `129` | `last_name` | 'Badu' -> 'badu' |
| 83 | `name_variants` | `salespeople` | `61` | `last_name` | 'Tetteh' -> 'Tetteh' |
| 84 | `name_variants` | `salespeople` | `101` | `last_name` | 'Mensah' -> 'Mensah ' |
| 85 | `name_variants` | `salespeople` | `22` | `last_name` | 'Frimpong' -> 'Frimpong' |
| 86 | `name_variants` | `salespeople` | `168` | `last_name` | 'Frimpong' -> 'FRIMPONG' |
| 87 | `name_variants` | `salespeople` | `28` | `last_name` | 'Darko' -> 'darko' |
| 88 | `name_variants` | `salespeople` | `131` | `last_name` | 'Addo' -> 'Addo' |
| 89 | `name_variants` | `salespeople` | `182` | `last_name` | 'Addo' -> 'Addo ' |
| 90 | `name_variants` | `salespeople` | `37` | `last_name` | 'Amankwah' -> 'Amankwah' |
| 91 | `name_variants` | `salespeople` | `30` | `last_name` | 'Mensah' -> 'MENSAH' |
| 92 | `name_variants` | `salespeople` | `150` | `last_name` | 'Sarpong' -> 'sarpong' |
| 93 | `name_variants` | `salespeople` | `205` | `last_name` | 'Quaye' -> 'Quaye' |
| 94 | `name_variants` | `salespeople` | `210` | `last_name` | 'Mensah' -> 'Mensah ' |
| 95 | `name_variants` | `salespeople` | `6` | `last_name` | 'Opoku' -> 'Opoku' |
| 96 | `name_variants` | `salespeople` | `40` | `last_name` | 'Tetteh' -> 'TETTEH' |
| 97 | `name_variants` | `salespeople` | `36` | `last_name` | 'Sarpong' -> 'sarpong' |
| 98 | `name_variants` | `salespeople` | `204` | `last_name` | 'Quaye' -> 'Quaye' |
| 99 | `name_variants` | `salespeople` | `190` | `last_name` | 'Osei' -> 'Osei ' |
| 100 | `name_variants` | `salespeople` | `177` | `last_name` | 'Appiah' -> 'Appiah' |
| 101 | `name_variants` | `salespeople` | `211` | `last_name` | 'Mensah' -> 'MENSAH' |
| 102 | `name_variants` | `salespeople` | `46` | `last_name` | 'Opoku' -> 'opoku' |
| 103 | `name_variants` | `salespeople` | `158` | `last_name` | 'Quaye' -> 'Quaye' |
| 104 | `name_variants` | `salespeople` | `60` | `last_name` | 'Amankwah' -> 'Amankwah ' |
| 105 | `name_variants` | `salespeople` | `176` | `last_name` | 'Badu' -> 'Badu' |
| 106 | `name_variants` | `salespeople` | `10` | `last_name` | 'Addo' -> 'ADDO' |
| 107 | `name_variants` | `salespeople` | `52` | `last_name` | 'Arthur' -> 'arthur' |
| 108 | `name_variants` | `salespeople` | `174` | `last_name` | 'Frimpong' -> 'Frimpong' |
| 109 | `name_variants` | `salespeople` | `98` | `last_name` | 'Amankwah' -> 'Amankwah ' |
| 110 | `name_variants` | `salespeople` | `41` | `last_name` | 'Darko' -> 'Darko' |
| 111 | `name_variants` | `salespeople` | `64` | `last_name` | 'Opoku' -> 'OPOKU' |
| 112 | `name_variants` | `salespeople` | `188` | `last_name` | 'Appiah' -> 'appiah' |
| 113 | `name_variants` | `salespeople` | `24` | `last_name` | 'Amankwah' -> 'Amankwah' |
| 114 | `name_variants` | `salespeople` | `223` | `last_name` | 'Osei' -> 'Osei ' |
| 115 | `name_variants` | `salespeople` | `35` | `last_name` | 'Arthur' -> 'Arthur' |
| 116 | `name_variants` | `salespeople` | `215` | `last_name` | 'Appiah' -> 'APPIAH' |
| 117 | `name_variants` | `salespeople` | `55` | `last_name` | 'Asare' -> 'asare' |
| 118 | `name_variants` | `salespeople` | `130` | `last_name` | 'Antwi' -> 'Antwi' |
| 119 | `name_variants` | `salespeople` | `164` | `last_name` | 'Opoku' -> 'Opoku ' |
| 120 | `name_variants` | `salespeople` | `195` | `last_name` | 'Asare' -> 'Asare' |
| 121 | `name_variants` | `salespeople` | `13` | `last_name` | 'Arthur' -> 'ARTHUR' |
| 122 | `name_variants` | `salespeople` | `76` | `last_name` | 'Gyasi' -> 'gyasi' |
| 123 | `name_variants` | `salespeople` | `20` | `last_name` | 'Acheampong' -> 'Acheampong' |
| 124 | `name_variants` | `salespeople` | `82` | `last_name` | 'Quaye' -> 'Quaye ' |
| 125 | `name_variants` | `salespeople` | `103` | `last_name` | 'Badu' -> 'Badu' |
| 126 | `name_variants` | `salespeople` | `34` | `last_name` | 'Addo' -> 'ADDO' |
| 127 | `name_variants` | `salespeople` | `58` | `last_name` | 'Arthur' -> 'arthur' |
| 128 | `name_variants` | `salespeople` | `212` | `last_name` | 'Arthur' -> 'Arthur' |
| 129 | `name_variants` | `salespeople` | `125` | `last_name` | 'Gyasi' -> 'Gyasi ' |
| 130 | `name_variants` | `salespeople` | `179` | `last_name` | 'Asare' -> 'Asare' |
| 131 | `name_variants` | `salespeople` | `116` | `last_name` | 'Owusu' -> 'OWUSU' |
| 132 | `name_variants` | `salespeople` | `175` | `last_name` | 'Frimpong' -> 'frimpong' |
| 133 | `name_variants` | `salespeople` | `197` | `last_name` | 'Badu' -> 'Badu' |
| 134 | `name_variants` | `salespeople` | `121` | `last_name` | 'Darko' -> 'Darko ' |
| 135 | `name_variants` | `salespeople` | `145` | `last_name` | 'Darko' -> 'Darko' |
| 136 | `name_variants` | `salespeople` | `12` | `last_name` | 'Agyeman' -> 'AGYEMAN' |
| 137 | `name_variants` | `salespeople` | `66` | `last_name` | 'Gyasi' -> 'gyasi' |
| 138 | `name_variants` | `salespeople` | `50` | `last_name` | 'Badu' -> 'Badu' |
| 139 | `name_variants` | `salespeople` | `31` | `last_name` | 'Osei' -> 'Osei ' |
| 140 | `name_variants` | `salespeople` | `171` | `last_name` | 'Frimpong' -> 'Frimpong' |
| 141 | `missing_prices_or_costs` | `inventory` | `5188` | `listed_price` | removed 462248.75 |
| 142 | `missing_prices_or_costs` | `inventory` | `948` | `listed_price` | removed 343202.27 |
| 143 | `missing_prices_or_costs` | `inventory` | `23117` | `listed_price` | removed 364015.28 |
| 144 | `missing_prices_or_costs` | `inventory` | `13747` | `listed_price` | removed 175331.20 |
| 145 | `missing_prices_or_costs` | `inventory` | `22148` | `listed_price` | removed 328227.83 |
| 146 | `missing_prices_or_costs` | `inventory` | `13503` | `listed_price` | removed 273944.01 |
| 147 | `missing_prices_or_costs` | `inventory` | `2632` | `listed_price` | removed 350462.50 |
| 148 | `missing_prices_or_costs` | `inventory` | `17725` | `listed_price` | removed 200165.84 |
| 149 | `missing_prices_or_costs` | `inventory` | `21959` | `listed_price` | removed 333203.14 |
| 150 | `missing_prices_or_costs` | `inventory` | `19234` | `listed_price` | removed 238804.76 |
| 151 | `missing_prices_or_costs` | `inventory` | `12728` | `listed_price` | removed 183657.41 |
| 152 | `missing_prices_or_costs` | `inventory` | `19733` | `listed_price` | removed 321938.45 |
| 153 | `missing_prices_or_costs` | `inventory` | `24902` | `listed_price` | removed 260015.38 |
| 154 | `missing_prices_or_costs` | `inventory` | `6798` | `listed_price` | removed 282566.89 |
| 155 | `missing_prices_or_costs` | `inventory` | `12268` | `listed_price` | removed 276913.87 |
| 156 | `missing_prices_or_costs` | `inventory` | `10563` | `listed_price` | removed 168518.32 |
| 157 | `missing_prices_or_costs` | `inventory` | `7490` | `listed_price` | removed 209089.08 |
| 158 | `missing_prices_or_costs` | `inventory` | `14337` | `listed_price` | removed 387002.62 |
| 159 | `missing_prices_or_costs` | `inventory` | `9082` | `listed_price` | removed 353138.53 |
| 160 | `missing_prices_or_costs` | `inventory` | `14356` | `listed_price` | removed 465905.46 |
| 161 | `missing_prices_or_costs` | `inventory` | `20739` | `listed_price` | removed 242690.27 |
| 162 | `missing_prices_or_costs` | `inventory` | `9369` | `listed_price` | removed 329348.70 |
| 163 | `missing_prices_or_costs` | `inventory` | `6648` | `listed_price` | removed 211449.84 |
| 164 | `missing_prices_or_costs` | `inventory` | `23925` | `listed_price` | removed 264232.36 |
| 165 | `missing_prices_or_costs` | `inventory` | `16410` | `listed_price` | removed 339176.29 |
| 166 | `missing_prices_or_costs` | `inventory` | `22364` | `listed_price` | removed 380575.10 |
| 167 | `missing_prices_or_costs` | `inventory` | `3540` | `listed_price` | removed 326024.48 |
| 168 | `missing_prices_or_costs` | `inventory` | `17471` | `listed_price` | removed 335017.48 |
| 169 | `missing_prices_or_costs` | `inventory` | `20040` | `listed_price` | removed 187242.34 |
| 170 | `missing_prices_or_costs` | `inventory` | `856` | `listed_price` | removed 278612.78 |
| 171 | `missing_prices_or_costs` | `inventory` | `24707` | `listed_price` | removed 184333.24 |
| 172 | `missing_prices_or_costs` | `inventory` | `22904` | `listed_price` | removed 347838.49 |
| 173 | `missing_prices_or_costs` | `inventory` | `443` | `listed_price` | removed 322597.54 |
| 174 | `missing_prices_or_costs` | `inventory` | `20838` | `listed_price` | removed 203239.93 |
| 175 | `missing_prices_or_costs` | `inventory` | `15027` | `listed_price` | removed 322833.88 |
| 176 | `missing_prices_or_costs` | `inventory` | `21983` | `acquisition_cost` | removed 193975.87 |
| 177 | `missing_prices_or_costs` | `inventory` | `20104` | `acquisition_cost` | removed 235654.70 |
| 178 | `missing_prices_or_costs` | `inventory` | `15956` | `acquisition_cost` | removed 378149.52 |
| 179 | `missing_prices_or_costs` | `inventory` | `581` | `acquisition_cost` | removed 223314.58 |
| 180 | `missing_prices_or_costs` | `inventory` | `23415` | `acquisition_cost` | removed 314829.86 |
| 181 | `missing_prices_or_costs` | `inventory` | `8590` | `acquisition_cost` | removed 287330.16 |
| 182 | `missing_prices_or_costs` | `inventory` | `4231` | `acquisition_cost` | removed 279537.18 |
| 183 | `missing_prices_or_costs` | `inventory` | `16302` | `acquisition_cost` | removed 160632.27 |
| 184 | `missing_prices_or_costs` | `inventory` | `22688` | `acquisition_cost` | removed 144712.21 |
| 185 | `missing_prices_or_costs` | `inventory` | `9925` | `acquisition_cost` | removed 277152.22 |
| 186 | `missing_prices_or_costs` | `inventory` | `11079` | `acquisition_cost` | removed 182868.23 |
| 187 | `missing_prices_or_costs` | `inventory` | `14668` | `acquisition_cost` | removed 279235.56 |
| 188 | `missing_prices_or_costs` | `inventory` | `24841` | `acquisition_cost` | removed 206590.22 |
| 189 | `missing_prices_or_costs` | `inventory` | `16` | `acquisition_cost` | removed 279423.98 |
| 190 | `missing_prices_or_costs` | `inventory` | `17912` | `acquisition_cost` | removed 313846.42 |
| 191 | `missing_prices_or_costs` | `inventory` | `6783` | `acquisition_cost` | removed 232921.95 |
| 192 | `missing_prices_or_costs` | `inventory` | `16962` | `acquisition_cost` | removed 237552.99 |
| 193 | `missing_prices_or_costs` | `inventory` | `3294` | `acquisition_cost` | removed 240516.02 |
| 194 | `missing_prices_or_costs` | `inventory` | `16111` | `acquisition_cost` | removed 293018.30 |
| 195 | `missing_prices_or_costs` | `inventory` | `11186` | `acquisition_cost` | removed 284970.72 |
| 196 | `missing_prices_or_costs` | `inventory` | `5902` | `acquisition_cost` | removed 237940.43 |
| 197 | `missing_prices_or_costs` | `inventory` | `19428` | `acquisition_cost` | removed 216225.98 |
| 198 | `missing_prices_or_costs` | `inventory` | `15880` | `acquisition_cost` | removed 114640.63 |
| 199 | `missing_prices_or_costs` | `inventory` | `23737` | `acquisition_cost` | removed 279810.18 |
| 200 | `missing_prices_or_costs` | `inventory` | `13554` | `acquisition_cost` | removed 290908.85 |
| 201 | `missing_prices_or_costs` | `inventory` | `4620` | `acquisition_cost` | removed 189445.35 |
| 202 | `missing_prices_or_costs` | `inventory` | `13307` | `acquisition_cost` | removed 266740.38 |
| 203 | `missing_prices_or_costs` | `inventory` | `11822` | `acquisition_cost` | removed 232103.64 |
| 204 | `missing_prices_or_costs` | `inventory` | `408` | `acquisition_cost` | removed 263210.24 |
| 205 | `missing_prices_or_costs` | `inventory` | `658` | `acquisition_cost` | removed 367573.43 |
| 206 | `missing_prices_or_costs` | `sales` | `10818` | `total_sale_price` | removed 254885.19 |
| 207 | `missing_prices_or_costs` | `sales` | `6000` | `total_sale_price` | removed 380420.05 |
| 208 | `missing_prices_or_costs` | `sales` | `1884` | `total_sale_price` | removed 284737.84 |
| 209 | `missing_prices_or_costs` | `sales` | `19496` | `total_sale_price` | removed 310726.94 |
| 210 | `missing_prices_or_costs` | `sales` | `12120` | `total_sale_price` | removed 351459.92 |
| 211 | `missing_prices_or_costs` | `sales` | `11493` | `total_sale_price` | removed 382886.64 |
| 212 | `missing_prices_or_costs` | `sales` | `13460` | `total_sale_price` | removed 219146.59 |
| 213 | `missing_prices_or_costs` | `sales` | `9443` | `total_sale_price` | removed 268015.03 |
| 214 | `missing_prices_or_costs` | `sales` | `7069` | `total_sale_price` | removed 444649.79 |
| 215 | `missing_prices_or_costs` | `sales` | `4085` | `total_sale_price` | removed 202635.81 |
| 216 | `missing_prices_or_costs` | `sales` | `261` | `total_sale_price` | removed 504678.74 |
| 217 | `missing_prices_or_costs` | `sales` | `19113` | `total_sale_price` | removed 278766.84 |
| 218 | `missing_prices_or_costs` | `sales` | `20300` | `total_sale_price` | removed 288592.79 |
| 219 | `missing_prices_or_costs` | `sales` | `271` | `total_sale_price` | removed 372706.27 |
| 220 | `missing_prices_or_costs` | `sales` | `15141` | `total_sale_price` | removed 253034.87 |
| 221 | `missing_prices_or_costs` | `sales` | `5488` | `total_sale_price` | removed 374791.75 |
| 222 | `missing_prices_or_costs` | `sales` | `5561` | `total_sale_price` | removed 270890.94 |
| 223 | `missing_prices_or_costs` | `sales` | `8392` | `total_sale_price` | removed 216977.62 |
| 224 | `missing_prices_or_costs` | `sales` | `11855` | `total_sale_price` | removed 293339.74 |
| 225 | `missing_prices_or_costs` | `sales` | `17760` | `total_sale_price` | removed 339095.60 |
| 226 | `missing_prices_or_costs` | `sales` | `8961` | `total_sale_price` | removed 263519.56 |
| 227 | `missing_prices_or_costs` | `sales` | `7675` | `total_sale_price` | removed 220856.58 |
| 228 | `missing_prices_or_costs` | `sales` | `7377` | `total_sale_price` | removed 370154.81 |
| 229 | `missing_prices_or_costs` | `sales` | `19068` | `total_sale_price` | removed 328048.26 |
| 230 | `missing_prices_or_costs` | `sales` | `16636` | `total_sale_price` | removed 372117.17 |
| 231 | `missing_prices_or_costs` | `sales` | `15331` | `total_sale_price` | removed 499077.79 |
| 232 | `missing_prices_or_costs` | `sales` | `8906` | `total_sale_price` | removed 272450.50 |
| 233 | `missing_prices_or_costs` | `sales` | `15864` | `total_sale_price` | removed 417732.33 |
| 234 | `missing_prices_or_costs` | `sales` | `16943` | `total_sale_price` | removed 391364.95 |
| 235 | `missing_prices_or_costs` | `sales` | `7219` | `total_sale_price` | removed 369223.27 |
| 236 | `missing_prices_or_costs` | `sales` | `2293` | `total_sale_price` | removed 261572.30 |
| 237 | `missing_prices_or_costs` | `sales` | `12080` | `total_sale_price` | removed 383507.40 |
| 238 | `missing_prices_or_costs` | `sales` | `264` | `total_sale_price` | removed 355908.11 |
| 239 | `missing_prices_or_costs` | `sales` | `576` | `total_sale_price` | removed 313018.75 |
| 240 | `missing_prices_or_costs` | `sales` | `20094` | `total_sale_price` | removed 262569.12 |
| 241 | `missing_prices_or_costs` | `sales` | `5289` | `total_sale_price` | removed 266778.18 |
| 242 | `missing_prices_or_costs` | `sales` | `1047` | `total_sale_price` | removed 424949.18 |
| 243 | `missing_prices_or_costs` | `sales` | `6041` | `total_sale_price` | removed 375491.23 |
| 244 | `missing_prices_or_costs` | `sales` | `9465` | `total_sale_price` | removed 433726.36 |
| 245 | `missing_prices_or_costs` | `sales` | `7841` | `total_sale_price` | removed 252063.47 |
| 246 | `missing_prices_or_costs` | `sales` | `5704` | `total_sale_price` | removed 447504.17 |
| 247 | `missing_prices_or_costs` | `sales` | `6930` | `total_sale_price` | removed 341050.93 |
| 248 | `missing_prices_or_costs` | `sales` | `10024` | `total_sale_price` | removed 342496.16 |
| 249 | `missing_prices_or_costs` | `sales` | `14790` | `total_sale_price` | removed 355254.52 |
| 250 | `missing_prices_or_costs` | `sales` | `16950` | `total_sale_price` | removed 343228.27 |
| 251 | `missing_prices_or_costs` | `sales` | `3870` | `total_sale_price` | removed 367871.20 |
| 252 | `missing_prices_or_costs` | `sales` | `17805` | `total_sale_price` | removed 168269.95 |
| 253 | `missing_prices_or_costs` | `sales` | `16154` | `total_sale_price` | removed 363478.42 |
| 254 | `missing_prices_or_costs` | `sales` | `9566` | `total_sale_price` | removed 317895.53 |
| 255 | `missing_prices_or_costs` | `sales` | `20156` | `total_sale_price` | removed 449985.41 |
| 256 | `missing_prices_or_costs` | `sales` | `11160` | `total_sale_price` | removed 376764.88 |
| 257 | `missing_prices_or_costs` | `sales` | `9052` | `total_sale_price` | removed 383349.52 |
| 258 | `missing_prices_or_costs` | `sales` | `9889` | `total_sale_price` | removed 338538.06 |
| 259 | `missing_prices_or_costs` | `sales` | `11182` | `total_sale_price` | removed 308324.85 |
| 260 | `missing_prices_or_costs` | `sales` | `3567` | `total_sale_price` | removed 364588.59 |
| 261 | `missing_prices_or_costs` | `service_records` | `35643` | `total_service_cost` | removed 3446.80 |
| 262 | `missing_prices_or_costs` | `service_records` | `42837` | `total_service_cost` | removed 988.14 |
| 263 | `missing_prices_or_costs` | `service_records` | `16315` | `total_service_cost` | removed 727.92 |
| 264 | `missing_prices_or_costs` | `service_records` | `17512` | `total_service_cost` | removed 768.81 |
| 265 | `missing_prices_or_costs` | `service_records` | `30417` | `total_service_cost` | removed 1653.68 |
| 266 | `missing_prices_or_costs` | `service_records` | `33036` | `total_service_cost` | removed 3843.73 |
| 267 | `missing_prices_or_costs` | `service_records` | `3568` | `total_service_cost` | removed 491.46 |
| 268 | `missing_prices_or_costs` | `service_records` | `29914` | `total_service_cost` | removed 1329.32 |
| 269 | `missing_prices_or_costs` | `service_records` | `29237` | `total_service_cost` | removed 657.16 |
| 270 | `missing_prices_or_costs` | `service_records` | `33271` | `total_service_cost` | removed 619.05 |
| 271 | `missing_prices_or_costs` | `service_records` | `36807` | `total_service_cost` | removed 693.84 |
| 272 | `missing_prices_or_costs` | `service_records` | `45822` | `total_service_cost` | removed 1674.05 |
| 273 | `missing_prices_or_costs` | `service_records` | `10205` | `total_service_cost` | removed 764.75 |
| 274 | `missing_prices_or_costs` | `service_records` | `25850` | `total_service_cost` | removed 1621.16 |
| 275 | `missing_prices_or_costs` | `service_records` | `43182` | `total_service_cost` | removed 3607.73 |
| 276 | `missing_prices_or_costs` | `service_records` | `40183` | `total_service_cost` | removed 600.26 |
| 277 | `missing_prices_or_costs` | `service_records` | `8381` | `total_service_cost` | removed 1046.67 |
| 278 | `missing_prices_or_costs` | `service_records` | `9835` | `total_service_cost` | removed 2435.33 |
| 279 | `missing_prices_or_costs` | `service_records` | `5812` | `total_service_cost` | removed 608.93 |
| 280 | `missing_prices_or_costs` | `service_records` | `7989` | `total_service_cost` | removed 440.36 |
| 281 | `missing_prices_or_costs` | `service_records` | `4355` | `total_service_cost` | removed 2439.55 |
| 282 | `missing_prices_or_costs` | `service_records` | `22543` | `total_service_cost` | removed 1655.92 |
| 283 | `missing_prices_or_costs` | `service_records` | `27035` | `total_service_cost` | removed 1184.55 |
| 284 | `missing_prices_or_costs` | `service_records` | `23688` | `total_service_cost` | removed 582.14 |
| 285 | `missing_prices_or_costs` | `service_records` | `1485` | `total_service_cost` | removed 918.71 |
| 286 | `missing_prices_or_costs` | `service_records` | `44307` | `total_service_cost` | removed 701.20 |
| 287 | `missing_prices_or_costs` | `service_records` | `14626` | `total_service_cost` | removed 1009.03 |
| 288 | `missing_prices_or_costs` | `service_records` | `46496` | `total_service_cost` | removed 3323.58 |
| 289 | `missing_prices_or_costs` | `service_records` | `816` | `total_service_cost` | removed 1302.68 |
| 290 | `missing_prices_or_costs` | `service_records` | `14614` | `total_service_cost` | removed 983.62 |
| 291 | `missing_prices_or_costs` | `service_records` | `17965` | `total_service_cost` | removed 1079.57 |
| 292 | `missing_prices_or_costs` | `service_records` | `1392` | `total_service_cost` | removed 1247.50 |
| 293 | `missing_prices_or_costs` | `service_records` | `3370` | `total_service_cost` | removed 1328.64 |
| 294 | `missing_prices_or_costs` | `service_records` | `1074` | `total_service_cost` | removed 990.96 |
| 295 | `missing_prices_or_costs` | `service_records` | `15508` | `total_service_cost` | removed 2802.34 |
| 296 | `missing_prices_or_costs` | `service_records` | `42569` | `total_service_cost` | removed 584.42 |
| 297 | `missing_prices_or_costs` | `service_records` | `41986` | `total_service_cost` | removed 310.81 |
| 298 | `missing_prices_or_costs` | `service_records` | `29425` | `total_service_cost` | removed 806.36 |
| 299 | `missing_prices_or_costs` | `service_records` | `88` | `total_service_cost` | removed 1655.58 |
| 300 | `missing_prices_or_costs` | `service_records` | `39706` | `total_service_cost` | removed 642.77 |
| 301 | `missing_prices_or_costs` | `warranty_claims` | `1277` | `claim_amount` | removed 922.83 |
| 302 | `missing_prices_or_costs` | `warranty_claims` | `688` | `claim_amount` | removed 471.87 |
| 303 | `missing_prices_or_costs` | `warranty_claims` | `738` | `claim_amount` | removed 740.60 |
| 304 | `missing_prices_or_costs` | `warranty_claims` | `1953` | `claim_amount` | removed 5645.99 |
| 305 | `missing_prices_or_costs` | `warranty_claims` | `2649` | `claim_amount` | removed 3523.26 |
| 306 | `missing_prices_or_costs` | `warranty_claims` | `1331` | `claim_amount` | removed 1165.70 |
| 307 | `missing_prices_or_costs` | `warranty_claims` | `1097` | `claim_amount` | removed 1653.55 |
| 308 | `missing_prices_or_costs` | `warranty_claims` | `777` | `claim_amount` | removed 633.29 |
| 309 | `missing_prices_or_costs` | `warranty_claims` | `2732` | `claim_amount` | removed 813.75 |
| 310 | `missing_prices_or_costs` | `warranty_claims` | `2542` | `claim_amount` | removed 927.99 |
| 311 | `missing_prices_or_costs` | `warranty_claims` | `1315` | `claim_amount` | removed 971.78 |
| 312 | `missing_prices_or_costs` | `warranty_claims` | `1318` | `claim_amount` | removed 2302.59 |
| 313 | `missing_prices_or_costs` | `warranty_claims` | `1838` | `claim_amount` | removed 438.75 |
| 314 | `missing_prices_or_costs` | `warranty_claims` | `2644` | `claim_amount` | removed 2372.76 |
| 315 | `missing_prices_or_costs` | `warranty_claims` | `382` | `claim_amount` | removed 746.80 |
| 316 | `missing_prices_or_costs` | `warranty_claims` | `12` | `claim_amount` | removed 9388.62 |
| 317 | `missing_prices_or_costs` | `warranty_claims` | `1377` | `claim_amount` | removed 493.72 |
| 318 | `missing_prices_or_costs` | `warranty_claims` | `229` | `claim_amount` | removed 451.15 |
| 319 | `missing_prices_or_costs` | `warranty_claims` | `187` | `claim_amount` | removed 5724.19 |
| 320 | `missing_prices_or_costs` | `warranty_claims` | `299` | `claim_amount` | removed 2599.76 |
| 321 | `invalid_dates` | `sales` | `10091` | `sale_date` | sale before inventory arrival |
| 322 | `invalid_dates` | `sales` | `11264` | `sale_date` | sale before inventory arrival |
| 323 | `invalid_dates` | `sales` | `15994` | `sale_date` | sale before inventory arrival |
| 324 | `invalid_dates` | `sales` | `6639` | `sale_date` | sale before inventory arrival |
| 325 | `invalid_dates` | `sales` | `5540` | `sale_date` | sale before inventory arrival |
| 326 | `invalid_dates` | `sales` | `1324` | `sale_date` | sale before inventory arrival |
| 327 | `invalid_dates` | `sales` | `17002` | `sale_date` | sale before inventory arrival |
| 328 | `invalid_dates` | `sales` | `4896` | `sale_date` | sale before inventory arrival |
| 329 | `invalid_dates` | `sales` | `2512` | `sale_date` | sale before inventory arrival |
| 330 | `invalid_dates` | `sales` | `3450` | `sale_date` | sale before inventory arrival |
| 331 | `invalid_dates` | `sales` | `8448` | `sale_date` | sale before inventory arrival |
| 332 | `invalid_dates` | `sales` | `11233` | `sale_date` | sale before inventory arrival |
| 333 | `invalid_dates` | `sales` | `4464` | `sale_date` | sale before inventory arrival |
| 334 | `invalid_dates` | `sales` | `16118` | `sale_date` | sale before inventory arrival |
| 335 | `invalid_dates` | `sales` | `15604` | `sale_date` | sale before inventory arrival |
| 336 | `invalid_dates` | `sales` | `17663` | `sale_date` | sale before inventory arrival |
| 337 | `invalid_dates` | `sales` | `7708` | `sale_date` | sale before inventory arrival |
| 338 | `invalid_dates` | `sales` | `19580` | `sale_date` | sale before inventory arrival |
| 339 | `invalid_dates` | `sales` | `1754` | `sale_date` | sale before inventory arrival |
| 340 | `invalid_dates` | `sales` | `15736` | `sale_date` | sale before inventory arrival |
| 341 | `invalid_dates` | `sales` | `9733` | `sale_date` | sale before inventory arrival |
| 342 | `invalid_dates` | `sales` | `2801` | `sale_date` | sale before inventory arrival |
| 343 | `invalid_dates` | `sales` | `2423` | `sale_date` | sale before inventory arrival |
| 344 | `invalid_dates` | `sales` | `204` | `sale_date` | sale before inventory arrival |
| 345 | `invalid_dates` | `sales` | `10663` | `sale_date` | sale before inventory arrival |
| 346 | `invalid_dates` | `sales` | `20237` | `sale_date` | sale before inventory arrival |
| 347 | `invalid_dates` | `sales` | `3076` | `sale_date` | sale before inventory arrival |
| 348 | `invalid_dates` | `sales` | `1336` | `sale_date` | sale before inventory arrival |
| 349 | `invalid_dates` | `sales` | `15433` | `sale_date` | sale before inventory arrival |
| 350 | `invalid_dates` | `sales` | `19512` | `sale_date` | sale before inventory arrival |
| 351 | `invalid_dates` | `sales` | `20173` | `sale_date` | sale before inventory arrival |
| 352 | `invalid_dates` | `sales` | `16707` | `sale_date` | sale before inventory arrival |
| 353 | `invalid_dates` | `sales` | `17507` | `sale_date` | sale before inventory arrival |
| 354 | `invalid_dates` | `sales` | `6042` | `sale_date` | sale before inventory arrival |
| 355 | `invalid_dates` | `sales` | `18084` | `sale_date` | sale before inventory arrival |
| 356 | `invalid_dates` | `service_records` | `1667` | `service_close_date` | close before open |
| 357 | `invalid_dates` | `service_records` | `21596` | `service_close_date` | close before open |
| 358 | `invalid_dates` | `service_records` | `12547` | `service_close_date` | close before open |
| 359 | `invalid_dates` | `service_records` | `38579` | `service_close_date` | close before open |
| 360 | `invalid_dates` | `service_records` | `18573` | `service_close_date` | close before open |
| 361 | `invalid_dates` | `service_records` | `14660` | `service_close_date` | close before open |
| 362 | `invalid_dates` | `service_records` | `46138` | `service_close_date` | close before open |
| 363 | `invalid_dates` | `service_records` | `12126` | `service_close_date` | close before open |
| 364 | `invalid_dates` | `service_records` | `41575` | `service_close_date` | close before open |
| 365 | `invalid_dates` | `service_records` | `22600` | `service_close_date` | close before open |
| 366 | `invalid_dates` | `service_records` | `27042` | `service_close_date` | close before open |
| 367 | `invalid_dates` | `service_records` | `16469` | `service_close_date` | close before open |
| 368 | `invalid_dates` | `service_records` | `20710` | `service_close_date` | close before open |
| 369 | `invalid_dates` | `service_records` | `13702` | `service_close_date` | close before open |
| 370 | `invalid_dates` | `service_records` | `41538` | `service_close_date` | close before open |
| 371 | `invalid_dates` | `service_records` | `43240` | `service_close_date` | close before open |
| 372 | `invalid_dates` | `service_records` | `36514` | `service_close_date` | close before open |
| 373 | `invalid_dates` | `service_records` | `14616` | `service_close_date` | close before open |
| 374 | `invalid_dates` | `service_records` | `39427` | `service_close_date` | close before open |
| 375 | `invalid_dates` | `service_records` | `41959` | `service_close_date` | close before open |
| 376 | `invalid_dates` | `service_records` | `9302` | `service_close_date` | close before open |
| 377 | `invalid_dates` | `service_records` | `11157` | `service_close_date` | close before open |
| 378 | `invalid_dates` | `service_records` | `25668` | `service_close_date` | close before open |
| 379 | `invalid_dates` | `service_records` | `39954` | `service_close_date` | close before open |
| 380 | `invalid_dates` | `service_records` | `36837` | `service_close_date` | close before open |
| 381 | `invalid_dates` | `service_records` | `113` | `service_close_date` | close before open |
| 382 | `invalid_dates` | `service_records` | `40831` | `service_close_date` | close before open |
| 383 | `invalid_dates` | `service_records` | `6769` | `service_close_date` | close before open |
| 384 | `invalid_dates` | `service_records` | `28648` | `service_close_date` | close before open |
| 385 | `invalid_dates` | `service_records` | `4599` | `service_close_date` | close before open |
| 386 | `invalid_dates` | `warranty_claims` | `2105` | `claim_date` | claim before dataset transaction period |
| 387 | `invalid_dates` | `warranty_claims` | `1248` | `claim_date` | claim before dataset transaction period |
| 388 | `invalid_dates` | `warranty_claims` | `2613` | `claim_date` | claim before dataset transaction period |
| 389 | `invalid_dates` | `warranty_claims` | `1275` | `claim_date` | claim before dataset transaction period |
| 390 | `invalid_dates` | `warranty_claims` | `386` | `claim_date` | claim before dataset transaction period |
| 391 | `invalid_dates` | `warranty_claims` | `1296` | `claim_date` | claim before dataset transaction period |
| 392 | `invalid_dates` | `warranty_claims` | `2423` | `claim_date` | claim before dataset transaction period |
| 393 | `invalid_dates` | `warranty_claims` | `778` | `claim_date` | claim before dataset transaction period |
| 394 | `invalid_dates` | `warranty_claims` | `1010` | `claim_date` | claim before dataset transaction period |
| 395 | `invalid_dates` | `warranty_claims` | `1223` | `claim_date` | claim before dataset transaction period |
| 396 | `invalid_dates` | `warranty_claims` | `166` | `claim_date` | claim before dataset transaction period |
| 397 | `invalid_dates` | `warranty_claims` | `2158` | `claim_date` | claim before dataset transaction period |
| 398 | `invalid_dates` | `warranty_claims` | `1237` | `claim_date` | claim before dataset transaction period |
| 399 | `invalid_dates` | `warranty_claims` | `885` | `claim_date` | claim before dataset transaction period |
| 400 | `invalid_dates` | `warranty_claims` | `908` | `claim_date` | claim before dataset transaction period |
| 401 | `invalid_dates` | `warranty_claims` | `157` | `claim_date` | claim before dataset transaction period |
| 402 | `invalid_dates` | `warranty_claims` | `2434` | `claim_date` | claim before dataset transaction period |
| 403 | `invalid_dates` | `warranty_claims` | `1996` | `claim_date` | claim before dataset transaction period |
| 404 | `invalid_dates` | `warranty_claims` | `407` | `claim_date` | claim before dataset transaction period |
| 405 | `invalid_dates` | `warranty_claims` | `2388` | `claim_date` | claim before dataset transaction period |
| 406 | `invalid_dates` | `complaints` | `1336` | `resolution_date` | resolution before complaint |
| 407 | `invalid_dates` | `complaints` | `1767` | `resolution_date` | resolution before complaint |
| 408 | `invalid_dates` | `complaints` | `965` | `resolution_date` | resolution before complaint |
| 409 | `invalid_dates` | `complaints` | `1573` | `resolution_date` | resolution before complaint |
| 410 | `invalid_dates` | `complaints` | `83` | `resolution_date` | resolution before complaint |
| 411 | `invalid_dates` | `complaints` | `1270` | `resolution_date` | resolution before complaint |
| 412 | `invalid_dates` | `complaints` | `983` | `resolution_date` | resolution before complaint |
| 413 | `invalid_dates` | `complaints` | `1446` | `resolution_date` | resolution before complaint |
| 414 | `invalid_dates` | `complaints` | `1511` | `resolution_date` | resolution before complaint |
| 415 | `invalid_dates` | `complaints` | `574` | `resolution_date` | resolution before complaint |
| 416 | `invalid_dates` | `complaints` | `1478` | `resolution_date` | resolution before complaint |
| 417 | `invalid_dates` | `complaints` | `1819` | `resolution_date` | resolution before complaint |
| 418 | `invalid_dates` | `complaints` | `1093` | `resolution_date` | resolution before complaint |
| 419 | `invalid_dates` | `complaints` | `1424` | `resolution_date` | resolution before complaint |
| 420 | `invalid_dates` | `complaints` | `1296` | `resolution_date` | resolution before complaint |
| 421 | `invalid_dates` | `satisfaction` | `9131` | `survey_date` | nonexistent calendar date |
| 422 | `invalid_dates` | `satisfaction` | `1720` | `survey_date` | nonexistent calendar date |
| 423 | `invalid_dates` | `satisfaction` | `7097` | `survey_date` | nonexistent calendar date |
| 424 | `invalid_dates` | `satisfaction` | `13764` | `survey_date` | nonexistent calendar date |
| 425 | `invalid_dates` | `satisfaction` | `4127` | `survey_date` | nonexistent calendar date |
| 426 | `invalid_dates` | `satisfaction` | `13148` | `survey_date` | nonexistent calendar date |
| 427 | `invalid_dates` | `satisfaction` | `13509` | `survey_date` | nonexistent calendar date |
| 428 | `invalid_dates` | `satisfaction` | `14717` | `survey_date` | nonexistent calendar date |
| 429 | `invalid_dates` | `satisfaction` | `12797` | `survey_date` | nonexistent calendar date |
| 430 | `invalid_dates` | `satisfaction` | `4690` | `survey_date` | nonexistent calendar date |
| 431 | `negative_costs_or_prices` | `inventory` | `15184` | `acquisition_cost` | positive amount made negative |
| 432 | `negative_costs_or_prices` | `inventory` | `6288` | `acquisition_cost` | positive amount made negative |
| 433 | `negative_costs_or_prices` | `inventory` | `14520` | `acquisition_cost` | positive amount made negative |
| 434 | `negative_costs_or_prices` | `inventory` | `19422` | `acquisition_cost` | positive amount made negative |
| 435 | `negative_costs_or_prices` | `inventory` | `8536` | `acquisition_cost` | positive amount made negative |
| 436 | `negative_costs_or_prices` | `inventory` | `20736` | `acquisition_cost` | positive amount made negative |
| 437 | `negative_costs_or_prices` | `inventory` | `17524` | `acquisition_cost` | positive amount made negative |
| 438 | `negative_costs_or_prices` | `inventory` | `16656` | `acquisition_cost` | positive amount made negative |
| 439 | `negative_costs_or_prices` | `inventory` | `8034` | `acquisition_cost` | positive amount made negative |
| 440 | `negative_costs_or_prices` | `inventory` | `20482` | `acquisition_cost` | positive amount made negative |
| 441 | `negative_costs_or_prices` | `inventory` | `24041` | `acquisition_cost` | positive amount made negative |
| 442 | `negative_costs_or_prices` | `inventory` | `7522` | `acquisition_cost` | positive amount made negative |
| 443 | `negative_costs_or_prices` | `inventory` | `17543` | `acquisition_cost` | positive amount made negative |
| 444 | `negative_costs_or_prices` | `inventory` | `10069` | `acquisition_cost` | positive amount made negative |
| 445 | `negative_costs_or_prices` | `inventory` | `2693` | `acquisition_cost` | positive amount made negative |
| 446 | `negative_costs_or_prices` | `inventory` | `9541` | `acquisition_cost` | positive amount made negative |
| 447 | `negative_costs_or_prices` | `inventory` | `17598` | `acquisition_cost` | positive amount made negative |
| 448 | `negative_costs_or_prices` | `inventory` | `7469` | `acquisition_cost` | positive amount made negative |
| 449 | `negative_costs_or_prices` | `inventory` | `14400` | `acquisition_cost` | positive amount made negative |
| 450 | `negative_costs_or_prices` | `inventory` | `24471` | `acquisition_cost` | positive amount made negative |
| 451 | `negative_costs_or_prices` | `sales` | `7303` | `net_sale_price` | positive amount made negative |
| 452 | `negative_costs_or_prices` | `sales` | `4458` | `net_sale_price` | positive amount made negative |
| 453 | `negative_costs_or_prices` | `sales` | `357` | `net_sale_price` | positive amount made negative |
| 454 | `negative_costs_or_prices` | `sales` | `8623` | `net_sale_price` | positive amount made negative |
| 455 | `negative_costs_or_prices` | `sales` | `18816` | `net_sale_price` | positive amount made negative |
| 456 | `negative_costs_or_prices` | `sales` | `5515` | `net_sale_price` | positive amount made negative |
| 457 | `negative_costs_or_prices` | `sales` | `18003` | `net_sale_price` | positive amount made negative |
| 458 | `negative_costs_or_prices` | `sales` | `8071` | `net_sale_price` | positive amount made negative |
| 459 | `negative_costs_or_prices` | `sales` | `3180` | `net_sale_price` | positive amount made negative |
| 460 | `negative_costs_or_prices` | `sales` | `17950` | `net_sale_price` | positive amount made negative |
| 461 | `negative_costs_or_prices` | `sales` | `9508` | `net_sale_price` | positive amount made negative |
| 462 | `negative_costs_or_prices` | `sales` | `16099` | `net_sale_price` | positive amount made negative |
| 463 | `negative_costs_or_prices` | `sales` | `19959` | `net_sale_price` | positive amount made negative |
| 464 | `negative_costs_or_prices` | `sales` | `12742` | `net_sale_price` | positive amount made negative |
| 465 | `negative_costs_or_prices` | `sales` | `897` | `net_sale_price` | positive amount made negative |
| 466 | `negative_costs_or_prices` | `service_records` | `14732` | `parts_cost` | positive amount made negative |
| 467 | `negative_costs_or_prices` | `service_records` | `29337` | `parts_cost` | positive amount made negative |
| 468 | `negative_costs_or_prices` | `service_records` | `10313` | `parts_cost` | positive amount made negative |
| 469 | `negative_costs_or_prices` | `service_records` | `5340` | `parts_cost` | positive amount made negative |
| 470 | `negative_costs_or_prices` | `service_records` | `11984` | `parts_cost` | positive amount made negative |
| 471 | `negative_costs_or_prices` | `service_records` | `8100` | `parts_cost` | positive amount made negative |
| 472 | `negative_costs_or_prices` | `service_records` | `34334` | `parts_cost` | positive amount made negative |
| 473 | `negative_costs_or_prices` | `service_records` | `21646` | `parts_cost` | positive amount made negative |
| 474 | `negative_costs_or_prices` | `service_records` | `41522` | `parts_cost` | positive amount made negative |
| 475 | `negative_costs_or_prices` | `service_records` | `38624` | `parts_cost` | positive amount made negative |
| 476 | `negative_costs_or_prices` | `service_records` | `5522` | `parts_cost` | positive amount made negative |
| 477 | `negative_costs_or_prices` | `service_records` | `7443` | `parts_cost` | positive amount made negative |
| 478 | `negative_costs_or_prices` | `service_records` | `9881` | `parts_cost` | positive amount made negative |
| 479 | `negative_costs_or_prices` | `service_records` | `8428` | `parts_cost` | positive amount made negative |
| 480 | `negative_costs_or_prices` | `service_records` | `42756` | `parts_cost` | positive amount made negative |
| 481 | `negative_costs_or_prices` | `service_records` | `47423` | `parts_cost` | positive amount made negative |
| 482 | `negative_costs_or_prices` | `service_records` | `46106` | `parts_cost` | positive amount made negative |
| 483 | `negative_costs_or_prices` | `service_records` | `36974` | `parts_cost` | positive amount made negative |
| 484 | `negative_costs_or_prices` | `service_records` | `31388` | `parts_cost` | positive amount made negative |
| 485 | `negative_costs_or_prices` | `service_records` | `32399` | `parts_cost` | positive amount made negative |
| 486 | `negative_costs_or_prices` | `warranty_claims` | `1776` | `approved_amount` | positive amount made negative |
| 487 | `negative_costs_or_prices` | `warranty_claims` | `2093` | `approved_amount` | positive amount made negative |
| 488 | `negative_costs_or_prices` | `warranty_claims` | `642` | `approved_amount` | positive amount made negative |
| 489 | `negative_costs_or_prices` | `warranty_claims` | `1298` | `approved_amount` | positive amount made negative |
| 490 | `negative_costs_or_prices` | `warranty_claims` | `1952` | `approved_amount` | positive amount made negative |
| 491 | `negative_costs_or_prices` | `warranty_claims` | `2992` | `approved_amount` | positive amount made negative |
| 492 | `negative_costs_or_prices` | `warranty_claims` | `1343` | `approved_amount` | positive amount made negative |
| 493 | `negative_costs_or_prices` | `warranty_claims` | `3032` | `approved_amount` | positive amount made negative |
| 494 | `negative_costs_or_prices` | `warranty_claims` | `1484` | `approved_amount` | positive amount made negative |
| 495 | `negative_costs_or_prices` | `warranty_claims` | `187` | `approved_amount` | positive amount made negative |
| 496 | `negative_costs_or_prices` | `complaints` | `1762` | `resolution_cost` | positive amount made negative |
| 497 | `negative_costs_or_prices` | `complaints` | `860` | `resolution_cost` | positive amount made negative |
| 498 | `negative_costs_or_prices` | `complaints` | `1581` | `resolution_cost` | positive amount made negative |
| 499 | `negative_costs_or_prices` | `complaints` | `590` | `resolution_cost` | positive amount made negative |
| 500 | `negative_costs_or_prices` | `complaints` | `697` | `resolution_cost` | positive amount made negative |
| 501 | `negative_costs_or_prices` | `complaints` | `1496` | `resolution_cost` | positive amount made negative |
| 502 | `negative_costs_or_prices` | `complaints` | `423` | `resolution_cost` | positive amount made negative |
| 503 | `negative_costs_or_prices` | `complaints` | `900` | `resolution_cost` | positive amount made negative |
| 504 | `negative_costs_or_prices` | `complaints` | `776` | `resolution_cost` | positive amount made negative |
| 505 | `negative_costs_or_prices` | `complaints` | `1542` | `resolution_cost` | positive amount made negative |
| 506 | `orphan_foreign_keys` | `salespeople` | `208` | `branch_id` | set to nonexistent key 9001 |
| 507 | `orphan_foreign_keys` | `salespeople` | `105` | `branch_id` | set to nonexistent key 9001 |
| 508 | `orphan_foreign_keys` | `salespeople` | `190` | `branch_id` | set to nonexistent key 9001 |
| 509 | `orphan_foreign_keys` | `salespeople` | `194` | `branch_id` | set to nonexistent key 9001 |
| 510 | `orphan_foreign_keys` | `salespeople` | `7` | `branch_id` | set to nonexistent key 9001 |
| 511 | `orphan_foreign_keys` | `salespeople` | `179` | `branch_id` | set to nonexistent key 9001 |
| 512 | `orphan_foreign_keys` | `salespeople` | `142` | `branch_id` | set to nonexistent key 9001 |
| 513 | `orphan_foreign_keys` | `salespeople` | `167` | `branch_id` | set to nonexistent key 9001 |
| 514 | `orphan_foreign_keys` | `inventory` | `24619` | `model_id` | set to nonexistent key 9002 |
| 515 | `orphan_foreign_keys` | `inventory` | `13646` | `model_id` | set to nonexistent key 9002 |
| 516 | `orphan_foreign_keys` | `inventory` | `24933` | `model_id` | set to nonexistent key 9002 |
| 517 | `orphan_foreign_keys` | `inventory` | `19474` | `model_id` | set to nonexistent key 9002 |
| 518 | `orphan_foreign_keys` | `inventory` | `20217` | `model_id` | set to nonexistent key 9002 |
| 519 | `orphan_foreign_keys` | `inventory` | `14656` | `model_id` | set to nonexistent key 9002 |
| 520 | `orphan_foreign_keys` | `inventory` | `621` | `model_id` | set to nonexistent key 9002 |
| 521 | `orphan_foreign_keys` | `inventory` | `3577` | `model_id` | set to nonexistent key 9002 |
| 522 | `orphan_foreign_keys` | `inventory` | `3885` | `model_id` | set to nonexistent key 9002 |
| 523 | `orphan_foreign_keys` | `inventory` | `19698` | `model_id` | set to nonexistent key 9002 |
| 524 | `orphan_foreign_keys` | `inventory` | `24234` | `model_id` | set to nonexistent key 9002 |
| 525 | `orphan_foreign_keys` | `inventory` | `6801` | `model_id` | set to nonexistent key 9002 |
| 526 | `orphan_foreign_keys` | `inventory` | `5310` | `branch_id` | set to nonexistent key 9003 |
| 527 | `orphan_foreign_keys` | `inventory` | `22217` | `branch_id` | set to nonexistent key 9003 |
| 528 | `orphan_foreign_keys` | `inventory` | `23995` | `branch_id` | set to nonexistent key 9003 |
| 529 | `orphan_foreign_keys` | `inventory` | `1406` | `branch_id` | set to nonexistent key 9003 |
| 530 | `orphan_foreign_keys` | `inventory` | `22810` | `branch_id` | set to nonexistent key 9003 |
| 531 | `orphan_foreign_keys` | `inventory` | `24280` | `branch_id` | set to nonexistent key 9003 |
| 532 | `orphan_foreign_keys` | `inventory` | `17435` | `branch_id` | set to nonexistent key 9003 |
| 533 | `orphan_foreign_keys` | `inventory` | `23005` | `branch_id` | set to nonexistent key 9003 |
| 534 | `orphan_foreign_keys` | `inventory` | `5509` | `branch_id` | set to nonexistent key 9003 |
| 535 | `orphan_foreign_keys` | `inventory` | `22874` | `branch_id` | set to nonexistent key 9003 |
| 536 | `orphan_foreign_keys` | `sales` | `9401` | `salesperson_id` | set to nonexistent key 9004 |
| 537 | `orphan_foreign_keys` | `sales` | `3883` | `salesperson_id` | set to nonexistent key 9004 |
| 538 | `orphan_foreign_keys` | `sales` | `16344` | `salesperson_id` | set to nonexistent key 9004 |
| 539 | `orphan_foreign_keys` | `sales` | `9418` | `salesperson_id` | set to nonexistent key 9004 |
| 540 | `orphan_foreign_keys` | `sales` | `13336` | `salesperson_id` | set to nonexistent key 9004 |
| 541 | `orphan_foreign_keys` | `sales` | `11663` | `salesperson_id` | set to nonexistent key 9004 |
| 542 | `orphan_foreign_keys` | `sales` | `3347` | `salesperson_id` | set to nonexistent key 9004 |
| 543 | `orphan_foreign_keys` | `sales` | `8056` | `salesperson_id` | set to nonexistent key 9004 |
| 544 | `orphan_foreign_keys` | `sales` | `390` | `salesperson_id` | set to nonexistent key 9004 |
| 545 | `orphan_foreign_keys` | `sales` | `4963` | `salesperson_id` | set to nonexistent key 9004 |
| 546 | `orphan_foreign_keys` | `sales` | `6023` | `salesperson_id` | set to nonexistent key 9004 |
| 547 | `orphan_foreign_keys` | `sales` | `2412` | `salesperson_id` | set to nonexistent key 9004 |
| 548 | `orphan_foreign_keys` | `sales` | `6437` | `salesperson_id` | set to nonexistent key 9004 |
| 549 | `orphan_foreign_keys` | `sales` | `12075` | `salesperson_id` | set to nonexistent key 9004 |
| 550 | `orphan_foreign_keys` | `sales` | `19368` | `salesperson_id` | set to nonexistent key 9004 |
| 551 | `orphan_foreign_keys` | `service_records` | `20609` | `inventory_id` | set to nonexistent key 9005 |
| 552 | `orphan_foreign_keys` | `service_records` | `86` | `inventory_id` | set to nonexistent key 9005 |
| 553 | `orphan_foreign_keys` | `service_records` | `36551` | `inventory_id` | set to nonexistent key 9005 |
| 554 | `orphan_foreign_keys` | `service_records` | `20753` | `inventory_id` | set to nonexistent key 9005 |
| 555 | `orphan_foreign_keys` | `service_records` | `29810` | `inventory_id` | set to nonexistent key 9005 |
| 556 | `orphan_foreign_keys` | `service_records` | `19173` | `inventory_id` | set to nonexistent key 9005 |
| 557 | `orphan_foreign_keys` | `service_records` | `5829` | `inventory_id` | set to nonexistent key 9005 |
| 558 | `orphan_foreign_keys` | `service_records` | `37041` | `inventory_id` | set to nonexistent key 9005 |
| 559 | `orphan_foreign_keys` | `service_records` | `47687` | `inventory_id` | set to nonexistent key 9005 |
| 560 | `orphan_foreign_keys` | `service_records` | `3267` | `inventory_id` | set to nonexistent key 9005 |
| 561 | `orphan_foreign_keys` | `service_records` | `1262` | `inventory_id` | set to nonexistent key 9005 |
| 562 | `orphan_foreign_keys` | `service_records` | `995` | `inventory_id` | set to nonexistent key 9005 |
| 563 | `orphan_foreign_keys` | `service_records` | `4658` | `inventory_id` | set to nonexistent key 9005 |
| 564 | `orphan_foreign_keys` | `service_records` | `21016` | `inventory_id` | set to nonexistent key 9005 |
| 565 | `orphan_foreign_keys` | `service_records` | `8708` | `inventory_id` | set to nonexistent key 9005 |
| 566 | `orphan_foreign_keys` | `warranty_claims` | `1495` | `service_id` | set to nonexistent key 9006 |
| 567 | `orphan_foreign_keys` | `warranty_claims` | `2776` | `service_id` | set to nonexistent key 9006 |
| 568 | `orphan_foreign_keys` | `warranty_claims` | `2810` | `service_id` | set to nonexistent key 9006 |
| 569 | `orphan_foreign_keys` | `warranty_claims` | `2098` | `service_id` | set to nonexistent key 9006 |
| 570 | `orphan_foreign_keys` | `warranty_claims` | `2841` | `service_id` | set to nonexistent key 9006 |
| 571 | `orphan_foreign_keys` | `warranty_claims` | `3050` | `service_id` | set to nonexistent key 9006 |
| 572 | `orphan_foreign_keys` | `warranty_claims` | `2206` | `service_id` | set to nonexistent key 9006 |
| 573 | `orphan_foreign_keys` | `warranty_claims` | `1471` | `service_id` | set to nonexistent key 9006 |
| 574 | `orphan_foreign_keys` | `warranty_claims` | `1752` | `service_id` | set to nonexistent key 9006 |
| 575 | `orphan_foreign_keys` | `warranty_claims` | `2530` | `service_id` | set to nonexistent key 9006 |
| 576 | `orphan_foreign_keys` | `complaints` | `1233` | `claim_id` | set to nonexistent key 9007 |
| 577 | `orphan_foreign_keys` | `complaints` | `119` | `claim_id` | set to nonexistent key 9007 |
| 578 | `orphan_foreign_keys` | `complaints` | `848` | `claim_id` | set to nonexistent key 9007 |
| 579 | `orphan_foreign_keys` | `complaints` | `470` | `claim_id` | set to nonexistent key 9007 |
| 580 | `orphan_foreign_keys` | `complaints` | `488` | `claim_id` | set to nonexistent key 9007 |
| 581 | `orphan_foreign_keys` | `complaints` | `1218` | `claim_id` | set to nonexistent key 9007 |
| 582 | `orphan_foreign_keys` | `complaints` | `84` | `claim_id` | set to nonexistent key 9007 |
| 583 | `orphan_foreign_keys` | `complaints` | `1436` | `claim_id` | set to nonexistent key 9007 |
| 584 | `orphan_foreign_keys` | `satisfaction` | `13190` | `complaint_id` | set to nonexistent key 9008 |
| 585 | `orphan_foreign_keys` | `satisfaction` | `11640` | `complaint_id` | set to nonexistent key 9008 |
| 586 | `orphan_foreign_keys` | `satisfaction` | `6323` | `complaint_id` | set to nonexistent key 9008 |
| 587 | `orphan_foreign_keys` | `satisfaction` | `4288` | `complaint_id` | set to nonexistent key 9008 |
| 588 | `orphan_foreign_keys` | `satisfaction` | `6816` | `complaint_id` | set to nonexistent key 9008 |
| 589 | `orphan_foreign_keys` | `satisfaction` | `12726` | `complaint_id` | set to nonexistent key 9008 |
| 590 | `orphan_foreign_keys` | `satisfaction` | `10909` | `complaint_id` | set to nonexistent key 9008 |
| 591 | `duplicate_vins` | `inventory` | `24320` | `vin` | duplicates inventory_id 24601 |
| 592 | `duplicate_vins` | `inventory` | `3729` | `vin` | duplicates inventory_id 14866 |
| 593 | `duplicate_vins` | `inventory` | `426` | `vin` | duplicates inventory_id 10847 |
| 594 | `duplicate_vins` | `inventory` | `4057` | `vin` | duplicates inventory_id 6134 |
| 595 | `duplicate_vins` | `inventory` | `2149` | `vin` | duplicates inventory_id 10437 |
| 596 | `duplicate_vins` | `inventory` | `11408` | `vin` | duplicates inventory_id 11295 |
| 597 | `duplicate_vins` | `inventory` | `18909` | `vin` | duplicates inventory_id 6670 |
| 598 | `duplicate_vins` | `inventory` | `16094` | `vin` | duplicates inventory_id 14543 |
| 599 | `duplicate_vins` | `inventory` | `23527` | `vin` | duplicates inventory_id 2320 |
| 600 | `duplicate_vins` | `inventory` | `23138` | `vin` | duplicates inventory_id 14405 |
| 601 | `duplicate_vins` | `inventory` | `4528` | `vin` | duplicates inventory_id 4368 |
| 602 | `duplicate_vins` | `inventory` | `15494` | `vin` | duplicates inventory_id 18134 |
| 603 | `duplicate_vins` | `inventory` | `2260` | `vin` | duplicates inventory_id 22088 |
| 604 | `duplicate_vins` | `inventory` | `23860` | `vin` | duplicates inventory_id 7623 |
| 605 | `duplicate_vins` | `inventory` | `11353` | `vin` | duplicates inventory_id 21442 |
| 606 | `duplicate_vins` | `inventory` | `22406` | `vin` | duplicates inventory_id 16251 |
| 607 | `duplicate_vins` | `inventory` | `13972` | `vin` | duplicates inventory_id 20314 |
| 608 | `duplicate_vins` | `inventory` | `22185` | `vin` | duplicates inventory_id 12797 |
| 609 | `duplicate_vins` | `inventory` | `22258` | `vin` | duplicates inventory_id 4048 |
| 610 | `duplicate_vins` | `inventory` | `14610` | `vin` | duplicates inventory_id 3424 |
| 611 | `duplicate_vins` | `inventory` | `8091` | `vin` | duplicates inventory_id 8497 |
| 612 | `duplicate_vins` | `inventory` | `24738` | `vin` | duplicates inventory_id 3908 |
| 613 | `duplicate_vins` | `inventory` | `23809` | `vin` | duplicates inventory_id 24803 |
| 614 | `duplicate_vins` | `inventory` | `18776` | `vin` | duplicates inventory_id 6051 |
| 615 | `duplicate_vins` | `inventory` | `10778` | `vin` | duplicates inventory_id 18985 |
| 616 | `duplicate_vins` | `inventory` | `8574` | `vin` | duplicates inventory_id 13644 |
| 617 | `duplicate_vins` | `inventory` | `6606` | `vin` | duplicates inventory_id 5141 |
| 618 | `duplicate_vins` | `inventory` | `3346` | `vin` | duplicates inventory_id 22286 |
| 619 | `malformed_vins` | `inventory` | `17583` | `vin` | invalid VIN length or characters |
| 620 | `malformed_vins` | `inventory` | `23661` | `vin` | invalid VIN length or characters |
| 621 | `malformed_vins` | `inventory` | `9356` | `vin` | invalid VIN length or characters |
| 622 | `malformed_vins` | `inventory` | `2118` | `vin` | invalid VIN length or characters |
| 623 | `malformed_vins` | `inventory` | `14930` | `vin` | invalid VIN length or characters |
| 624 | `malformed_vins` | `inventory` | `5186` | `vin` | invalid VIN length or characters |
| 625 | `malformed_vins` | `inventory` | `16676` | `vin` | invalid VIN length or characters |
| 626 | `malformed_vins` | `inventory` | `9801` | `vin` | invalid VIN length or characters |
| 627 | `malformed_vins` | `inventory` | `2702` | `vin` | invalid VIN length or characters |
| 628 | `malformed_vins` | `inventory` | `5682` | `vin` | invalid VIN length or characters |
| 629 | `malformed_vins` | `inventory` | `2693` | `vin` | invalid VIN length or characters |
| 630 | `malformed_vins` | `inventory` | `14235` | `vin` | invalid VIN length or characters |
| 631 | `malformed_vins` | `inventory` | `18903` | `vin` | invalid VIN length or characters |
| 632 | `malformed_vins` | `inventory` | `15734` | `vin` | invalid VIN length or characters |
| 633 | `malformed_vins` | `inventory` | `5909` | `vin` | invalid VIN length or characters |
| 634 | `malformed_vins` | `inventory` | `1570` | `vin` | invalid VIN length or characters |
| 635 | `malformed_vins` | `inventory` | `19287` | `vin` | invalid VIN length or characters |
| 636 | `malformed_vins` | `inventory` | `6528` | `vin` | invalid VIN length or characters |
| 637 | `malformed_vins` | `inventory` | `2708` | `vin` | invalid VIN length or characters |
| 638 | `malformed_vins` | `inventory` | `1529` | `vin` | invalid VIN length or characters |
| 639 | `malformed_vins` | `inventory` | `18876` | `vin` | invalid VIN length or characters |
| 640 | `malformed_vins` | `inventory` | `22615` | `vin` | invalid VIN length or characters |
| 641 | `malformed_vins` | `inventory` | `10782` | `vin` | invalid VIN length or characters |
| 642 | `malformed_vins` | `inventory` | `22547` | `vin` | invalid VIN length or characters |
| 643 | `malformed_vins` | `inventory` | `4654` | `vin` | invalid VIN length or characters |
| 644 | `malformed_vins` | `inventory` | `4960` | `vin` | invalid VIN length or characters |
| 645 | `malformed_vins` | `inventory` | `2947` | `vin` | invalid VIN length or characters |
| 646 | `malformed_vins` | `inventory` | `18421` | `vin` | invalid VIN length or characters |
| 647 | `malformed_vins` | `inventory` | `22060` | `vin` | invalid VIN length or characters |
| 648 | `malformed_vins` | `inventory` | `17439` | `vin` | invalid VIN length or characters |
| 649 | `malformed_vins` | `inventory` | `2465` | `vin` | invalid VIN length or characters |
| 650 | `malformed_vins` | `inventory` | `18265` | `vin` | invalid VIN length or characters |
| 651 | `malformed_vins` | `inventory` | `23232` | `vin` | invalid VIN length or characters |
| 652 | `malformed_vins` | `inventory` | `8826` | `vin` | invalid VIN length or characters |
| 653 | `malformed_vins` | `inventory` | `7354` | `vin` | invalid VIN length or characters |
| 654 | `inconsistent_category_labels` | `branches` | `9` | `branch_type` | variant of 'full_service' |
| 655 | `inconsistent_category_labels` | `branches` | `3` | `branch_type` | variant of 'full_service' |
| 656 | `inconsistent_category_labels` | `branches` | `10` | `branch_type` | variant of 'full_service' |
| 657 | `inconsistent_category_labels` | `branches` | `7` | `branch_type` | variant of 'full_service' |
| 658 | `inconsistent_category_labels` | `branches` | `5` | `branch_type` | variant of 'full_service' |
| 659 | `inconsistent_category_labels` | `branches` | `1` | `branch_type` | variant of 'full_service' |
| 660 | `inconsistent_category_labels` | `branches` | `12` | `branch_type` | variant of 'sales_only' |
| 661 | `inconsistent_category_labels` | `branches` | `6` | `branch_type` | variant of 'full_service' |
| 662 | `inconsistent_category_labels` | `inventory` | `15405` | `inventory_status` | variant of 'sold' |
| 663 | `inconsistent_category_labels` | `inventory` | `7715` | `inventory_status` | variant of 'sold' |
| 664 | `inconsistent_category_labels` | `inventory` | `17876` | `inventory_status` | variant of 'sold' |
| 665 | `inconsistent_category_labels` | `inventory` | `4411` | `inventory_status` | variant of 'sold' |
| 666 | `inconsistent_category_labels` | `inventory` | `11776` | `inventory_status` | variant of 'sold' |
| 667 | `inconsistent_category_labels` | `inventory` | `6441` | `inventory_status` | variant of 'sold' |
| 668 | `inconsistent_category_labels` | `inventory` | `19947` | `inventory_status` | variant of 'sold' |
| 669 | `inconsistent_category_labels` | `inventory` | `17118` | `inventory_status` | variant of 'sold' |
| 670 | `inconsistent_category_labels` | `inventory` | `2450` | `inventory_status` | variant of 'sold' |
| 671 | `inconsistent_category_labels` | `inventory` | `2492` | `inventory_status` | variant of 'sold' |
| 672 | `inconsistent_category_labels` | `inventory` | `23831` | `inventory_status` | variant of 'sold' |
| 673 | `inconsistent_category_labels` | `inventory` | `39` | `inventory_status` | variant of 'sold' |
| 674 | `inconsistent_category_labels` | `inventory` | `14370` | `inventory_status` | variant of 'sold' |
| 675 | `inconsistent_category_labels` | `inventory` | `15403` | `inventory_status` | variant of 'sold' |
| 676 | `inconsistent_category_labels` | `inventory` | `2170` | `inventory_status` | variant of 'sold' |
| 677 | `inconsistent_category_labels` | `inventory` | `14664` | `inventory_status` | variant of 'sold' |
| 678 | `inconsistent_category_labels` | `inventory` | `15896` | `inventory_status` | variant of 'sold' |
| 679 | `inconsistent_category_labels` | `inventory` | `19630` | `inventory_status` | variant of 'sold' |
| 680 | `inconsistent_category_labels` | `inventory` | `17598` | `inventory_status` | variant of 'sold' |
| 681 | `inconsistent_category_labels` | `inventory` | `8118` | `inventory_status` | variant of 'sold' |
| 682 | `inconsistent_category_labels` | `inventory` | `15440` | `inventory_status` | variant of 'sold' |
| 683 | `inconsistent_category_labels` | `inventory` | `171` | `inventory_status` | variant of 'sold' |
| 684 | `inconsistent_category_labels` | `inventory` | `11237` | `inventory_status` | variant of 'sold' |
| 685 | `inconsistent_category_labels` | `inventory` | `12305` | `inventory_status` | variant of 'sold' |
| 686 | `inconsistent_category_labels` | `inventory` | `14249` | `inventory_status` | variant of 'available' |
| 687 | `inconsistent_category_labels` | `sales` | `8526` | `sales_channel` | variant of 'website_lead' |
| 688 | `inconsistent_category_labels` | `sales` | `6762` | `sales_channel` | variant of 'website_lead' |
| 689 | `inconsistent_category_labels` | `sales` | `15146` | `sales_channel` | variant of 'showroom' |
| 690 | `inconsistent_category_labels` | `sales` | `5156` | `sales_channel` | variant of 'website_lead' |
| 691 | `inconsistent_category_labels` | `sales` | `11702` | `sales_channel` | variant of 'fleet' |
| 692 | `inconsistent_category_labels` | `sales` | `15661` | `sales_channel` | variant of 'website_lead' |
| 693 | `inconsistent_category_labels` | `sales` | `18837` | `sales_channel` | variant of 'telephone' |
| 694 | `inconsistent_category_labels` | `sales` | `19423` | `sales_channel` | variant of 'website_lead' |
| 695 | `inconsistent_category_labels` | `sales` | `18291` | `sales_channel` | variant of 'showroom' |
| 696 | `inconsistent_category_labels` | `sales` | `17055` | `sales_channel` | variant of 'showroom' |
| 697 | `inconsistent_category_labels` | `sales` | `2422` | `sales_channel` | variant of 'showroom' |
| 698 | `inconsistent_category_labels` | `sales` | `5543` | `sales_channel` | variant of 'website_lead' |
| 699 | `inconsistent_category_labels` | `sales` | `2746` | `sales_channel` | variant of 'website_lead' |
| 700 | `inconsistent_category_labels` | `sales` | `5413` | `sales_channel` | variant of 'showroom' |
| 701 | `inconsistent_category_labels` | `sales` | `15329` | `sales_channel` | variant of 'showroom' |
| 702 | `inconsistent_category_labels` | `sales` | `6538` | `sales_channel` | variant of 'showroom' |
| 703 | `inconsistent_category_labels` | `sales` | `5815` | `sales_channel` | variant of 'showroom' |
| 704 | `inconsistent_category_labels` | `sales` | `2413` | `sales_channel` | variant of 'website_lead' |
| 705 | `inconsistent_category_labels` | `sales` | `3976` | `sales_channel` | variant of 'telephone' |
| 706 | `inconsistent_category_labels` | `sales` | `19774` | `sales_channel` | variant of 'showroom' |
| 707 | `inconsistent_category_labels` | `sales` | `10702` | `sales_channel` | variant of 'showroom' |
| 708 | `inconsistent_category_labels` | `sales` | `299` | `sales_channel` | variant of 'showroom' |
| 709 | `inconsistent_category_labels` | `sales` | `5490` | `sales_channel` | variant of 'showroom' |
| 710 | `inconsistent_category_labels` | `sales` | `13350` | `sales_channel` | variant of 'telephone' |
| 711 | `inconsistent_category_labels` | `sales` | `10457` | `sales_channel` | variant of 'fleet' |
| 712 | `inconsistent_category_labels` | `sales` | `18494` | `sales_channel` | variant of 'website_lead' |
| 713 | `inconsistent_category_labels` | `sales` | `12007` | `sales_channel` | variant of 'fleet' |
| 714 | `inconsistent_category_labels` | `sales` | `7611` | `sales_channel` | variant of 'website_lead' |
| 715 | `inconsistent_category_labels` | `sales` | `7564` | `sales_channel` | variant of 'showroom' |
| 716 | `inconsistent_category_labels` | `sales` | `12825` | `sales_channel` | variant of 'fleet' |
| 717 | `inconsistent_category_labels` | `service_records` | `42025` | `service_type` | variant of 'scheduled' |
| 718 | `inconsistent_category_labels` | `service_records` | `1121` | `service_type` | variant of 'repair' |
| 719 | `inconsistent_category_labels` | `service_records` | `38294` | `service_type` | variant of 'repair' |
| 720 | `inconsistent_category_labels` | `service_records` | `6440` | `service_type` | variant of 'scheduled' |
| 721 | `inconsistent_category_labels` | `service_records` | `31918` | `service_type` | variant of 'recall' |
| 722 | `inconsistent_category_labels` | `service_records` | `43316` | `service_type` | variant of 'scheduled' |
| 723 | `inconsistent_category_labels` | `service_records` | `46843` | `service_type` | variant of 'scheduled' |
| 724 | `inconsistent_category_labels` | `service_records` | `30907` | `service_type` | variant of 'bodywork' |
| 725 | `inconsistent_category_labels` | `service_records` | `33151` | `service_type` | variant of 'scheduled' |
| 726 | `inconsistent_category_labels` | `service_records` | `24938` | `service_type` | variant of 'scheduled' |
| 727 | `inconsistent_category_labels` | `service_records` | `10825` | `service_type` | variant of 'scheduled' |
| 728 | `inconsistent_category_labels` | `service_records` | `9199` | `service_type` | variant of 'scheduled' |
| 729 | `inconsistent_category_labels` | `service_records` | `3469` | `service_type` | variant of 'scheduled' |
| 730 | `inconsistent_category_labels` | `service_records` | `6801` | `service_type` | variant of 'scheduled' |
| 731 | `inconsistent_category_labels` | `service_records` | `31052` | `service_type` | variant of 'repair' |
| 732 | `inconsistent_category_labels` | `service_records` | `8242` | `service_type` | variant of 'bodywork' |
| 733 | `inconsistent_category_labels` | `service_records` | `34993` | `service_type` | variant of 'inspection' |
| 734 | `inconsistent_category_labels` | `service_records` | `4109` | `service_type` | variant of 'scheduled' |
| 735 | `inconsistent_category_labels` | `service_records` | `8862` | `service_type` | variant of 'bodywork' |
| 736 | `inconsistent_category_labels` | `service_records` | `42280` | `service_type` | variant of 'scheduled' |
| 737 | `inconsistent_category_labels` | `service_records` | `33738` | `service_type` | variant of 'repair' |
| 738 | `inconsistent_category_labels` | `service_records` | `20038` | `service_type` | variant of 'repair' |
| 739 | `inconsistent_category_labels` | `service_records` | `35974` | `service_type` | variant of 'scheduled' |
| 740 | `inconsistent_category_labels` | `service_records` | `26829` | `service_type` | variant of 'scheduled' |
| 741 | `inconsistent_category_labels` | `service_records` | `28605` | `service_type` | variant of 'scheduled' |
| 742 | `inconsistent_category_labels` | `service_records` | `31446` | `service_type` | variant of 'repair' |
| 743 | `inconsistent_category_labels` | `service_records` | `21173` | `service_type` | variant of 'inspection' |
| 744 | `inconsistent_category_labels` | `service_records` | `38746` | `service_type` | variant of 'scheduled' |
| 745 | `inconsistent_category_labels` | `service_records` | `10806` | `service_type` | variant of 'repair' |
| 746 | `inconsistent_category_labels` | `service_records` | `28143` | `service_type` | variant of 'scheduled' |
| 747 | `inconsistent_category_labels` | `complaints` | `449` | `complaint_category` | variant of 'staff' |
| 748 | `inconsistent_category_labels` | `complaints` | `1495` | `complaint_category` | variant of 'billing' |
| 749 | `inconsistent_category_labels` | `complaints` | `1775` | `complaint_category` | variant of 'product' |
| 750 | `inconsistent_category_labels` | `complaints` | `734` | `complaint_category` | variant of 'warranty' |
| 751 | `inconsistent_category_labels` | `complaints` | `1438` | `complaint_category` | variant of 'warranty' |
| 752 | `inconsistent_category_labels` | `complaints` | `269` | `complaint_category` | variant of 'product' |
| 753 | `inconsistent_category_labels` | `complaints` | `320` | `complaint_category` | variant of 'warranty' |
| 754 | `inconsistent_category_labels` | `complaints` | `528` | `complaint_category` | variant of 'service_delay' |
| 755 | `inconsistent_category_labels` | `complaints` | `335` | `complaint_category` | variant of 'delivery' |
| 756 | `inconsistent_category_labels` | `complaints` | `516` | `complaint_category` | variant of 'staff' |
| 757 | `inconsistent_category_labels` | `complaints` | `1714` | `complaint_category` | variant of 'service_delay' |
| 758 | `inconsistent_category_labels` | `complaints` | `1111` | `complaint_category` | variant of 'product' |
| 759 | `inconsistent_category_labels` | `complaints` | `994` | `complaint_category` | variant of 'billing' |
| 760 | `inconsistent_category_labels` | `complaints` | `1637` | `complaint_category` | variant of 'product' |
| 761 | `inconsistent_category_labels` | `complaints` | `1182` | `complaint_category` | variant of 'service_delay' |
| 762 | `inconsistent_category_labels` | `complaints` | `26` | `complaint_category` | variant of 'staff' |
| 763 | `inconsistent_category_labels` | `complaints` | `1170` | `complaint_category` | variant of 'product' |
| 764 | `inconsistent_category_labels` | `complaints` | `1178` | `complaint_category` | variant of 'warranty' |
| 765 | `inconsistent_category_labels` | `complaints` | `750` | `complaint_category` | variant of 'product' |
| 766 | `inconsistent_category_labels` | `complaints` | `1212` | `complaint_category` | variant of 'product' |
| 767 | `inconsistent_category_labels` | `complaints` | `682` | `complaint_category` | variant of 'product' |
| 768 | `inconsistent_category_labels` | `complaints` | `903` | `complaint_category` | variant of 'service_delay' |
| 769 | `inconsistent_category_labels` | `satisfaction` | `6252` | `response_channel` | variant of 'email' |
| 770 | `inconsistent_category_labels` | `satisfaction` | `14555` | `response_channel` | variant of 'sms' |
| 771 | `inconsistent_category_labels` | `satisfaction` | `11837` | `response_channel` | variant of 'email' |
| 772 | `inconsistent_category_labels` | `satisfaction` | `7198` | `response_channel` | variant of 'sms' |
| 773 | `inconsistent_category_labels` | `satisfaction` | `11688` | `response_channel` | variant of 'sms' |
| 774 | `inconsistent_category_labels` | `satisfaction` | `893` | `response_channel` | variant of 'web' |
| 775 | `inconsistent_category_labels` | `satisfaction` | `13302` | `response_channel` | variant of 'web' |
| 776 | `inconsistent_category_labels` | `satisfaction` | `14544` | `response_channel` | variant of 'sms' |
| 777 | `inconsistent_category_labels` | `satisfaction` | `8150` | `response_channel` | variant of 'sms' |
| 778 | `inconsistent_category_labels` | `satisfaction` | `7053` | `response_channel` | variant of 'email' |
| 779 | `inconsistent_category_labels` | `satisfaction` | `14759` | `response_channel` | variant of 'email' |
| 780 | `inconsistent_category_labels` | `satisfaction` | `7559` | `response_channel` | variant of 'sms' |
| 781 | `inconsistent_category_labels` | `satisfaction` | `9108` | `response_channel` | variant of 'sms' |
| 782 | `inconsistent_category_labels` | `satisfaction` | `7165` | `response_channel` | variant of 'email' |
| 783 | `inconsistent_category_labels` | `satisfaction` | `10881` | `response_channel` | variant of 'email' |
| 784 | `inconsistent_category_labels` | `satisfaction` | `11887` | `response_channel` | variant of 'sms' |
| 785 | `inconsistent_category_labels` | `satisfaction` | `14982` | `response_channel` | variant of 'sms' |
| 786 | `inconsistent_category_labels` | `satisfaction` | `11433` | `response_channel` | variant of 'phone' |
| 787 | `inconsistent_category_labels` | `satisfaction` | `1033` | `response_channel` | variant of 'email' |
| 788 | `inconsistent_category_labels` | `satisfaction` | `1400` | `response_channel` | variant of 'web' |
| 789 | `missing_required_descriptive_values` | `branches` | `14` | `manager_name` | required descriptive value removed |
| 790 | `missing_required_descriptive_values` | `branches` | `11` | `manager_name` | required descriptive value removed |
| 791 | `missing_required_descriptive_values` | `branches` | `15` | `manager_name` | required descriptive value removed |
| 792 | `missing_required_descriptive_values` | `branches` | `8` | `manager_name` | required descriptive value removed |
| 793 | `missing_required_descriptive_values` | `branches` | `12` | `manager_name` | required descriptive value removed |
| 794 | `missing_required_descriptive_values` | `branches` | `6` | `manager_name` | required descriptive value removed |
| 795 | `missing_required_descriptive_values` | `branches` | `7` | `manager_name` | required descriptive value removed |
| 796 | `missing_required_descriptive_values` | `branches` | `5` | `manager_name` | required descriptive value removed |
| 797 | `missing_required_descriptive_values` | `models` | `39` | `manufacturer` | required descriptive value removed |
| 798 | `missing_required_descriptive_values` | `models` | `53` | `manufacturer` | required descriptive value removed |
| 799 | `missing_required_descriptive_values` | `models` | `49` | `manufacturer` | required descriptive value removed |
| 800 | `missing_required_descriptive_values` | `models` | `21` | `manufacturer` | required descriptive value removed |
| 801 | `missing_required_descriptive_values` | `models` | `38` | `manufacturer` | required descriptive value removed |
| 802 | `missing_required_descriptive_values` | `models` | `35` | `manufacturer` | required descriptive value removed |
| 803 | `missing_required_descriptive_values` | `models` | `6` | `manufacturer` | required descriptive value removed |
| 804 | `missing_required_descriptive_values` | `models` | `37` | `manufacturer` | required descriptive value removed |
| 805 | `missing_required_descriptive_values` | `models` | `12` | `manufacturer` | required descriptive value removed |
| 806 | `missing_required_descriptive_values` | `models` | `15` | `manufacturer` | required descriptive value removed |
| 807 | `missing_required_descriptive_values` | `models` | `54` | `manufacturer` | required descriptive value removed |
| 808 | `missing_required_descriptive_values` | `models` | `32` | `manufacturer` | required descriptive value removed |
| 809 | `missing_required_descriptive_values` | `salespeople` | `94` | `job_title` | required descriptive value removed |
| 810 | `missing_required_descriptive_values` | `salespeople` | `17` | `job_title` | required descriptive value removed |
| 811 | `missing_required_descriptive_values` | `salespeople` | `83` | `job_title` | required descriptive value removed |
| 812 | `missing_required_descriptive_values` | `salespeople` | `201` | `job_title` | required descriptive value removed |
| 813 | `missing_required_descriptive_values` | `salespeople` | `8` | `job_title` | required descriptive value removed |
| 814 | `missing_required_descriptive_values` | `salespeople` | `24` | `job_title` | required descriptive value removed |
| 815 | `missing_required_descriptive_values` | `salespeople` | `157` | `job_title` | required descriptive value removed |
| 816 | `missing_required_descriptive_values` | `salespeople` | `130` | `job_title` | required descriptive value removed |
| 817 | `missing_required_descriptive_values` | `salespeople` | `104` | `job_title` | required descriptive value removed |
| 818 | `missing_required_descriptive_values` | `salespeople` | `119` | `job_title` | required descriptive value removed |
| 819 | `missing_required_descriptive_values` | `salespeople` | `181` | `job_title` | required descriptive value removed |
| 820 | `missing_required_descriptive_values` | `salespeople` | `217` | `job_title` | required descriptive value removed |
| 821 | `missing_required_descriptive_values` | `salespeople` | `134` | `job_title` | required descriptive value removed |
| 822 | `missing_required_descriptive_values` | `salespeople` | `203` | `job_title` | required descriptive value removed |
| 823 | `missing_required_descriptive_values` | `salespeople` | `65` | `job_title` | required descriptive value removed |
| 824 | `missing_required_descriptive_values` | `salespeople` | `51` | `job_title` | required descriptive value removed |
| 825 | `missing_required_descriptive_values` | `salespeople` | `27` | `job_title` | required descriptive value removed |
| 826 | `missing_required_descriptive_values` | `salespeople` | `48` | `job_title` | required descriptive value removed |
| 827 | `missing_required_descriptive_values` | `salespeople` | `69` | `job_title` | required descriptive value removed |
| 828 | `missing_required_descriptive_values` | `salespeople` | `220` | `job_title` | required descriptive value removed |
| 829 | `missing_required_descriptive_values` | `inventory` | `19409` | `exterior_color` | required descriptive value removed |
| 830 | `missing_required_descriptive_values` | `inventory` | `366` | `exterior_color` | required descriptive value removed |
| 831 | `missing_required_descriptive_values` | `inventory` | `12887` | `exterior_color` | required descriptive value removed |
| 832 | `missing_required_descriptive_values` | `inventory` | `24559` | `exterior_color` | required descriptive value removed |
| 833 | `missing_required_descriptive_values` | `inventory` | `18870` | `exterior_color` | required descriptive value removed |
| 834 | `missing_required_descriptive_values` | `inventory` | `465` | `exterior_color` | required descriptive value removed |
| 835 | `missing_required_descriptive_values` | `inventory` | `19087` | `exterior_color` | required descriptive value removed |
| 836 | `missing_required_descriptive_values` | `inventory` | `10612` | `exterior_color` | required descriptive value removed |
| 837 | `missing_required_descriptive_values` | `inventory` | `21659` | `exterior_color` | required descriptive value removed |
| 838 | `missing_required_descriptive_values` | `inventory` | `15513` | `exterior_color` | required descriptive value removed |
| 839 | `missing_required_descriptive_values` | `inventory` | `15937` | `exterior_color` | required descriptive value removed |
| 840 | `missing_required_descriptive_values` | `inventory` | `11130` | `exterior_color` | required descriptive value removed |
| 841 | `missing_required_descriptive_values` | `inventory` | `3095` | `exterior_color` | required descriptive value removed |
| 842 | `missing_required_descriptive_values` | `inventory` | `11272` | `exterior_color` | required descriptive value removed |
| 843 | `missing_required_descriptive_values` | `inventory` | `5040` | `exterior_color` | required descriptive value removed |
| 844 | `missing_required_descriptive_values` | `sales` | `9798` | `customer_type` | required descriptive value removed |
| 845 | `missing_required_descriptive_values` | `sales` | `1383` | `customer_type` | required descriptive value removed |
| 846 | `missing_required_descriptive_values` | `sales` | `9278` | `customer_type` | required descriptive value removed |
| 847 | `missing_required_descriptive_values` | `sales` | `8115` | `customer_type` | required descriptive value removed |
| 848 | `missing_required_descriptive_values` | `sales` | `14613` | `customer_type` | required descriptive value removed |
| 849 | `missing_required_descriptive_values` | `sales` | `13403` | `customer_type` | required descriptive value removed |
| 850 | `missing_required_descriptive_values` | `sales` | `1497` | `customer_type` | required descriptive value removed |
| 851 | `missing_required_descriptive_values` | `sales` | `761` | `customer_type` | required descriptive value removed |
| 852 | `missing_required_descriptive_values` | `sales` | `3109` | `customer_type` | required descriptive value removed |
| 853 | `missing_required_descriptive_values` | `sales` | `9541` | `customer_type` | required descriptive value removed |
| 854 | `missing_required_descriptive_values` | `sales` | `4651` | `customer_type` | required descriptive value removed |
| 855 | `missing_required_descriptive_values` | `sales` | `4206` | `customer_type` | required descriptive value removed |
| 856 | `missing_required_descriptive_values` | `sales` | `17673` | `customer_type` | required descriptive value removed |
| 857 | `missing_required_descriptive_values` | `sales` | `8108` | `customer_type` | required descriptive value removed |
| 858 | `missing_required_descriptive_values` | `sales` | `1473` | `customer_type` | required descriptive value removed |
| 859 | `missing_required_descriptive_values` | `service_records` | `14522` | `technician_team` | required descriptive value removed |
| 860 | `missing_required_descriptive_values` | `service_records` | `23239` | `technician_team` | required descriptive value removed |
| 861 | `missing_required_descriptive_values` | `service_records` | `16332` | `technician_team` | required descriptive value removed |
| 862 | `missing_required_descriptive_values` | `service_records` | `29628` | `technician_team` | required descriptive value removed |
| 863 | `missing_required_descriptive_values` | `service_records` | `8231` | `technician_team` | required descriptive value removed |
| 864 | `missing_required_descriptive_values` | `service_records` | `19981` | `technician_team` | required descriptive value removed |
| 865 | `missing_required_descriptive_values` | `service_records` | `41465` | `technician_team` | required descriptive value removed |
| 866 | `missing_required_descriptive_values` | `service_records` | `10109` | `technician_team` | required descriptive value removed |
| 867 | `missing_required_descriptive_values` | `service_records` | `47847` | `technician_team` | required descriptive value removed |
| 868 | `missing_required_descriptive_values` | `service_records` | `41409` | `technician_team` | required descriptive value removed |
| 869 | `missing_required_descriptive_values` | `service_records` | `6920` | `technician_team` | required descriptive value removed |
| 870 | `missing_required_descriptive_values` | `service_records` | `9189` | `technician_team` | required descriptive value removed |
| 871 | `missing_required_descriptive_values` | `service_records` | `39367` | `technician_team` | required descriptive value removed |
| 872 | `missing_required_descriptive_values` | `service_records` | `18386` | `technician_team` | required descriptive value removed |
| 873 | `missing_required_descriptive_values` | `service_records` | `43128` | `technician_team` | required descriptive value removed |
| 874 | `missing_required_descriptive_values` | `warranty_claims` | `810` | `claim_description` | required descriptive value removed |
| 875 | `missing_required_descriptive_values` | `warranty_claims` | `1065` | `claim_description` | required descriptive value removed |
| 876 | `missing_required_descriptive_values` | `warranty_claims` | `2374` | `claim_description` | required descriptive value removed |
| 877 | `missing_required_descriptive_values` | `warranty_claims` | `2839` | `claim_description` | required descriptive value removed |
| 878 | `missing_required_descriptive_values` | `warranty_claims` | `656` | `claim_description` | required descriptive value removed |
| 879 | `missing_required_descriptive_values` | `warranty_claims` | `1836` | `claim_description` | required descriptive value removed |
| 880 | `missing_required_descriptive_values` | `warranty_claims` | `2273` | `claim_description` | required descriptive value removed |
| 881 | `missing_required_descriptive_values` | `warranty_claims` | `1378` | `claim_description` | required descriptive value removed |
| 882 | `missing_required_descriptive_values` | `complaints` | `995` | `complaint_category` | required descriptive value removed |
| 883 | `missing_required_descriptive_values` | `complaints` | `1367` | `complaint_category` | required descriptive value removed |
| 884 | `missing_required_descriptive_values` | `complaints` | `1716` | `complaint_category` | required descriptive value removed |
| 885 | `missing_required_descriptive_values` | `complaints` | `6` | `complaint_category` | required descriptive value removed |
| 886 | `missing_required_descriptive_values` | `complaints` | `1112` | `complaint_category` | required descriptive value removed |
| 887 | `missing_required_descriptive_values` | `complaints` | `836` | `complaint_category` | required descriptive value removed |
| 888 | `missing_required_descriptive_values` | `complaints` | `1657` | `complaint_category` | required descriptive value removed |
| 889 | `arithmetic_inconsistencies` | `sales` | `1837` | `net_sale_price` | component total offset by GHS 777.77 |
| 890 | `arithmetic_inconsistencies` | `sales` | `3325` | `net_sale_price` | component total offset by GHS 777.77 |
| 891 | `arithmetic_inconsistencies` | `sales` | `4933` | `net_sale_price` | component total offset by GHS 777.77 |
| 892 | `arithmetic_inconsistencies` | `sales` | `16335` | `net_sale_price` | component total offset by GHS 777.77 |
| 893 | `arithmetic_inconsistencies` | `sales` | `33` | `net_sale_price` | component total offset by GHS 777.77 |
| 894 | `arithmetic_inconsistencies` | `sales` | `18053` | `net_sale_price` | component total offset by GHS 777.77 |
| 895 | `arithmetic_inconsistencies` | `sales` | `12918` | `net_sale_price` | component total offset by GHS 777.77 |
| 896 | `arithmetic_inconsistencies` | `sales` | `18338` | `net_sale_price` | component total offset by GHS 777.77 |
| 897 | `arithmetic_inconsistencies` | `sales` | `4580` | `net_sale_price` | component total offset by GHS 777.77 |
| 898 | `arithmetic_inconsistencies` | `sales` | `11282` | `net_sale_price` | component total offset by GHS 777.77 |
| 899 | `arithmetic_inconsistencies` | `sales` | `14652` | `net_sale_price` | component total offset by GHS 777.77 |
| 900 | `arithmetic_inconsistencies` | `sales` | `10648` | `net_sale_price` | component total offset by GHS 777.77 |
| 901 | `arithmetic_inconsistencies` | `sales` | `13233` | `net_sale_price` | component total offset by GHS 777.77 |
| 902 | `arithmetic_inconsistencies` | `sales` | `17384` | `net_sale_price` | component total offset by GHS 777.77 |
| 903 | `arithmetic_inconsistencies` | `sales` | `321` | `net_sale_price` | component total offset by GHS 777.77 |
| 904 | `arithmetic_inconsistencies` | `sales` | `9332` | `net_sale_price` | component total offset by GHS 777.77 |
| 905 | `arithmetic_inconsistencies` | `sales` | `20126` | `net_sale_price` | component total offset by GHS 777.77 |
| 906 | `arithmetic_inconsistencies` | `sales` | `11617` | `net_sale_price` | component total offset by GHS 777.77 |
| 907 | `arithmetic_inconsistencies` | `sales` | `8380` | `net_sale_price` | component total offset by GHS 777.77 |
| 908 | `arithmetic_inconsistencies` | `sales` | `11814` | `net_sale_price` | component total offset by GHS 777.77 |
| 909 | `arithmetic_inconsistencies` | `sales` | `9028` | `net_sale_price` | component total offset by GHS 777.77 |
| 910 | `arithmetic_inconsistencies` | `sales` | `19361` | `net_sale_price` | component total offset by GHS 777.77 |
| 911 | `arithmetic_inconsistencies` | `sales` | `13285` | `net_sale_price` | component total offset by GHS 777.77 |
| 912 | `arithmetic_inconsistencies` | `sales` | `14134` | `net_sale_price` | component total offset by GHS 777.77 |
| 913 | `arithmetic_inconsistencies` | `sales` | `8368` | `net_sale_price` | component total offset by GHS 777.77 |
| 914 | `arithmetic_inconsistencies` | `sales` | `1065` | `net_sale_price` | component total offset by GHS 777.77 |
| 915 | `arithmetic_inconsistencies` | `sales` | `17052` | `net_sale_price` | component total offset by GHS 777.77 |
| 916 | `arithmetic_inconsistencies` | `sales` | `5697` | `net_sale_price` | component total offset by GHS 777.77 |
| 917 | `arithmetic_inconsistencies` | `sales` | `4135` | `net_sale_price` | component total offset by GHS 777.77 |
| 918 | `arithmetic_inconsistencies` | `sales` | `6494` | `net_sale_price` | component total offset by GHS 777.77 |
| 919 | `arithmetic_inconsistencies` | `sales` | `332` | `net_sale_price` | component total offset by GHS 777.77 |
| 920 | `arithmetic_inconsistencies` | `sales` | `12669` | `net_sale_price` | component total offset by GHS 777.77 |
| 921 | `arithmetic_inconsistencies` | `sales` | `14295` | `net_sale_price` | component total offset by GHS 777.77 |
| 922 | `arithmetic_inconsistencies` | `sales` | `1402` | `net_sale_price` | component total offset by GHS 777.77 |
| 923 | `arithmetic_inconsistencies` | `sales` | `18739` | `net_sale_price` | component total offset by GHS 777.77 |
| 924 | `arithmetic_inconsistencies` | `sales` | `10324` | `net_sale_price` | component total offset by GHS 777.77 |
| 925 | `arithmetic_inconsistencies` | `sales` | `1856` | `net_sale_price` | component total offset by GHS 777.77 |
| 926 | `arithmetic_inconsistencies` | `sales` | `7060` | `net_sale_price` | component total offset by GHS 777.77 |
| 927 | `arithmetic_inconsistencies` | `sales` | `9715` | `net_sale_price` | component total offset by GHS 777.77 |
| 928 | `arithmetic_inconsistencies` | `sales` | `15141` | `net_sale_price` | component total offset by GHS 777.77 |
| 929 | `arithmetic_inconsistencies` | `sales` | `6372` | `net_sale_price` | component total offset by GHS 777.77 |
| 930 | `arithmetic_inconsistencies` | `sales` | `8082` | `net_sale_price` | component total offset by GHS 777.77 |
| 931 | `arithmetic_inconsistencies` | `sales` | `5652` | `net_sale_price` | component total offset by GHS 777.77 |
| 932 | `arithmetic_inconsistencies` | `sales` | `4210` | `net_sale_price` | component total offset by GHS 777.77 |
| 933 | `arithmetic_inconsistencies` | `sales` | `10674` | `net_sale_price` | component total offset by GHS 777.77 |
| 934 | `arithmetic_inconsistencies` | `sales` | `15734` | `net_sale_price` | component total offset by GHS 777.77 |
| 935 | `arithmetic_inconsistencies` | `sales` | `3581` | `net_sale_price` | component total offset by GHS 777.77 |
| 936 | `arithmetic_inconsistencies` | `sales` | `11488` | `net_sale_price` | component total offset by GHS 777.77 |
| 937 | `arithmetic_inconsistencies` | `sales` | `17337` | `net_sale_price` | component total offset by GHS 777.77 |
| 938 | `arithmetic_inconsistencies` | `sales` | `3335` | `net_sale_price` | component total offset by GHS 777.77 |
| 939 | `arithmetic_inconsistencies` | `service_records` | `26413` | `total_service_cost` | component total offset by GHS 777.77 |
| 940 | `arithmetic_inconsistencies` | `service_records` | `17537` | `total_service_cost` | component total offset by GHS 777.77 |
| 941 | `arithmetic_inconsistencies` | `service_records` | `7063` | `total_service_cost` | component total offset by GHS 777.77 |
| 942 | `arithmetic_inconsistencies` | `service_records` | `36973` | `total_service_cost` | component total offset by GHS 777.77 |
| 943 | `arithmetic_inconsistencies` | `service_records` | `7298` | `total_service_cost` | component total offset by GHS 777.77 |
| 944 | `arithmetic_inconsistencies` | `service_records` | `28170` | `total_service_cost` | component total offset by GHS 777.77 |
| 945 | `arithmetic_inconsistencies` | `service_records` | `33004` | `total_service_cost` | component total offset by GHS 777.77 |
| 946 | `arithmetic_inconsistencies` | `service_records` | `8431` | `total_service_cost` | component total offset by GHS 777.77 |
| 947 | `arithmetic_inconsistencies` | `service_records` | `36499` | `total_service_cost` | component total offset by GHS 777.77 |
| 948 | `arithmetic_inconsistencies` | `service_records` | `10634` | `total_service_cost` | component total offset by GHS 777.77 |
| 949 | `arithmetic_inconsistencies` | `service_records` | `27204` | `total_service_cost` | component total offset by GHS 777.77 |
| 950 | `arithmetic_inconsistencies` | `service_records` | `47552` | `total_service_cost` | component total offset by GHS 777.77 |
| 951 | `arithmetic_inconsistencies` | `service_records` | `38156` | `total_service_cost` | component total offset by GHS 777.77 |
| 952 | `arithmetic_inconsistencies` | `service_records` | `29084` | `total_service_cost` | component total offset by GHS 777.77 |
| 953 | `arithmetic_inconsistencies` | `service_records` | `9079` | `total_service_cost` | component total offset by GHS 777.77 |
| 954 | `arithmetic_inconsistencies` | `service_records` | `31508` | `total_service_cost` | component total offset by GHS 777.77 |
| 955 | `arithmetic_inconsistencies` | `service_records` | `22523` | `total_service_cost` | component total offset by GHS 777.77 |
| 956 | `arithmetic_inconsistencies` | `service_records` | `24921` | `total_service_cost` | component total offset by GHS 777.77 |
| 957 | `arithmetic_inconsistencies` | `service_records` | `40722` | `total_service_cost` | component total offset by GHS 777.77 |
| 958 | `arithmetic_inconsistencies` | `service_records` | `41510` | `total_service_cost` | component total offset by GHS 777.77 |
| 959 | `arithmetic_inconsistencies` | `service_records` | `43130` | `total_service_cost` | component total offset by GHS 777.77 |
| 960 | `arithmetic_inconsistencies` | `service_records` | `16943` | `total_service_cost` | component total offset by GHS 777.77 |
| 961 | `arithmetic_inconsistencies` | `service_records` | `45076` | `total_service_cost` | component total offset by GHS 777.77 |
| 962 | `arithmetic_inconsistencies` | `service_records` | `41513` | `total_service_cost` | component total offset by GHS 777.77 |
| 963 | `arithmetic_inconsistencies` | `service_records` | `27523` | `total_service_cost` | component total offset by GHS 777.77 |
| 964 | `arithmetic_inconsistencies` | `service_records` | `12872` | `total_service_cost` | component total offset by GHS 777.77 |
| 965 | `arithmetic_inconsistencies` | `service_records` | `43434` | `total_service_cost` | component total offset by GHS 777.77 |
| 966 | `arithmetic_inconsistencies` | `service_records` | `13330` | `total_service_cost` | component total offset by GHS 777.77 |
| 967 | `arithmetic_inconsistencies` | `service_records` | `40134` | `total_service_cost` | component total offset by GHS 777.77 |
| 968 | `arithmetic_inconsistencies` | `service_records` | `47471` | `total_service_cost` | component total offset by GHS 777.77 |
| 969 | `arithmetic_inconsistencies` | `warranty_claims` | `1798` | `approved_amount` | component total offset by GHS 777.77 |
| 970 | `arithmetic_inconsistencies` | `warranty_claims` | `1184` | `approved_amount` | component total offset by GHS 777.77 |
| 971 | `arithmetic_inconsistencies` | `warranty_claims` | `1444` | `approved_amount` | component total offset by GHS 777.77 |
| 972 | `arithmetic_inconsistencies` | `warranty_claims` | `1995` | `approved_amount` | component total offset by GHS 777.77 |
| 973 | `arithmetic_inconsistencies` | `warranty_claims` | `2688` | `approved_amount` | component total offset by GHS 777.77 |
| 974 | `arithmetic_inconsistencies` | `warranty_claims` | `1440` | `approved_amount` | component total offset by GHS 777.77 |
| 975 | `arithmetic_inconsistencies` | `warranty_claims` | `30` | `approved_amount` | component total offset by GHS 777.77 |
| 976 | `arithmetic_inconsistencies` | `warranty_claims` | `541` | `approved_amount` | component total offset by GHS 777.77 |
| 977 | `arithmetic_inconsistencies` | `warranty_claims` | `566` | `approved_amount` | component total offset by GHS 777.77 |
| 978 | `arithmetic_inconsistencies` | `warranty_claims` | `2787` | `approved_amount` | component total offset by GHS 777.77 |
| 979 | `arithmetic_inconsistencies` | `warranty_claims` | `1647` | `approved_amount` | component total offset by GHS 777.77 |
| 980 | `arithmetic_inconsistencies` | `warranty_claims` | `58` | `approved_amount` | component total offset by GHS 777.77 |
| 981 | `arithmetic_inconsistencies` | `warranty_claims` | `2734` | `approved_amount` | component total offset by GHS 777.77 |
| 982 | `arithmetic_inconsistencies` | `warranty_claims` | `2595` | `approved_amount` | component total offset by GHS 777.77 |
| 983 | `arithmetic_inconsistencies` | `warranty_claims` | `678` | `approved_amount` | component total offset by GHS 777.77 |
| 984 | `invalid_satisfaction_scores` | `satisfaction` | `5311` | `overall_score` | outside field's permitted range |
| 985 | `invalid_satisfaction_scores` | `satisfaction` | `14841` | `nps_score` | outside field's permitted range |
| 986 | `invalid_satisfaction_scores` | `satisfaction` | `2166` | `overall_score` | outside field's permitted range |
| 987 | `invalid_satisfaction_scores` | `satisfaction` | `1837` | `staff_score` | outside field's permitted range |
| 988 | `invalid_satisfaction_scores` | `satisfaction` | `2634` | `timeliness_score` | outside field's permitted range |
| 989 | `invalid_satisfaction_scores` | `satisfaction` | `10919` | `value_score` | outside field's permitted range |
| 990 | `invalid_satisfaction_scores` | `satisfaction` | `8956` | `overall_score` | outside field's permitted range |
| 991 | `invalid_satisfaction_scores` | `satisfaction` | `10795` | `nps_score` | outside field's permitted range |
| 992 | `invalid_satisfaction_scores` | `satisfaction` | `499` | `product_score` | outside field's permitted range |
| 993 | `invalid_satisfaction_scores` | `satisfaction` | `12042` | `staff_score` | outside field's permitted range |
| 994 | `invalid_satisfaction_scores` | `satisfaction` | `1967` | `timeliness_score` | outside field's permitted range |
| 995 | `invalid_satisfaction_scores` | `satisfaction` | `4517` | `value_score` | outside field's permitted range |
| 996 | `invalid_satisfaction_scores` | `satisfaction` | `14138` | `overall_score` | outside field's permitted range |
| 997 | `invalid_satisfaction_scores` | `satisfaction` | `14064` | `nps_score` | outside field's permitted range |
| 998 | `invalid_satisfaction_scores` | `satisfaction` | `867` | `product_score` | outside field's permitted range |
| 999 | `invalid_satisfaction_scores` | `satisfaction` | `7437` | `staff_score` | outside field's permitted range |
| 1000 | `invalid_satisfaction_scores` | `satisfaction` | `6708` | `timeliness_score` | outside field's permitted range |
| 1001 | `invalid_satisfaction_scores` | `satisfaction` | `3837` | `value_score` | outside field's permitted range |
| 1002 | `invalid_satisfaction_scores` | `satisfaction` | `13874` | `overall_score` | outside field's permitted range |
| 1003 | `invalid_satisfaction_scores` | `satisfaction` | `14930` | `nps_score` | outside field's permitted range |
| 1004 | `invalid_satisfaction_scores` | `satisfaction` | `14365` | `overall_score` | outside field's permitted range |
| 1005 | `invalid_satisfaction_scores` | `satisfaction` | `13984` | `staff_score` | outside field's permitted range |
| 1006 | `invalid_satisfaction_scores` | `satisfaction` | `11632` | `timeliness_score` | outside field's permitted range |
| 1007 | `invalid_satisfaction_scores` | `satisfaction` | `9809` | `value_score` | outside field's permitted range |
| 1008 | `invalid_satisfaction_scores` | `satisfaction` | `9757` | `overall_score` | outside field's permitted range |
| 1009 | `invalid_satisfaction_scores` | `satisfaction` | `13768` | `nps_score` | outside field's permitted range |
| 1010 | `invalid_satisfaction_scores` | `satisfaction` | `3999` | `product_score` | outside field's permitted range |
| 1011 | `invalid_satisfaction_scores` | `satisfaction` | `13970` | `staff_score` | outside field's permitted range |
| 1012 | `invalid_satisfaction_scores` | `satisfaction` | `8442` | `timeliness_score` | outside field's permitted range |
| 1013 | `invalid_satisfaction_scores` | `satisfaction` | `3459` | `value_score` | outside field's permitted range |
| 1014 | `invalid_satisfaction_scores` | `satisfaction` | `991` | `overall_score` | outside field's permitted range |
| 1015 | `invalid_satisfaction_scores` | `satisfaction` | `11340` | `nps_score` | outside field's permitted range |
| 1016 | `invalid_satisfaction_scores` | `satisfaction` | `8678` | `overall_score` | outside field's permitted range |
| 1017 | `invalid_satisfaction_scores` | `satisfaction` | `8393` | `staff_score` | outside field's permitted range |
| 1018 | `invalid_satisfaction_scores` | `satisfaction` | `4441` | `timeliness_score` | outside field's permitted range |
| 1019 | `invalid_satisfaction_scores` | `satisfaction` | `3794` | `value_score` | outside field's permitted range |
| 1020 | `invalid_satisfaction_scores` | `satisfaction` | `10531` | `overall_score` | outside field's permitted range |
| 1021 | `invalid_satisfaction_scores` | `satisfaction` | `11250` | `nps_score` | outside field's permitted range |
| 1022 | `invalid_satisfaction_scores` | `satisfaction` | `9226` | `product_score` | outside field's permitted range |
| 1023 | `invalid_satisfaction_scores` | `satisfaction` | `8274` | `staff_score` | outside field's permitted range |
| 1024 | `invalid_satisfaction_scores` | `satisfaction` | `10916` | `timeliness_score` | outside field's permitted range |
| 1025 | `invalid_satisfaction_scores` | `satisfaction` | `5391` | `value_score` | outside field's permitted range |
| 1026 | `invalid_satisfaction_scores` | `satisfaction` | `4064` | `overall_score` | outside field's permitted range |
| 1027 | `invalid_satisfaction_scores` | `satisfaction` | `3367` | `nps_score` | outside field's permitted range |
| 1028 | `invalid_satisfaction_scores` | `satisfaction` | `2649` | `overall_score` | outside field's permitted range |
| 1029 | `status_date_contradictions` | `inventory` | `5110` | `inventory_status` | available despite sold_date |
| 1030 | `status_date_contradictions` | `inventory` | `20788` | `inventory_status` | available despite sold_date |
| 1031 | `status_date_contradictions` | `inventory` | `24178` | `inventory_status` | available despite sold_date |
| 1032 | `status_date_contradictions` | `inventory` | `18122` | `inventory_status` | available despite sold_date |
| 1033 | `status_date_contradictions` | `inventory` | `11579` | `inventory_status` | available despite sold_date |
| 1034 | `status_date_contradictions` | `inventory` | `11953` | `inventory_status` | available despite sold_date |
| 1035 | `status_date_contradictions` | `inventory` | `15856` | `inventory_status` | available despite sold_date |
| 1036 | `status_date_contradictions` | `inventory` | `12247` | `inventory_status` | available despite sold_date |
| 1037 | `status_date_contradictions` | `inventory` | `23627` | `inventory_status` | available despite sold_date |
| 1038 | `status_date_contradictions` | `inventory` | `17168` | `inventory_status` | available despite sold_date |
| 1039 | `status_date_contradictions` | `inventory` | `15270` | `inventory_status` | available despite sold_date |
| 1040 | `status_date_contradictions` | `inventory` | `10230` | `inventory_status` | available despite sold_date |
| 1041 | `status_date_contradictions` | `inventory` | `496` | `inventory_status` | available despite sold_date |
| 1042 | `status_date_contradictions` | `inventory` | `9783` | `inventory_status` | available despite sold_date |
| 1043 | `status_date_contradictions` | `inventory` | `15533` | `inventory_status` | available despite sold_date |
| 1044 | `status_date_contradictions` | `inventory` | `19700` | `inventory_status` | available despite sold_date |
| 1045 | `status_date_contradictions` | `inventory` | `21919` | `inventory_status` | available despite sold_date |
| 1046 | `status_date_contradictions` | `inventory` | `19479` | `inventory_status` | available despite sold_date |
| 1047 | `status_date_contradictions` | `inventory` | `11659` | `inventory_status` | available despite sold_date |
| 1048 | `status_date_contradictions` | `inventory` | `5128` | `inventory_status` | available despite sold_date |
| 1049 | `status_date_contradictions` | `complaints` | `1689` | `resolution_date` | resolved without resolution date |
| 1050 | `status_date_contradictions` | `complaints` | `278` | `resolution_date` | resolved without resolution date |
| 1051 | `status_date_contradictions` | `complaints` | `1501` | `resolution_date` | resolved without resolution date |
| 1052 | `status_date_contradictions` | `complaints` | `896` | `resolution_date` | resolved without resolution date |
| 1053 | `status_date_contradictions` | `complaints` | `1385` | `resolution_date` | resolved without resolution date |
| 1054 | `status_date_contradictions` | `complaints` | `25` | `resolution_date` | resolved without resolution date |
| 1055 | `status_date_contradictions` | `complaints` | `1682` | `resolution_date` | resolved without resolution date |
| 1056 | `status_date_contradictions` | `complaints` | `841` | `resolution_date` | resolved without resolution date |
| 1057 | `status_date_contradictions` | `complaints` | `1485` | `resolution_date` | resolved without resolution date |
| 1058 | `status_date_contradictions` | `complaints` | `1022` | `resolution_date` | resolved without resolution date |
| 1059 | `status_date_contradictions` | `complaints` | `1771` | `resolution_date` | resolved without resolution date |
| 1060 | `status_date_contradictions` | `complaints` | `434` | `resolution_date` | resolved without resolution date |
| 1061 | `status_date_contradictions` | `complaints` | `1276` | `resolution_date` | resolved without resolution date |
| 1062 | `status_date_contradictions` | `complaints` | `1084` | `resolution_date` | resolved without resolution date |
| 1063 | `status_date_contradictions` | `complaints` | `257` | `resolution_date` | resolved without resolution date |
| 1064 | `status_date_contradictions` | `complaints` | `1475` | `resolution_date` | resolved without resolution date |
| 1065 | `status_date_contradictions` | `complaints` | `34` | `resolution_date` | resolved without resolution date |
| 1066 | `status_date_contradictions` | `complaints` | `1402` | `resolution_date` | resolved without resolution date |
| 1067 | `status_date_contradictions` | `complaints` | `662` | `resolution_date` | resolved without resolution date |
| 1068 | `status_date_contradictions` | `complaints` | `422` | `resolution_date` | resolved without resolution date |
| 1069 | `status_date_contradictions` | `warranty_claims` | `259` | `decision_date` | approved without decision date |
| 1070 | `status_date_contradictions` | `warranty_claims` | `3031` | `decision_date` | approved without decision date |
| 1071 | `status_date_contradictions` | `warranty_claims` | `767` | `decision_date` | approved without decision date |
| 1072 | `status_date_contradictions` | `warranty_claims` | `628` | `decision_date` | approved without decision date |
| 1073 | `status_date_contradictions` | `warranty_claims` | `687` | `decision_date` | approved without decision date |
| 1074 | `status_date_contradictions` | `warranty_claims` | `456` | `decision_date` | approved without decision date |
| 1075 | `status_date_contradictions` | `warranty_claims` | `405` | `decision_date` | approved without decision date |
| 1076 | `status_date_contradictions` | `warranty_claims` | `2294` | `decision_date` | approved without decision date |
| 1077 | `status_date_contradictions` | `warranty_claims` | `1705` | `decision_date` | approved without decision date |
| 1078 | `status_date_contradictions` | `warranty_claims` | `2041` | `decision_date` | approved without decision date |
| 1079 | `status_date_contradictions` | `warranty_claims` | `704` | `decision_date` | approved without decision date |
| 1080 | `status_date_contradictions` | `warranty_claims` | `2872` | `decision_date` | approved without decision date |
| 1081 | `status_date_contradictions` | `warranty_claims` | `1929` | `decision_date` | approved without decision date |
| 1082 | `status_date_contradictions` | `warranty_claims` | `2897` | `decision_date` | approved without decision date |
| 1083 | `status_date_contradictions` | `warranty_claims` | `1097` | `decision_date` | approved without decision date |
| 1084 | `status_date_contradictions` | `warranty_claims` | `1458` | `decision_date` | approved without decision date |
| 1085 | `status_date_contradictions` | `warranty_claims` | `2034` | `decision_date` | approved without decision date |
| 1086 | `status_date_contradictions` | `warranty_claims` | `496` | `decision_date` | approved without decision date |
| 1087 | `status_date_contradictions` | `warranty_claims` | `1859` | `decision_date` | approved without decision date |
| 1088 | `status_date_contradictions` | `warranty_claims` | `44` | `decision_date` | approved without decision date |
| 1089 | `implausible_mileage_or_labor_hours` | `service_records` | `27761` | `odometer_km` | negative odometer |
| 1090 | `implausible_mileage_or_labor_hours` | `service_records` | `26248` | `odometer_km` | negative odometer |
| 1091 | `implausible_mileage_or_labor_hours` | `service_records` | `6075` | `odometer_km` | negative odometer |
| 1092 | `implausible_mileage_or_labor_hours` | `service_records` | `387` | `odometer_km` | negative odometer |
| 1093 | `implausible_mileage_or_labor_hours` | `service_records` | `20256` | `odometer_km` | negative odometer |
| 1094 | `implausible_mileage_or_labor_hours` | `service_records` | `2650` | `odometer_km` | negative odometer |
| 1095 | `implausible_mileage_or_labor_hours` | `service_records` | `2699` | `odometer_km` | negative odometer |
| 1096 | `implausible_mileage_or_labor_hours` | `service_records` | `45990` | `odometer_km` | negative odometer |
| 1097 | `implausible_mileage_or_labor_hours` | `service_records` | `15428` | `odometer_km` | negative odometer |
| 1098 | `implausible_mileage_or_labor_hours` | `service_records` | `10218` | `odometer_km` | negative odometer |
| 1099 | `implausible_mileage_or_labor_hours` | `service_records` | `21463` | `odometer_km` | negative odometer |
| 1100 | `implausible_mileage_or_labor_hours` | `service_records` | `24216` | `odometer_km` | negative odometer |
| 1101 | `implausible_mileage_or_labor_hours` | `service_records` | `41423` | `odometer_km` | negative odometer |
| 1102 | `implausible_mileage_or_labor_hours` | `service_records` | `42940` | `odometer_km` | negative odometer |
| 1103 | `implausible_mileage_or_labor_hours` | `service_records` | `12814` | `odometer_km` | negative odometer |
| 1104 | `implausible_mileage_or_labor_hours` | `service_records` | `32700` | `odometer_km` | negative odometer |
| 1105 | `implausible_mileage_or_labor_hours` | `service_records` | `14935` | `odometer_km` | negative odometer |
| 1106 | `implausible_mileage_or_labor_hours` | `service_records` | `7647` | `odometer_km` | negative odometer |
| 1107 | `implausible_mileage_or_labor_hours` | `service_records` | `14604` | `odometer_km` | negative odometer |
| 1108 | `implausible_mileage_or_labor_hours` | `service_records` | `25146` | `odometer_km` | negative odometer |
| 1109 | `implausible_mileage_or_labor_hours` | `service_records` | `6818` | `odometer_km` | negative odometer |
| 1110 | `implausible_mileage_or_labor_hours` | `service_records` | `41016` | `odometer_km` | negative odometer |
| 1111 | `implausible_mileage_or_labor_hours` | `service_records` | `39963` | `odometer_km` | negative odometer |
| 1112 | `implausible_mileage_or_labor_hours` | `service_records` | `35926` | `odometer_km` | negative odometer |
| 1113 | `implausible_mileage_or_labor_hours` | `service_records` | `25864` | `labor_hours` | implausibly high labor hours |
| 1114 | `implausible_mileage_or_labor_hours` | `service_records` | `26312` | `labor_hours` | implausibly high labor hours |
| 1115 | `implausible_mileage_or_labor_hours` | `service_records` | `31115` | `labor_hours` | implausibly high labor hours |
| 1116 | `implausible_mileage_or_labor_hours` | `service_records` | `23870` | `labor_hours` | implausibly high labor hours |
| 1117 | `implausible_mileage_or_labor_hours` | `service_records` | `1143` | `labor_hours` | implausibly high labor hours |
| 1118 | `implausible_mileage_or_labor_hours` | `service_records` | `45659` | `labor_hours` | implausibly high labor hours |
| 1119 | `implausible_mileage_or_labor_hours` | `service_records` | `34635` | `labor_hours` | implausibly high labor hours |
| 1120 | `implausible_mileage_or_labor_hours` | `service_records` | `36881` | `labor_hours` | implausibly high labor hours |
| 1121 | `implausible_mileage_or_labor_hours` | `service_records` | `17302` | `labor_hours` | implausibly high labor hours |
| 1122 | `implausible_mileage_or_labor_hours` | `service_records` | `22039` | `labor_hours` | implausibly high labor hours |
| 1123 | `implausible_mileage_or_labor_hours` | `service_records` | `40138` | `labor_hours` | implausibly high labor hours |
| 1124 | `implausible_mileage_or_labor_hours` | `service_records` | `38963` | `labor_hours` | implausibly high labor hours |
| 1125 | `implausible_mileage_or_labor_hours` | `service_records` | `38885` | `labor_hours` | implausibly high labor hours |
| 1126 | `implausible_mileage_or_labor_hours` | `service_records` | `28145` | `labor_hours` | implausibly high labor hours |
| 1127 | `implausible_mileage_or_labor_hours` | `service_records` | `16791` | `labor_hours` | implausibly high labor hours |
| 1128 | `implausible_mileage_or_labor_hours` | `service_records` | `23634` | `labor_hours` | implausibly high labor hours |
| 1129 | `implausible_mileage_or_labor_hours` | `service_records` | `27806` | `labor_hours` | implausibly high labor hours |
| 1130 | `implausible_mileage_or_labor_hours` | `service_records` | `9566` | `labor_hours` | implausibly high labor hours |
| 1131 | `implausible_mileage_or_labor_hours` | `service_records` | `42380` | `labor_hours` | implausibly high labor hours |
| 1132 | `implausible_mileage_or_labor_hours` | `service_records` | `8300` | `labor_hours` | implausibly high labor hours |
| 1133 | `implausible_mileage_or_labor_hours` | `service_records` | `27538` | `labor_hours` | implausibly high labor hours |
| 1134 | `implausible_mileage_or_labor_hours` | `service_records` | `39799` | `labor_hours` | implausibly high labor hours |
| 1135 | `implausible_mileage_or_labor_hours` | `service_records` | `1482` | `labor_hours` | implausibly high labor hours |
| 1136 | `implausible_mileage_or_labor_hours` | `service_records` | `13204` | `labor_hours` | implausibly high labor hours |
| 1137 | `near_duplicate_records` | `sales` | `20501` | `created_at` | near duplicate of 13018 |
| 1138 | `near_duplicate_records` | `sales` | `20502` | `created_at` | near duplicate of 8852 |
| 1139 | `near_duplicate_records` | `sales` | `20503` | `created_at` | near duplicate of 16382 |
| 1140 | `near_duplicate_records` | `sales` | `20504` | `created_at` | near duplicate of 8796 |
| 1141 | `near_duplicate_records` | `sales` | `20505` | `created_at` | near duplicate of 8984 |
| 1142 | `near_duplicate_records` | `sales` | `20506` | `created_at` | near duplicate of 19312 |
| 1143 | `near_duplicate_records` | `sales` | `20507` | `created_at` | near duplicate of 9452 |
| 1144 | `near_duplicate_records` | `sales` | `20508` | `created_at` | near duplicate of 4021 |
| 1145 | `near_duplicate_records` | `sales` | `20509` | `created_at` | near duplicate of 4742 |
| 1146 | `near_duplicate_records` | `sales` | `20510` | `created_at` | near duplicate of 14535 |
| 1147 | `near_duplicate_records` | `sales` | `20511` | `created_at` | near duplicate of 16190 |
| 1148 | `near_duplicate_records` | `sales` | `20512` | `created_at` | near duplicate of 1295 |
| 1149 | `near_duplicate_records` | `sales` | `20513` | `created_at` | near duplicate of 11000 |
| 1150 | `near_duplicate_records` | `sales` | `20514` | `created_at` | near duplicate of 16900 |
| 1151 | `near_duplicate_records` | `sales` | `20515` | `created_at` | near duplicate of 16849 |
| 1152 | `near_duplicate_records` | `sales` | `20516` | `created_at` | near duplicate of 16925 |
| 1153 | `near_duplicate_records` | `sales` | `20517` | `created_at` | near duplicate of 5651 |
| 1154 | `near_duplicate_records` | `sales` | `20518` | `created_at` | near duplicate of 8704 |
| 1155 | `near_duplicate_records` | `sales` | `20519` | `created_at` | near duplicate of 10467 |
| 1156 | `near_duplicate_records` | `sales` | `20520` | `created_at` | near duplicate of 5760 |
| 1157 | `near_duplicate_records` | `service_records` | `48001` | `repeat_repair_flag` | near duplicate of 21898 |
| 1158 | `near_duplicate_records` | `service_records` | `48002` | `repeat_repair_flag` | near duplicate of 39752 |
| 1159 | `near_duplicate_records` | `service_records` | `48003` | `repeat_repair_flag` | near duplicate of 27057 |
| 1160 | `near_duplicate_records` | `service_records` | `48004` | `repeat_repair_flag` | near duplicate of 25824 |
| 1161 | `near_duplicate_records` | `service_records` | `48005` | `repeat_repair_flag` | near duplicate of 21329 |
| 1162 | `near_duplicate_records` | `service_records` | `48006` | `repeat_repair_flag` | near duplicate of 16774 |
| 1163 | `near_duplicate_records` | `service_records` | `48007` | `repeat_repair_flag` | near duplicate of 41278 |
| 1164 | `near_duplicate_records` | `service_records` | `48008` | `repeat_repair_flag` | near duplicate of 2027 |
| 1165 | `near_duplicate_records` | `service_records` | `48009` | `repeat_repair_flag` | near duplicate of 39074 |
| 1166 | `near_duplicate_records` | `service_records` | `48010` | `repeat_repair_flag` | near duplicate of 43543 |
| 1167 | `near_duplicate_records` | `service_records` | `48011` | `repeat_repair_flag` | near duplicate of 26158 |
| 1168 | `near_duplicate_records` | `service_records` | `48012` | `repeat_repair_flag` | near duplicate of 41927 |
| 1169 | `near_duplicate_records` | `service_records` | `48013` | `repeat_repair_flag` | near duplicate of 1419 |
| 1170 | `near_duplicate_records` | `service_records` | `48014` | `repeat_repair_flag` | near duplicate of 4895 |
| 1171 | `near_duplicate_records` | `service_records` | `48015` | `repeat_repair_flag` | near duplicate of 42074 |
| 1172 | `near_duplicate_records` | `service_records` | `48016` | `repeat_repair_flag` | near duplicate of 41383 |
| 1173 | `near_duplicate_records` | `service_records` | `48017` | `repeat_repair_flag` | near duplicate of 10974 |
| 1174 | `near_duplicate_records` | `service_records` | `48018` | `repeat_repair_flag` | near duplicate of 17952 |
| 1175 | `near_duplicate_records` | `service_records` | `48019` | `repeat_repair_flag` | near duplicate of 14024 |
| 1176 | `near_duplicate_records` | `service_records` | `48020` | `repeat_repair_flag` | near duplicate of 42647 |
| 1177 | `near_duplicate_records` | `service_records` | `48021` | `repeat_repair_flag` | near duplicate of 38133 |
| 1178 | `near_duplicate_records` | `service_records` | `48022` | `repeat_repair_flag` | near duplicate of 41832 |
| 1179 | `near_duplicate_records` | `service_records` | `48023` | `repeat_repair_flag` | near duplicate of 46541 |
| 1180 | `near_duplicate_records` | `service_records` | `48024` | `repeat_repair_flag` | near duplicate of 20415 |
| 1181 | `near_duplicate_records` | `service_records` | `48025` | `repeat_repair_flag` | near duplicate of 9477 |
| 1182 | `near_duplicate_records` | `warranty_claims` | `3051` | `repeat_claim_flag` | near duplicate of 424 |
| 1183 | `near_duplicate_records` | `warranty_claims` | `3052` | `repeat_claim_flag` | near duplicate of 954 |
| 1184 | `near_duplicate_records` | `warranty_claims` | `3053` | `repeat_claim_flag` | near duplicate of 348 |
| 1185 | `near_duplicate_records` | `warranty_claims` | `3054` | `repeat_claim_flag` | near duplicate of 2275 |
| 1186 | `near_duplicate_records` | `warranty_claims` | `3055` | `repeat_claim_flag` | near duplicate of 1734 |
| 1187 | `near_duplicate_records` | `warranty_claims` | `3056` | `repeat_claim_flag` | near duplicate of 789 |
| 1188 | `near_duplicate_records` | `warranty_claims` | `3057` | `repeat_claim_flag` | near duplicate of 183 |
| 1189 | `near_duplicate_records` | `warranty_claims` | `3058` | `repeat_claim_flag` | near duplicate of 1050 |
| 1190 | `near_duplicate_records` | `complaints` | `1851` | `days_to_resolution` | near duplicate of 207 |
| 1191 | `near_duplicate_records` | `complaints` | `1852` | `days_to_resolution` | near duplicate of 1711 |
| 1192 | `near_duplicate_records` | `complaints` | `1853` | `days_to_resolution` | near duplicate of 439 |
| 1193 | `near_duplicate_records` | `complaints` | `1854` | `days_to_resolution` | near duplicate of 299 |
| 1194 | `near_duplicate_records` | `complaints` | `1855` | `days_to_resolution` | near duplicate of 891 |
| 1195 | `near_duplicate_records` | `satisfaction` | `15001` | `comment_text` | near duplicate of 2971 |
| 1196 | `near_duplicate_records` | `satisfaction` | `15002` | `comment_text` | near duplicate of 4270 |
| 1197 | `near_duplicate_records` | `satisfaction` | `15003` | `comment_text` | near duplicate of 464 |
| 1198 | `near_duplicate_records` | `satisfaction` | `15004` | `comment_text` | near duplicate of 2898 |
| 1199 | `near_duplicate_records` | `satisfaction` | `15005` | `comment_text` | near duplicate of 5988 |
| 1200 | `near_duplicate_records` | `satisfaction` | `15006` | `comment_text` | near duplicate of 2146 |
| 1201 | `near_duplicate_records` | `satisfaction` | `15007` | `comment_text` | near duplicate of 14455 |
| 1202 | `exact_duplicate_rows` | `sales` | `7963` | `entire_row` | second byte-equivalent CSV row added |
| 1203 | `exact_duplicate_rows` | `sales` | `15739` | `entire_row` | second byte-equivalent CSV row added |
| 1204 | `exact_duplicate_rows` | `sales` | `1872` | `entire_row` | second byte-equivalent CSV row added |
| 1205 | `exact_duplicate_rows` | `sales` | `6790` | `entire_row` | second byte-equivalent CSV row added |
| 1206 | `exact_duplicate_rows` | `sales` | `5051` | `entire_row` | second byte-equivalent CSV row added |
| 1207 | `exact_duplicate_rows` | `sales` | `3424` | `entire_row` | second byte-equivalent CSV row added |
| 1208 | `exact_duplicate_rows` | `sales` | `12449` | `entire_row` | second byte-equivalent CSV row added |
| 1209 | `exact_duplicate_rows` | `sales` | `15265` | `entire_row` | second byte-equivalent CSV row added |
| 1210 | `exact_duplicate_rows` | `sales` | `6887` | `entire_row` | second byte-equivalent CSV row added |
| 1211 | `exact_duplicate_rows` | `sales` | `8794` | `entire_row` | second byte-equivalent CSV row added |
| 1212 | `exact_duplicate_rows` | `sales` | `1137` | `entire_row` | second byte-equivalent CSV row added |
| 1213 | `exact_duplicate_rows` | `sales` | `7872` | `entire_row` | second byte-equivalent CSV row added |
| 1214 | `exact_duplicate_rows` | `sales` | `9539` | `entire_row` | second byte-equivalent CSV row added |
| 1215 | `exact_duplicate_rows` | `sales` | `19804` | `entire_row` | second byte-equivalent CSV row added |
| 1216 | `exact_duplicate_rows` | `sales` | `11740` | `entire_row` | second byte-equivalent CSV row added |
| 1217 | `exact_duplicate_rows` | `sales` | `15463` | `entire_row` | second byte-equivalent CSV row added |
| 1218 | `exact_duplicate_rows` | `sales` | `14885` | `entire_row` | second byte-equivalent CSV row added |
| 1219 | `exact_duplicate_rows` | `sales` | `8763` | `entire_row` | second byte-equivalent CSV row added |
| 1220 | `exact_duplicate_rows` | `sales` | `14905` | `entire_row` | second byte-equivalent CSV row added |
| 1221 | `exact_duplicate_rows` | `sales` | `13570` | `entire_row` | second byte-equivalent CSV row added |
| 1222 | `exact_duplicate_rows` | `service_records` | `35120` | `entire_row` | second byte-equivalent CSV row added |
| 1223 | `exact_duplicate_rows` | `service_records` | `36471` | `entire_row` | second byte-equivalent CSV row added |
| 1224 | `exact_duplicate_rows` | `service_records` | `36151` | `entire_row` | second byte-equivalent CSV row added |
| 1225 | `exact_duplicate_rows` | `service_records` | `17294` | `entire_row` | second byte-equivalent CSV row added |
| 1226 | `exact_duplicate_rows` | `service_records` | `25090` | `entire_row` | second byte-equivalent CSV row added |
| 1227 | `exact_duplicate_rows` | `service_records` | `44536` | `entire_row` | second byte-equivalent CSV row added |
| 1228 | `exact_duplicate_rows` | `service_records` | `44870` | `entire_row` | second byte-equivalent CSV row added |
| 1229 | `exact_duplicate_rows` | `service_records` | `9194` | `entire_row` | second byte-equivalent CSV row added |
| 1230 | `exact_duplicate_rows` | `service_records` | `33263` | `entire_row` | second byte-equivalent CSV row added |
| 1231 | `exact_duplicate_rows` | `service_records` | `1510` | `entire_row` | second byte-equivalent CSV row added |
| 1232 | `exact_duplicate_rows` | `service_records` | `26189` | `entire_row` | second byte-equivalent CSV row added |
| 1233 | `exact_duplicate_rows` | `service_records` | `31497` | `entire_row` | second byte-equivalent CSV row added |
| 1234 | `exact_duplicate_rows` | `service_records` | `38310` | `entire_row` | second byte-equivalent CSV row added |
| 1235 | `exact_duplicate_rows` | `service_records` | `47516` | `entire_row` | second byte-equivalent CSV row added |
| 1236 | `exact_duplicate_rows` | `service_records` | `20146` | `entire_row` | second byte-equivalent CSV row added |
| 1237 | `exact_duplicate_rows` | `service_records` | `678` | `entire_row` | second byte-equivalent CSV row added |
| 1238 | `exact_duplicate_rows` | `service_records` | `10259` | `entire_row` | second byte-equivalent CSV row added |
| 1239 | `exact_duplicate_rows` | `service_records` | `39432` | `entire_row` | second byte-equivalent CSV row added |
| 1240 | `exact_duplicate_rows` | `service_records` | `38575` | `entire_row` | second byte-equivalent CSV row added |
| 1241 | `exact_duplicate_rows` | `service_records` | `15045` | `entire_row` | second byte-equivalent CSV row added |
| 1242 | `exact_duplicate_rows` | `service_records` | `15766` | `entire_row` | second byte-equivalent CSV row added |
| 1243 | `exact_duplicate_rows` | `service_records` | `40567` | `entire_row` | second byte-equivalent CSV row added |
| 1244 | `exact_duplicate_rows` | `service_records` | `9927` | `entire_row` | second byte-equivalent CSV row added |
| 1245 | `exact_duplicate_rows` | `service_records` | `29268` | `entire_row` | second byte-equivalent CSV row added |
| 1246 | `exact_duplicate_rows` | `service_records` | `11780` | `entire_row` | second byte-equivalent CSV row added |
| 1247 | `exact_duplicate_rows` | `service_records` | `7413` | `entire_row` | second byte-equivalent CSV row added |
| 1248 | `exact_duplicate_rows` | `service_records` | `44291` | `entire_row` | second byte-equivalent CSV row added |
| 1249 | `exact_duplicate_rows` | `service_records` | `47880` | `entire_row` | second byte-equivalent CSV row added |
| 1250 | `exact_duplicate_rows` | `service_records` | `36735` | `entire_row` | second byte-equivalent CSV row added |
| 1251 | `exact_duplicate_rows` | `service_records` | `28696` | `entire_row` | second byte-equivalent CSV row added |
| 1252 | `exact_duplicate_rows` | `service_records` | `32160` | `entire_row` | second byte-equivalent CSV row added |
| 1253 | `exact_duplicate_rows` | `service_records` | `40647` | `entire_row` | second byte-equivalent CSV row added |
| 1254 | `exact_duplicate_rows` | `service_records` | `33851` | `entire_row` | second byte-equivalent CSV row added |
| 1255 | `exact_duplicate_rows` | `service_records` | `3140` | `entire_row` | second byte-equivalent CSV row added |
| 1256 | `exact_duplicate_rows` | `service_records` | `35302` | `entire_row` | second byte-equivalent CSV row added |
| 1257 | `exact_duplicate_rows` | `warranty_claims` | `463` | `entire_row` | second byte-equivalent CSV row added |
| 1258 | `exact_duplicate_rows` | `warranty_claims` | `1313` | `entire_row` | second byte-equivalent CSV row added |
| 1259 | `exact_duplicate_rows` | `warranty_claims` | `2654` | `entire_row` | second byte-equivalent CSV row added |
| 1260 | `exact_duplicate_rows` | `warranty_claims` | `706` | `entire_row` | second byte-equivalent CSV row added |
| 1261 | `exact_duplicate_rows` | `warranty_claims` | `401` | `entire_row` | second byte-equivalent CSV row added |
| 1262 | `exact_duplicate_rows` | `warranty_claims` | `988` | `entire_row` | second byte-equivalent CSV row added |
| 1263 | `exact_duplicate_rows` | `warranty_claims` | `2427` | `entire_row` | second byte-equivalent CSV row added |
| 1264 | `exact_duplicate_rows` | `warranty_claims` | `1100` | `entire_row` | second byte-equivalent CSV row added |
| 1265 | `exact_duplicate_rows` | `warranty_claims` | `2668` | `entire_row` | second byte-equivalent CSV row added |
| 1266 | `exact_duplicate_rows` | `warranty_claims` | `1102` | `entire_row` | second byte-equivalent CSV row added |
| 1267 | `exact_duplicate_rows` | `warranty_claims` | `2215` | `entire_row` | second byte-equivalent CSV row added |
| 1268 | `exact_duplicate_rows` | `warranty_claims` | `2786` | `entire_row` | second byte-equivalent CSV row added |
| 1269 | `exact_duplicate_rows` | `complaints` | `314` | `entire_row` | second byte-equivalent CSV row added |
| 1270 | `exact_duplicate_rows` | `complaints` | `1085` | `entire_row` | second byte-equivalent CSV row added |
| 1271 | `exact_duplicate_rows` | `complaints` | `459` | `entire_row` | second byte-equivalent CSV row added |
| 1272 | `exact_duplicate_rows` | `complaints` | `1836` | `entire_row` | second byte-equivalent CSV row added |
| 1273 | `exact_duplicate_rows` | `complaints` | `1147` | `entire_row` | second byte-equivalent CSV row added |
| 1274 | `exact_duplicate_rows` | `complaints` | `1291` | `entire_row` | second byte-equivalent CSV row added |
| 1275 | `exact_duplicate_rows` | `complaints` | `1541` | `entire_row` | second byte-equivalent CSV row added |
| 1276 | `exact_duplicate_rows` | `complaints` | `1702` | `entire_row` | second byte-equivalent CSV row added |
| 1277 | `exact_duplicate_rows` | `satisfaction` | `10303` | `entire_row` | second byte-equivalent CSV row added |
| 1278 | `exact_duplicate_rows` | `satisfaction` | `12279` | `entire_row` | second byte-equivalent CSV row added |
| 1279 | `exact_duplicate_rows` | `satisfaction` | `2130` | `entire_row` | second byte-equivalent CSV row added |
| 1280 | `exact_duplicate_rows` | `satisfaction` | `9550` | `entire_row` | second byte-equivalent CSV row added |
| 1281 | `exact_duplicate_rows` | `satisfaction` | `14911` | `entire_row` | second byte-equivalent CSV row added |
| 1282 | `exact_duplicate_rows` | `satisfaction` | `5971` | `entire_row` | second byte-equivalent CSV row added |
| 1283 | `exact_duplicate_rows` | `satisfaction` | `5222` | `entire_row` | second byte-equivalent CSV row added |
| 1284 | `exact_duplicate_rows` | `satisfaction` | `12866` | `entire_row` | second byte-equivalent CSV row added |
| 1285 | `exact_duplicate_rows` | `satisfaction` | `14757` | `entire_row` | second byte-equivalent CSV row added |
| 1286 | `exact_duplicate_rows` | `satisfaction` | `4402` | `entire_row` | second byte-equivalent CSV row added |
| 1287 | `exact_duplicate_rows` | `satisfaction` | `6696` | `entire_row` | second byte-equivalent CSV row added |
| 1288 | `exact_duplicate_rows` | `satisfaction` | `12950` | `entire_row` | second byte-equivalent CSV row added |
| 1289 | `exact_duplicate_rows` | `satisfaction` | `4520` | `entire_row` | second byte-equivalent CSV row added |
| 1290 | `exact_duplicate_rows` | `satisfaction` | `254` | `entire_row` | second byte-equivalent CSV row added |
| 1291 | `exact_duplicate_rows` | `satisfaction` | `2766` | `entire_row` | second byte-equivalent CSV row added |

## Intended relational keys

- `salespeople.branch_id -> branches.branch_id`
- `inventory.model_id -> models.model_id`; `inventory.branch_id -> branches.branch_id`
- `sales.inventory_id -> inventory.inventory_id`; `sales.branch_id -> branches.branch_id`; `sales.salesperson_id -> salespeople.salesperson_id`
- `service_records.inventory_id -> inventory.inventory_id`; `service_records.branch_id -> branches.branch_id`; `service_records.sale_id -> sales.sale_id`
- `warranty_claims.service_id -> service_records.service_id`; `inventory_id -> inventory.inventory_id`; `sale_id -> sales.sale_id`; `branch_id -> branches.branch_id`
- `complaints.branch_id -> branches.branch_id`; nullable transaction keys point to sales, service records, and warranty claims
- `satisfaction.branch_id -> branches.branch_id`; nullable source keys point to sales, service records, and complaints

The orphan-key entries in the ledger are the only intentionally injected referential-integrity violations; duplicate rows can create repeated PK values by design.
