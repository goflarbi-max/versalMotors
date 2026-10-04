# Project Name

**versalMotors — Automotive Business Intelligence System**

## Business Problem

versalMotors has sales, inventory, service, warranty, complaint, and customer-satisfaction data spread across separate operational records. Management needs a reliable way to monitor performance, investigate problems, understand customer outcomes, and identify data-quality risks without manually reconciling those sources.

## Solution

This project provides a multipage business-intelligence application that turns operational records into auditable management metrics. The implementation includes deterministic data generation, documented profiling, an explainable cleaning pipeline, a DuckDB analytical database, tested metrics, a filterable management Overview, warranty-cost drill-down, data-quality monitoring, evidence-backed business questions, and downloadable management briefs.

## Dataset

The repository contains nine synthetic raw CSV tables covering branches, models, salespeople, inventory, sales, service records, warranty claims, complaints, and satisfaction. The data spans approximately 2.5 years, uses Ghanaian cedi (`GHS`), and deliberately contains realistic quality problems for testing. Cleaned outputs are generated locally in `data/cleaned/` and loaded into `data/business.duckdb`; both are excluded from Git and can be rebuilt from source. `docs/data_dictionary.md` records the observed schema and profile.

## How the System Works

1. `scripts/generate_dataset.py` creates deterministic synthetic raw CSVs.
2. `scripts/profile_raw_data.py` profiles columns, duplicates, suspicious values, and relationships.
3. `src/data/cleaning.py` standardises reviewed values, safely parses fields, flags questionable records, removes only exact duplicates, and writes an audit log.
4. `scripts/build_database.py` rebuilds the cleaned CSVs and local DuckDB database.
5. `src/analytics/metrics.py` calculates tested business metrics without UI or database side effects.
6. Streamlit presents persistent filters, management KPIs, period comparisons, charts, warranty drill-down evidence, data-quality checks, and PDF exports.
7. The optional Gemini layer tries a primary model and lighter fallback model with bounded transient-error retries. Reviewed queries and deterministic evidence summaries remain available when every model is unavailable.

## Architecture

```text
Business Data -> Data Processing -> Database -> Analysis -> AI Layer        -> Dashboard -> Management
Raw CSVs      -> Audited Cleaning -> DuckDB   -> Metrics  -> Optional Gemini -> Streamlit -> Decisions
```

The AI layer is optional: reviewed database queries and deterministic summaries keep the dashboard operational during missing credentials, timeouts, rate limits, invalid generated SQL, and Gemini service failures. See `docs/architecture.md` for the detailed request and fallback flow.

## Technologies (What + Why)

- **Python and pandas:** generate, clean, test, and analyse the dataset reproducibly.
- **Streamlit:** provides responsive multipage navigation, persistent filters, KPI cards, charts, and drill-down evidence.
- **CSV:** keeps raw and cleaned pipeline stages portable and auditable.
- **DuckDB:** stores the local analytical model and supports independent SQL verification of important calculations.
- **pytest:** checks cleaning contracts, formulas, filter safety, SQL parity, and drill-down reconciliation.
- **Google Gen AI SDK:** provides optional evidence-grounded questions and management narratives using the configurable `gemini-3.8-flash` model.
- **fpdf2:** creates genuine downloadable PDF management briefs and operational reports.
- **Git and GitHub:** provide version control, traceability, and project history.

## AI Usage

AI has assisted development by drafting code, documentation, dataset patterns, tests, and quality checks. At runtime, Gemini can translate supported business questions into read-only queries and turn returned evidence into concise narratives. Every generated query passes through table and operation allowlists, and response numbers are checked against request evidence. For `429`, `5xx`, and timeout failures, the client uses bounded retries and then tries a configured lighter model. If all models fail, credentials are absent, SQL is rejected, or a narrative is unverified, reviewed deterministic queries and evidence summaries take over without exposing provider errors. AI does not calculate source metrics, make business decisions, silently repair ambiguous records, or replace database evidence.

## Data Quality

The raw data intentionally includes missing values, duplicates, name and category variants, invalid dates, negative amounts, malformed VINs, arithmetic inconsistencies, and orphan references. Raw files remain unchanged. The cleaning pipeline preserves raw companions, removes only exact duplicates, uses reviewed exact mappings rather than fuzzy guesses, converts invalid values to null with flags, and assigns `ERROR`, `WARNING`, or `VALID` status. Every action is recorded in `docs/cleaning_log.csv`. Orphan model references such as raw model ID `9002` remain flagged and are excluded from management metrics rather than displayed as a real model.

## Challenges

- Defining safe cleaning rules without inventing answers for ambiguous business fields.
- Separating exact duplicates from legitimate repeated transactions and near-duplicates.
- Preserving referential integrity across nine related tables with deliberately orphaned keys.
- Keeping the private generator answer key out of the public repository while retaining it locally for verification.
- Preventing invalid dimension relationships from appearing as legitimate `Unmapped` categories without discarding otherwise valid records.
- Keeping KPI totals consistent between pandas calculations and independent DuckDB SQL checks.
- Tracing recurring `Unmapped` chart values back through sales, inventory, and model joins, then enforcing orphan exclusion at the shared enrichment boundary instead of applying a cosmetic chart-only fix.
- Preventing generated SQL from accessing files or unapproved tables while still supporting legitimate CTE-based analytical queries.
- Keeping business-question and management-brief workflows useful when Gemini credentials are absent or the API returns `503`, rate-limit, or timeout failures.
- Verifying every AI-reported number against request evidence and suppressing narratives that cannot be grounded.
- Producing genuine PDF downloads instead of renaming plain text with a `.pdf` extension.
- Keeping implementation-level SQL hidden from the user interface while retaining evidence tables and internal auditability.
- Managing Streamlit widget state so a persistent quick-question selection cannot override typed follow-ups, repeat an old answer, or make another quick-question control appear unresponsive.

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
- External AI services must be optional enhancements; deterministic business logic is the reliable product foundation.
- Read-only database mode alone is insufficient for generated SQL because analytical engines may still expose filesystem functions.

## Future Improvements

- Expand drill-down beyond warranty costs to sales, inventory, service, and complaints.
- Route all remaining AI-page KPI definitions through the shared analytics metrics layer.
- Expand the deterministic question registry beyond the four reviewed offline questions.
- Complete the evidence-object schema and strengthen prompt-injection testing.
- Add browser-level mobile testing and deployment checks.

## Daily Progress Log

### Day 4 - 2026-10-04 - Resilient AI Model Failover

- Done: Added bounded retry and lighter-model failover for Gemini `429`, `5xx`, and timeout failures; routed missing credentials, exhausted models, and rejected generated SQL through reviewed offline queries; generated concrete grounded answers for revenue trend, best branch, aged inventory, and complaints; replaced stateful suggestion controls with reliable buttons that run reviewed queries without waiting for Gemini; prevented raw provider errors and `FACTS` labels from reaching users; preserved typed-question AI handling; and documented the complete architecture.
- Files: `src/ai/gemini_client.py`, `src/ai/fallback.py`, `src/ai/guardrails.py`, `pages/ask_the_business.py`, `tests/test_ai_fallback.py`, `tests/test_ask_business_resilience.py`, `.env.example`, `docs/architecture.md`, `README.md`.
- Commit: Current Day 4 AI resilience and question-flow commit.
- Next: Expand the reviewed offline question registry and consolidate remaining AI-page KPIs through `src/analytics/metrics.py`.

### Day 3 - 2026-10-03 - Governed AI, Data Quality & Management Reporting

- Done: Completed the Data Quality and Management Brief pages; secured Ask the Business with read-only SQL allowlists and numerical evidence checks; upgraded the configurable model to Gemini 3.8 Flash; added retries for transient API failures and deterministic no-Gemini fallbacks; removed SQL code from the user-facing evidence view; and added genuine PDF downloads for briefs, claims, and quality reports.
- Files: `pages/ask_the_business.py`, `pages/management_brief.py`, `pages/data_quality.py`, `src/ai/guardrails.py`, `src/ai/gemini_client.py`, `src/ai/fallback.py`, `src/ai/brief.py`, `src/database/connection.py`, `src/ui/pdf_exports.py`, `tests/test_ai_fallback.py`, `docs/day3_audit.md`, `docs/test_log.md`, `requirements.txt`, `.env.example`.
- Commits: `e2d7589 fix guardrails integration - complete Step 3`; `b689bfb Add management brief`; `1b5e938 Add data quality page`; current Day 3 resilience and reporting update.
- Next: Consolidate remaining AI-page metrics in `src/analytics/metrics.py`, complete the deterministic insights registry, and broaden drill-down coverage.

### Day 2 - 2026-10-02 - README, Analytics, Overview & Drill-Down

- Done: Rebuilt the README to satisfy the required 14-section structure; built the audited cleaning and DuckDB pipeline, tested core metrics, persistent business filters, period-over-period management KPIs, responsive Overview charts, and warranty drill-down from model to branch to downloadable claims; corrected orphan and branch mapping issues, and added an explicit orphan-model guard in shared dimension enrichment so invalid relationships do not become management categories.
- Files: `README.md`, `src/data/cleaning.py`, `scripts/build_database.py`, `src/analytics/metrics.py`, `src/analytics/drilldown.py`, `src/ui/filters.py`, `pages/overview.py`, `pages/investigate.py`, `tests/`, `docs/cleaning_log.csv`, `docs/ai_mistakes.md`.
- Commits: `5d9dda9 Update README for submission requirements`; `b6b881e Add drill-down investigation`; `055841d Complete Day 2 analytics and dashboard`.
- Next: Build the Data Quality page, then ground Ask the Business and Management Brief in tested database evidence.

### Day 1 - 2026-09-30 - Streamlit App Skeleton

- Done: Generated and profiled the synthetic automotive dataset, documented its structure and assumptions, and launched a Streamlit shell on `localhost:8501` with Overview, Investigate, Ask the Business, Management Brief, and Data Quality pages.
- Files: `app.py`, `pages/`, `data/raw/`, `docs/data_dictionary.md`, `docs/assumptions.md`, `scripts/generate_dataset.py`, `scripts/profile_raw_data.py`, `.env.example`, `.gitignore`, `requirements.txt`.
- Commit: `cca4a75 Create Streamlit app skeleton`
- Next: Confirm cleaning rules and build the auditable DuckDB data pipeline.
