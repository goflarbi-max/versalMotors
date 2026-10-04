# VersalMotors Management Brief

**Reporting comparison:** 1 January–30 June 2025 versus the same six months of 2024  
**Inventory snapshot date:** 30 June 2025

## Executive summary

Completed-sale revenue grew strongly in the first half of 2025, reaching GHS 2.349 billion from 7,276 completed sales, compared with GHS 1.160 billion from 3,546 completed sales in the first half of 2024. However, after-sales pressure grew faster than sales in important areas. Valid complaints increased to 786, while approved warranty cost reached GHS 1.718 million. The available inventory also contains 1,258 vehicles whose age exceeds 1.5 times the median for their model. Management should protect the value of sales growth by addressing aged inventory, complaint incidence, and warranty exposure.

## Three things management should investigate

### 1. Why is so much available inventory materially older than its model peers?

- 5,158 valid, non-orphan vehicles were available at the snapshot date.
- 1,258 vehicles, or 24.4%, were older than 1.5 times the median age for their model.
- The overall median available-stock age was 502 days; the oldest available vehicle was 1,003 days old.
- The oldest vehicle was VIN `VMGNJVWHT80011552`, a Hilux at Tema.

Management action: identify whether pricing, model mix, branch allocation, or sales execution is preventing these vehicles from moving. Start with the oldest vehicles and branches holding the largest aged-stock value.

Evidence: `inventory`, joined to `models` and `branches`; available rows with valid acquisition dates and without model or branch orphan flags.

### 2. Why are valid complaints rising faster than completed sales?

- Valid complaints increased from 330 in H1 2024 to 786 in H1 2025, a 138.2% increase.
- Completed sales increased from 3,546 to 7,276, a 105.2% increase.
- Complaints therefore increased from 9.31 to 10.80 per 100 completed sales, a 16.1% deterioration in complaint incidence.
- Accra recorded the largest complaint volume in H1 2025 with 182 complaints; Kumasi followed with 149 and Tema with 95.
- Warranty complaints at Accra increased from 10 to 42, while service-delay complaints at Kumasi increased from 11 to 29.

Management action: review complaint root causes and resolution journeys in Accra, Kumasi, and Tema, normalising each branch by its sales and service volumes before judging performance.

Evidence: `complaints`, joined to `branches`, and `sales`; excludes invalid complaint dates and orphan branch keys and uses completed sales as the volume denominator.

### 3. What is driving the increase and concentration in warranty exposure?

- Valid warranty claims increased from 589 in H1 2024 to 1,263 in H1 2025, a 114.4% increase.
- Approved warranty cost increased from GHS 792,849.38 to GHS 1,717,523.29, a 116.6% increase.
- Approved cost per completed sale increased from GHS 223.59 to GHS 236.05, a 5.6% increase.
- Hilux generated 402 claims and GHS 539,486.19 of approved cost in H1 2025, representing 31.4% of valid approved warranty cost. Its approved cost was GHS 253,057.92 in H1 2024.
- The largest model-branch concentrations in H1 2025 were Hilux at Kumasi (GHS 122,291.38) and Hilux at Accra (GHS 92,120.51).

Management action: drill into Hilux failure categories, parts, repair recurrence, model year, and the Kumasi and Accra service processes. Compare rates per Hilux sold or serviced before concluding that the model itself is defective.

Evidence: `warranty_claims`, joined to `inventory`, `models`, and `branches`; approved amounts only, excluding orphan inventory and branch keys.

## Management brief

### Key findings

- H1 completed-sale revenue increased 102.4% year over year, while completed units increased 105.2%. Average revenue per completed sale therefore softened slightly rather than driving the growth.
- The complaint rate worsened despite higher volume: complaints rose 138.2%, faster than completed sales.
- Warranty claim volume and approved cost more than doubled. Hilux alone accounted for almost one-third of H1 2025 approved warranty cost.
- Nearly one-quarter of available vehicles meet the category-relative aged-stock threshold, tying up capital and increasing discount risk.

### Risks

- Continued sales growth could mask deteriorating customer experience if complaint incidence is viewed only as a raw count.
- Aged inventory and rising warranty costs may erode cash efficiency and gross margin even while revenue grows.

### Opportunities

- Targeted aged-stock actions by VIN, model, and branch can release working capital without applying indiscriminate discounts.
- Failure-category analysis on Hilux claims can focus supplier, technical, and service-process interventions where the financial exposure is greatest.

### Recommended next steps

1. Assign owners to the three investigations above and review results weekly.
2. Add complaint-per-100-sales and warranty-cost-per-sale indicators to management monitoring.
3. Produce an aged-stock action list containing VIN, branch, model, age, acquisition cost, current listed price, and proposed disposition.
4. Do not infer root cause from these associations alone; validate against service volume, model sales, parts, technician, campaign, and customer-contact data.

## Evidence and limitations

This brief was generated from `data/business.duckdb`, which is built from the cleaned operational tables. `data/generator_truth.md` was not used as an analytical source. The comparison uses equal six-month periods to avoid comparing a partial 2025 year with a full prior year. The data supports identification of patterns and investigation priorities, but it does not establish causality. Branch names are not unique identifiers—Accra and Kumasi each have more than one branch ID—so branch-level operational follow-up should use `branch_id` as well as the displayed name.
