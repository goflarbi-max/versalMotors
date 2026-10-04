# Project Name

**versalMotors — Automotive Business Intelligence System**

## Business Problem

versalMotors has sales, inventory, service, warranty, complaint, and customer-satisfaction data spread across separate operational records. Management needs a reliable way to monitor performance, investigate problems, understand customer outcomes, and identify data-quality risks without manually reconciling those sources.

## Solution

This project provides a multipage business-intelligence application that turns operational records into auditable management metrics. The implementation includes deterministic data generation, documented profiling, an explainable cleaning pipeline, a DuckDB analytical database, tested metrics, a filterable management Overview, warranty-cost drill-down, data-quality monitoring, evidence-backed business questions, and downloadable management briefs.

### Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

The database and cleaned CSVs are generated artifacts. On a fresh clone or Streamlit Cloud deployment, `app.py` automatically builds and validates them from the committed raw CSVs before opening the pages. You can still run `.\.venv\Scripts\python.exe scripts\build_database.py` explicitly when rebuilding data during development. Google Gemini is optional; copy `.env.example` to `.env` only when AI narration is wanted.

### Testing

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The Day 4 stress suite records 35 passing tests and 24 passing subtests across calculations, degraded schemas, bad chronology, filters, AI failures, unsupported questions, large data, and all five Streamlit pages. Full results and limitations are in `docs/test_log.md`.

## Dataset

The repository contains nine synthetic raw CSV tables covering branches, models, salespeople, inventory, sales, service records, warranty claims, complaints, and satisfaction. The data spans approximately 2.5 years, uses Ghanaian cedi (`GHS`), and deliberately contains realistic quality problems for testing. Raw CSVs are committed so a fresh clone can rebuild the application without access to private files. Cleaned outputs are generated locally in `data/cleaned/` and loaded into `data/business.duckdb`; both are excluded from Git. `docs/data_dictionary.md` records the observed schema and profile.

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
Business Data -> Data Processing -> Database -> Analysis -> Evidence -> AI & Guardrails -> Dashboard -> Management
Raw CSVs      -> Audited Cleaning -> DuckDB   -> Metrics  -> Objects  -> Optional Gemini  -> Streamlit -> Decisions
```

The AI layer is optional: reviewed database queries and deterministic summaries keep the dashboard operational during missing credentials, timeouts, rate limits, invalid generated SQL, and Gemini service failures. See `docs/architecture.md` for the Mermaid diagrams and exported PNG.

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

The raw data intentionally includes missing values, duplicates, name and category variants, invalid dates, negative amounts, malformed VINs, arithmetic inconsistencies, and orphan references. Raw files remain unchanged. As recorded in `docs/cleaning_log.md`, the pipeline removes only exact duplicates—20 sales, 35 service records, 12 warranty claims, 8 complaints, and 15 satisfaction rows—while retaining questionable non-duplicates with flags. It nulls and flags 20 negative inventory amounts, 15 negative sales amounts, 20 negative service amounts, 10 negative warranty amounts, and 10 negative complaint amounts instead of treating them as credits. Reviewed exact mappings replace fuzzy guessing; invalid values retain raw companions; missing amounts remain null; and row severity follows `ERROR > WARNING > VALID`. Orphan references remain auditable and are excluded from management calculations when the relationship is required. Every action is recorded in `docs/cleaning_log.csv`.

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
- Selecting management priorities from comparable periods and valid relationships without treating synthetic-data ground truth as business evidence or implying causation from associations.
- Bootstrapping a generated analytical database on Streamlit Cloud, where ignored local artifacts and manual terminal instructions are unavailable to hosted users.
- Implementing the approved DD/MM-first date rule while retaining ambiguous inputs and invalid-date flags rather than silently choosing a convenient interpretation.
- Keeping missing totals null while exposing calculated companion values, so management metrics never confuse reconstruction with a source-recorded amount.
- Enforcing the approved one-completed-sale-per-VIN and near-duplicate rules without automatically deleting legitimate transactions that merely look similar.

## AI Mistakes

The following is reproduced verbatim from `docs/ai_mistakes.md`:

```text
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



- Error on 'Which branch has highest complaints?': 404 models/gemini-1.5-flash is not found for API version v1beta, or is not supported for generateContent. Call ModelService.ListModels to see the list of available models and their supported methods.
## Stress-test timing attribution

- **Situation:** I initially treated a 24.4-second subprocess measurement as Data Quality page load time.
- **How discovered:** A phased `AppTest` measurement separated Streamlit shell startup from child-page rendering and showed 11.9 seconds of test-shell startup, 3.625 seconds for the cold page, and 1.182 seconds for a cached rerun.
- **How corrected:** I recorded the isolated timings in `docs/test_log.md`, retained the useful caching/query-batching improvements, and stopped attributing process startup overhead to the page itself.

## Hosted database bootstrap

- **Situation:** I verified that a fresh clone could run after a manual database build, but the deployed Streamlit app had no shell step to create the ignored DuckDB file and showed an unavailable-database error.
- **How discovered:** The hosted Overview screenshot showed `data/business.duckdb` was missing and instructed an end user to run a local command that is unavailable on the hosted page.
- **How corrected:** I added a locked, validated first-start bootstrap before page navigation. The app now builds DuckDB from the nine committed raw CSVs, verifies every required table, and shows a safe deployment message only if automatic preparation fails.
```

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
- Add normalized service-volume and model-population denominators to strengthen the management investigations in `docs/management_brief.md`.

## Daily Progress Log

### Day 5 - 2026-10-05 - Final Verification & Deployment Readiness

- Done: Completed the evidence-backed Management Brief; finalized the Mermaid architecture and PNG export; reconciled total revenue, units sold, and gross margin exactly against direct DuckDB SQL; verified `requirements.txt` in an isolated clean installation; confirmed all five Streamlit pages start from a fresh clone; removed the private generator answer key from reachable Git history; and fixed Streamlit Cloud startup so the ignored analytical database is built and validated automatically from committed raw CSVs. The final automated suite passes 38 tests and 24 subtests.
- Files: `README.md`, `docs/management_brief.md`, `docs/architecture.md`, `docs/screenshots/architecture.png`, `docs/test_log.md`, `docs/ai_mistakes.md`, `scripts/render_architecture.py`, `app.py`, `src/database/bootstrap.py`, `tests/test_database_bootstrap.py`, `requirements.txt`.
- Commits: `e273ab5 Complete architecture and verification documentation`; `940f792 Update documentation after history sanitization`; `0d3d210 Build analytics database on hosted startup`.
- Next: Verify the live deployment after its first database build, capture final desktop and mobile screenshots, record the demonstration, and complete the submission document.

### Day 4 - 2026-10-04 - Resilient AI Model Failover

- Done: Added bounded retry and lighter-model failover for Gemini `429`, `5xx`, and timeout failures; routed missing credentials, exhausted models, and rejected generated SQL through reviewed offline queries; generated concrete grounded answers for revenue trend, best branch, aged inventory, and complaints; replaced stateful suggestion controls with reliable buttons that run reviewed queries without waiting for Gemini; prevented raw provider errors and `FACTS` labels from reaching users; preserved typed-question AI handling; produced an evidence-backed Management Brief; completed the Mermaid architecture and PNG export; audited secrets, dependencies, SQL totals, and private-file history; and fixed Streamlit Cloud startup by automatically building and validating the ignored DuckDB database from committed raw CSVs.
- Files: `app.py`, `src/database/bootstrap.py`, `tests/test_database_bootstrap.py`, `src/ai/gemini_client.py`, `src/ai/fallback.py`, `src/ai/guardrails.py`, `pages/ask_the_business.py`, `.env.example`, `docs/architecture.md`, `docs/screenshots/architecture.png`, `scripts/render_architecture.py`, `docs/management_brief.md`, `docs/test_log.md`, `docs/ai_mistakes.md`, `requirements.txt`, `README.md`.
- Commits: `679a6d2 Make business question buttons deterministic`; `91a4d59 Add evidence-backed management brief`; `e273ab5 Complete architecture and verification documentation`.
- Next: Add drill-downs and normalized monitoring for the three priorities in the Management Brief.

### Day 3 - 2026-10-03 - Governed AI, Data Quality & Management Reporting

- Done: Completed the Data Quality and Management Brief pages; secured Ask the Business with read-only SQL allowlists and numerical evidence checks; upgraded the configurable model to Gemini 3.8 Flash; added retries for transient API failures and deterministic no-Gemini fallbacks; removed SQL code from the user-facing evidence view; and added genuine PDF downloads for briefs, claims, and quality reports.
- Files: `pages/ask_the_business.py`, `pages/management_brief.py`, `pages/data_quality.py`, `src/ai/guardrails.py`, `src/ai/gemini_client.py`, `src/ai/fallback.py`, `src/ai/brief.py`, `src/database/connection.py`, `src/ui/pdf_exports.py`, `tests/test_ai_fallback.py`, `docs/day3_audit.md`, `docs/test_log.md`, `requirements.txt`, `.env.example`.
- Commits: `133e09e fix guardrails integration - complete Step 3`; `e522efa Add management brief`; `0c21203 Add data quality page`; `b614136 Add resilient AI reporting and Day 3 documentation`.
- Next: Consolidate remaining AI-page metrics in `src/analytics/metrics.py`, complete the deterministic insights registry, and broaden drill-down coverage.

### Day 2 - 2026-10-02 - README, Analytics, Overview & Drill-Down

- Done: Rebuilt the README to satisfy the required 14-section structure; built the audited cleaning and DuckDB pipeline, tested core metrics, persistent business filters, period-over-period management KPIs, responsive Overview charts, and warranty drill-down from model to branch to downloadable claims; corrected orphan and branch mapping issues, and added an explicit orphan-model guard in shared dimension enrichment so invalid relationships do not become management categories.
- Files: `README.md`, `src/data/cleaning.py`, `scripts/build_database.py`, `src/analytics/metrics.py`, `src/analytics/drilldown.py`, `src/ui/filters.py`, `pages/overview.py`, `pages/investigate.py`, `tests/`, `docs/cleaning_log.csv`, `docs/ai_mistakes.md`.
- Commits: `53ce936 Update README for submission requirements`; `6d7a108 Add drill-down investigation`; `93e6e9b Complete Day 2 analytics and dashboard`.
- Next: Build the Data Quality page, then ground Ask the Business and Management Brief in tested database evidence.

### Day 1 - 2026-09-30 - Streamlit App Skeleton

- Done: Generated and profiled the synthetic automotive dataset, documented its structure and assumptions, and launched a Streamlit shell on `localhost:8501` with Overview, Investigate, Ask the Business, Management Brief, and Data Quality pages.
- Files: `app.py`, `pages/`, `data/raw/`, `docs/data_dictionary.md`, `docs/assumptions.md`, `scripts/generate_dataset.py`, `scripts/profile_raw_data.py`, `.env.example`, `.gitignore`, `requirements.txt`.
- Commit: `23fcbcb Create Streamlit app skeleton`
- Next: Confirm cleaning rules and build the auditable DuckDB data pipeline.
