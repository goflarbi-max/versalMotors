# Project Name

**versalMotors — Automotive Business Intelligence System**

## Business Problem

versalMotors has sales, inventory, service, warranty, complaint, and customer-satisfaction data spread across separate operational records. Management needs a reliable way to monitor performance, investigate problems, understand customer outcomes, and identify data-quality risks without manually reconciling those sources.

## Solution

This project provides a multipage business-intelligence application that turns the operational records into auditable management metrics. The current implementation includes deterministic data generation, documented profiling, an explainable cleaning pipeline, a DuckDB analytical database, tested metrics, a filterable management Overview, and warranty-cost drill-down from model to branch to individual claims.

## Dataset

The repository contains nine synthetic raw CSV tables covering branches, models, salespeople, inventory, sales, service records, warranty claims, complaints, and satisfaction. The data spans approximately 2.5 years, uses Ghanaian cedi (`GHS`), and deliberately contains realistic quality problems for testing. Cleaned outputs are generated locally in `data/cleaned/` and loaded into `data/business.duckdb`; both are excluded from Git and can be rebuilt from source. `docs/data_dictionary.md` records the observed schema and profile.

## How the System Works

1. `scripts/generate_dataset.py` creates deterministic synthetic raw CSVs.
2. `scripts/profile_raw_data.py` profiles columns, duplicates, suspicious values, and relationships.
3. `src/data/cleaning.py` standardises reviewed values, safely parses fields, flags questionable records, removes only exact duplicates, and writes an audit log.
4. `scripts/build_database.py` rebuilds the cleaned CSVs and local DuckDB database.
5. `src/analytics/metrics.py` calculates tested business metrics without UI or database side effects.
6. Streamlit presents persistent filters, management KPIs, period comparisons, charts, and warranty drill-down evidence. Ask the Business, Management Brief, and Data Quality remain placeholders.

## Architecture

```text
Business Data -> Data Processing -> Database -> Analysis -> AI Layer -> Dashboard -> Management
Raw CSVs      -> Audited Cleaning -> DuckDB   -> Metrics  -> Planned  -> Streamlit -> Decisions
```

The implemented path currently runs through the dashboard. The runtime AI layer is still planned.

## Technologies (What + Why)

- **Python and pandas:** generate, clean, test, and analyse the dataset reproducibly.
- **Streamlit:** provides responsive multipage navigation, persistent filters, KPI cards, charts, and drill-down evidence.
- **CSV:** keeps raw and cleaned pipeline stages portable and auditable.
- **DuckDB:** stores the local analytical model and supports independent SQL verification of important calculations.
- **pytest:** checks cleaning contracts, formulas, filter safety, SQL parity, and drill-down reconciliation.
- **Git and GitHub:** provide version control, traceability, and project history.

## AI Usage

AI has assisted development by drafting code, documentation, dataset patterns, tests, and quality checks. Its output is reviewed against source data, cleaning logs, SQL totals, and hand-built fixtures. The planned runtime AI layer may help users ask business questions and prepare management summaries, but no runtime AI feature exists yet. AI does not make business decisions, silently repair ambiguous records, or replace evidence from the database.

## Data Quality

The raw data intentionally includes missing values, duplicates, name and category variants, invalid dates, negative amounts, malformed VINs, arithmetic inconsistencies, and orphan references. Raw files remain unchanged. The cleaning pipeline preserves raw companions, removes only exact duplicates, uses reviewed exact mappings rather than fuzzy guesses, converts invalid values to null with flags, and assigns `ERROR`, `WARNING`, or `VALID` status. Every action is recorded in `docs/cleaning_log.csv`. Orphan model references such as raw model ID `9002` remain flagged and are excluded from management metrics rather than displayed as a real model.

## Challenges

- Defining safe cleaning rules without inventing answers for ambiguous business fields.
- Separating exact duplicates from legitimate repeated transactions and near-duplicates.
- Preserving referential integrity across nine related tables with deliberately orphaned keys.
- Keeping the private generator answer key out of the public repository while retaining it locally for verification.
- Preventing invalid dimension relationships from appearing as legitimate `Unmapped` categories without discarding otherwise valid records.
- Keeping KPI totals consistent between pandas calculations and independent DuckDB SQL checks.

## AI Mistakes

- **Situation:** An AI-assisted `git add .` included the private generator answer key in an early public commit.
- **How discovered:** The committed-file list showed `data/generator_truth.md` among the published files.
- **How corrected:** The file was added to `.gitignore`, removed from current Git tracking, and retained locally. It still exists in earlier Git history, so a history rewrite would be required for complete removal.
- **Situation:** An attempted orphan-model fix created a synthetic `Model ID 9002 (unresolved)` category, moving a source-data error into the management chart.
- **How discovered:** Raw-to-dimension reconciliation and the Gross margin by model chart showed that 12 inventory records referenced model ID `9002`, which does not exist in the model source.
- **How corrected:** The synthetic member was removed. The raw ID is preserved for audit, the cleaned relationship is null and flagged as an error, affected records are excluded before margin aggregation, and explicit regression tests prevent `Unmapped` or placeholder model labels from reaching management results.

## What You Learned

- Profile raw data before designing dashboards or committing to cleaning rules.
- Keep observed facts separate from business assumptions and request clarification when meaning is uncertain.
- Treat generated answer keys, secrets, local databases, and caches as private artifacts from the start.
- Build navigation and data foundations before investing in presentation details.
- A renamed error is still an error; data-quality problems should remain auditable and must not be promoted into management categories.
- Period comparisons and drill-down totals need independent tests so charts reconcile to their underlying records.

## Future Improvements

- Complete the Data Quality page with visible counts and affected-record evidence.
- Expand drill-down beyond warranty costs to sales, inventory, service, and complaints.
- Add a validated business-question interface and clearly governed AI summaries.
- Generate an evidence-backed Management Brief from tested analytical results.
- Add browser-level mobile testing and deployment checks.

## Daily Progress Log

### Day 2 - 2026-10-01 - Analytics, Overview & Drill-Down

- Done: Built the audited cleaning and DuckDB pipeline, tested core metrics, persistent business filters, period-over-period management KPIs, responsive Overview charts, and warranty drill-down from model to branch to downloadable claims; corrected orphan and branch mapping issues so invalid relationships do not become management categories.
- Files: `src/data/cleaning.py`, `scripts/build_database.py`, `src/analytics/metrics.py`, `src/analytics/drilldown.py`, `src/ui/filters.py`, `pages/overview.py`, `pages/investigate.py`, `tests/`, `docs/cleaning_log.csv`, `docs/ai_mistakes.md`.
- Commit: `b6b881e Add drill-down investigation` (latest completed commit before this update)
- Next: Build the Data Quality page, then ground Ask the Business and Management Brief in tested database evidence.

### Day 2 - 2026-09-30 - README Submission Compliance

- Done: Rebuilt the README with the required 14-section structure, documented only repository-backed capabilities, and established the newest-first daily progress log.
- Files: `README.md`.
- Commit: `5d9dda9 Update README for submission requirements`
- Next: Confirm cleaning rules and build the auditable DuckDB data pipeline.

### Day 1 - 2026-09-30 - Streamlit App Skeleton

- Done: Generated and profiled the synthetic automotive dataset, documented its structure and assumptions, and launched a Streamlit shell on `localhost:8501` with Overview, Investigate, Ask the Business, Management Brief, and Data Quality pages.
- Files: `app.py`, `pages/`, `data/raw/`, `docs/data_dictionary.md`, `docs/assumptions.md`, `scripts/generate_dataset.py`, `scripts/profile_raw_data.py`, `.env.example`, `.gitignore`, `requirements.txt`.
- Commit: `cca4a75 Create Streamlit app skeleton`
- Next: Confirm cleaning rules and build the auditable DuckDB data pipeline.
