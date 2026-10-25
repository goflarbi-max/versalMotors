# Project Name

**versalMotors — Automotive Business Intelligence System**

## Business Problem

versalMotors has sales, inventory, service, warranty, complaint, and customer-satisfaction data spread across separate operational records. Management needs a reliable way to monitor performance, investigate problems, understand customer outcomes, and identify data-quality risks without manually reconciling those sources.

## Solution

This project provides a multipage business-intelligence application that turns operational records into auditable management metrics. A responsive public landing page introduces the evidence-led system before sign-in, while authenticated users enter directly through the management Overview. The implementation includes deterministic data generation, documented profiling, an explainable cleaning pipeline, a DuckDB analytical database, tested metrics, warranty-cost drill-down, responsive sortable and paginated evidence tables, data-quality monitoring, evidence-backed business questions, and downloadable management briefs.

### Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

The database and cleaned CSVs are generated artifacts. On a fresh clone or Streamlit Cloud deployment, `app.py` automatically builds and validates them from the committed raw CSVs before opening the pages. You can still run `.\.venv\Scripts\python.exe scripts\build_database.py` explicitly when rebuilding data during development. Google Gemini is optional; copy `.env.example` to `.env` only when AI narration is wanted.

### Authentication

VersalMotors uses a small app-level login for this project demo. It is an access gate for the demonstration, not a replacement for managed identity, MFA or enterprise single sign-on. The public landing and `/login` are anonymous; Next.js and FastAPI independently enforce every protected page and API route. Passwords are checked with cost-12 bcrypt, including a dummy-hash check for unknown accounts, and the browser receives only an opaque, HttpOnly, Secure, SameSite=Lax session cookie. Sessions have a 30-minute idle timeout and an eight-hour absolute lifetime, and logout revokes the server-side session.

Login, logout and other POST requests require an allowed Origin and a matching CSRF cookie/header. Within a 15-minute window, five failures lock an email and 25 failures lock an IP; the separate thresholds prevent one account from immediately denying access to unrelated users behind a shared address. Production should set `VERSALMOTORS_LOGIN_LOCK_SECONDS=900`; the limiter and session store are in memory on the current single-process Render service, so restarts clear them and horizontal scaling requires a shared store such as Redis. Authentication responses are not cached, CORS is restricted, and both frontend and API send CSP, HSTS, frame-denial, MIME-sniffing, referrer and permissions headers.

The public landing page has one fixed black-and-light presentation, independent of browser theme, with accessible reduced-motion support for its subtle entrance effects. The login screen always uses the light theme; signing out resets the next login to light. After signing in, users enter Overview and can switch protected pages between the existing light and dark themes.

Public demo access:

- Email: `demo@versalmotors.com`
- Password: `VersalDemo2026!`

Generate the corresponding hash locally without placing the password in shell history:

```powershell
.\.venv\Scripts\python.exe scripts\create_user.py
```

For local development, place the generated hash and role in `.env`:

```dotenv
VERSALMOTORS_AUTH_USERS_JSON='{"demo@versalmotors.com":{"password_hash":"<bcrypt-hash>","role":"viewer"}}'
```

For Streamlit Community Cloud, use this format in the app's Secrets settings:

```toml
[auth.users]
"demo@versalmotors.com" = "<bcrypt-hash>"
```

Roles are currently `viewer` or `admin`; they are exposed by `/api/auth/me` for future authorization work, but no role-specific screen exists yet. Only hashes are used for verification. The displayed demo password is intentionally public for this demonstration account. `.env`, `.env.*` and `.streamlit/secrets.toml` are excluded from Git.

### Testing

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The full suite records 65 passing tests and 24 passing subtests across public/protected routing, authentication, calculations, degraded schemas, bad chronology, filters, AI failures, unsupported questions, large data, all five protected Streamlit pages, and the shared table renderer. Full stress-test results and limitations are in `docs/test_log.md`.

## Dataset

The repository contains nine synthetic raw CSV tables covering branches, models, salespeople, inventory, sales, service records, warranty claims, complaints, and satisfaction. The data spans approximately 2.5 years, uses Ghanaian cedi (`GHS`), and deliberately contains realistic quality problems for testing. Raw CSVs are committed so a fresh clone can rebuild the application without access to private files. Cleaned outputs are generated locally in `data/cleaned/` and loaded into `data/business.duckdb`; both are excluded from Git. `docs/data_dictionary.md` records the observed schema and profile.

### Assets

The `assets/` folder contains the theme-aware VersalMotors logos and preserved earlier landing artwork. The public landing uses the existing white logo; its lightweight dotted wave is rendered with scoped CSS, so it requires no new image asset.

## How the System Works

1. `scripts/generate_dataset.py` creates deterministic synthetic raw CSVs.
2. `scripts/profile_raw_data.py` profiles columns, duplicates, suspicious values, and relationships.
3. `src/data/cleaning.py` standardises reviewed values, safely parses fields, flags questionable records, removes only exact duplicates, and writes an audit log.
4. `scripts/build_database.py` rebuilds the cleaned CSVs and local DuckDB database.
5. `src/analytics/metrics.py` calculates tested business metrics without UI or database side effects.
6. Signed-out sessions can view the public landing or login page; direct protected URLs choose Login. Successful authentication opens Overview without disturbing shared filter state.
7. Streamlit presents persistent filters, management KPIs, period comparisons, charts, responsive sortable and paginated tables, warranty drill-down evidence, data-quality checks, and PDF exports. Theme-aware logo assets are stored in `assets/`.
8. Ask the Business uses reviewed read-only queries and deterministic evidence summaries only; it never sends a question or business record to Gemini. Optional Gemini narration remains limited to the Management Brief and legacy Streamlit workflow.

## Architecture

```text
Business Data -> Data Processing -> Database -> Analysis -> Evidence -> AI & Guardrails -> Dashboard -> Management
Raw CSVs      -> Audited Cleaning -> DuckDB   -> Metrics  -> Objects  -> Optional Gemini  -> Streamlit -> Decisions
```

Ask the Business is data-only: reviewed queries run against the uploaded DuckDB tables and return deterministic answers with evidence. Optional AI narration is separate and is never required to ask about the business. See `docs/architecture.md` for the Mermaid diagrams and exported PNG.

The Phase 7 migration preview packages the read-only FastAPI service in a verified non-root Docker image and serves the Next.js interface through Vercel with a same-origin `/api/*` proxy. Railway hosts the preview API; the Streamlit deployment remains the production rollback target until the separately approved cutover phase. See `docs/deployment.md`.

## Technologies (What + Why)

- **Python and pandas:** generate, clean, test, and analyse the dataset reproducibly.
- **Streamlit:** provides responsive multipage navigation, persistent filters, KPI cards, charts, and drill-down evidence.
- **Navigation:** protected pages use Streamlit's native responsive sidebar with a clear hamburger/close control, preserving filters, direct URLs, and mobile drawer behaviour.
- **Fonts:** one shared typography module applies self-hosted Inter Latin WOFF2 assets to Streamlit, custom HTML, tables, and Plotly; system sans-serif fonts remain the non-blocking fallback.
- **bcrypt:** verifies demo-account passwords using salted adaptive hashes instead of stored plaintext credentials.
- **CSV:** keeps raw and cleaned pipeline stages portable and auditable.
- **DuckDB:** stores the local analytical model and supports independent SQL verification of important calculations.
- **pytest:** checks cleaning contracts, formulas, filter safety, SQL parity, and drill-down reconciliation.
- **Google Gen AI SDK:** provides optional evidence-grounded questions and management narratives using the configurable `gemini-3.8-flash` model.
- **fpdf2:** creates genuine downloadable PDF management briefs and operational reports.
- **Git and GitHub:** provide version control, traceability, and project history.
- **FastAPI, Docker, Railway, Next.js and Vercel:** provide the parallel, parity-tested deployment path while the current Streamlit application remains available for rollback.

## AI Usage

AI has assisted development by drafting code, documentation, dataset patterns, tests, and quality checks. Ask the Business does not use an external AI service: supported intents map to reviewed read-only DuckDB queries, and every response is produced deterministically from returned evidence. Questions outside that reviewed registry are declined rather than converted into generated SQL. Optional Gemini narration remains available only in the Management Brief and legacy Streamlit path; it does not calculate source metrics, make business decisions, silently repair ambiguous records, or replace database evidence.

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
- Keeping transparent brand artwork readable across Streamlit light and dark modes, including first renders where server-side theme context is unavailable.
- Protecting direct multipage URLs without adding authentication code to every business page, while preserving existing headless page tests and shared filter state.
- Replacing inconsistent native data grids with one safe table renderer while preserving DataFrame values, download payloads, stable numeric/date/text sorting, null ordering, pagination state, and mobile overflow behaviour.
- Keeping the protected navigation and complete dark palette stable across Streamlit reruns; an authenticated root-route check initially replaced the Overview shell after a theme switch and required browser-level DOM diagnosis.

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

### Day 12 - 2026-10-23 - Navigation, Typography & Theme Regression Fixes

- Done: Added self-hosted Inter typography, a responsive native-sidebar hamburger/X treatment, accessible mobile drawer behaviour, persistent light/dark page and chart palettes, and regression coverage for shared theme state. Diagnosed the Overview-only theme failure in a real browser and corrected authenticated root routing so a theme-switch rerun remains on Overview with navigation, filters, account controls, and the `#0F172A` dark background intact. Corrected dark-mode CSV/PDF download controls so their labels, icons, hover state, and keyboard focus remain clearly visible. Standardized main-content primary actions to black with white text in light mode and the inverse in dark mode without altering secondary or branded controls. The full suite passes 74 tests and 24 subtests.
- Files: `.streamlit/config.toml`, `app.py`, `src/ui/theme.py`, `src/ui/sidebar.py`, `src/ui/charts.py`, `static/fonts/`, `tests/test_ui_theme_sidebar_regression.py`, `tests/test_ui_typography.py`, `docs/regression_diagnosis.md`, `docs/ai_mistakes.md`, `docs/architecture.md`, `README.md`.
- Next: Verify the refreshed navigation and theme switch on the hosted custom domain after deployment.

### Day 11 - 2026-10-21 - Public Landing Visual Polish

- Done: Refined the public landing with a black hero, five compact analytics icons, a responsive one-time staggered entrance sequence, a subtle desktop-only dot-wave drift, reduced-motion support, and clean card hover feedback. Made the landing page the guaranteed custom-domain root even when a hosting proxy omits URL context, while preserving protected-page redirects, the white logo, evidence cards, and all business logic. Browser checks passed at 375px, 768px, and 1280px with no horizontal overflow; the full suite passes 65 tests and 24 subtests.
- Files: `src/ui/landing.py`, `src/ui/theme.py`, `README.md`.
- Next: Verify the updated landing experience after the hosted Streamlit deployment refreshes.

### Day 10 - 2026-10-20 - Public Landing & Protected Routing

- Done: Replaced the authenticated Home screen with a database-independent public landing page featuring the white VersalMotors logo, fixed navy hero, lightweight inline-SVG dotted wave, evidence-focused feature cards, and one Sign in action. Anonymous protected URLs now select Login, successful sign-in opens Overview, and the Home item was removed from the protected sidebar without changing business-page logic. The full suite passes 65 tests and 24 subtests.
- Files: `app.py`, `pages/landing.py`, `pages/login.py`, `src/ui/landing.py`, `src/ui/theme.py`, `tests/test_public_routing.py`, `README.md`, `docs/architecture.md`.
- Next: Verify the public-to-login journey and responsive presentation on the hosted deployment.

### Day 9 - 2026-10-19 - Light-Only Login & UI Card Polish

- Done: Made the login screen permanently light regardless of native, browser, or operating-system theme; removed login theme switching; reset the UI theme to light on sign-out; preserved protected-page dark mode; and verified responsive login rendering at 375px, 768px, and 1280px. Restyled the Sign In control with a scoped black-and-white charcoal treatment, accessible focus state, responsive sizing, and no arrow icon; reinforced the selector against hosted Streamlit markup changes so the old primary-button styling cannot return. Also completed the pending themed summary-card presentation for Ask the Business and Data Quality. The full suite passes 57 tests and 24 subtests.
- Files: `.streamlit/config.toml`, `app.py`, `pages/ask_the_business.py`, `pages/data_quality.py`, `src/ui/auth_ui.py`, `src/ui/components.py`, `src/ui/sidebar.py`, `src/ui/theme.py`, `tests/test_auth.py`, `README.md`.
- Next: Verify the light-only login and refreshed cards on the hosted deployment.

### Day 8 - 2026-10-18 - Responsive Application Tables

- Done: Replaced application data grids with one reusable, theme-aware table renderer across Investigate, Ask the Business, Management Brief, and Data Quality. Added stable three-state sorting, nulls-last ordering, 10/25/50-row pagination, responsive internal scrolling, safe HTML escaping, empty-result handling, and per-table session state without mutating source DataFrames or download data. Resolved a stale local Streamlit process that initially continued serving the pre-change module. The full suite passes 55 tests and 24 subtests.
- Files: `src/ui/components.py`, `src/ui/theme.py`, `pages/investigate.py`, `pages/ask_the_business.py`, `pages/management_brief.py`, `pages/data_quality.py`, `tests/test_table_ui.py`, `README.md`.
- Next: Verify the table experience on the hosted deployment at desktop and mobile widths.

### Day 7 - 2026-10-15 - Demo Authentication & Access Control

- Done: Added a responsive bcrypt-backed login screen, conditional page registration that protects direct URLs, consistent credential errors, five-attempt session lockout, a safe password-hash generator, landing-page account controls, business-page sidebar sign-out, local and Streamlit Secrets documentation, and authentication architecture. The full suite passes 48 tests and 24 subtests.
- Files: `app.py`, `src/auth/auth.py`, `src/auth/__init__.py`, `src/ui/auth_ui.py`, `src/ui/theme.py`, `scripts/create_user.py`, `tests/test_auth.py`, `requirements.txt`, `.env.example`, `README.md`, `docs/architecture.md`.
- Next: Add the generated demo bcrypt hash to Streamlit Secrets and verify sign-in and lockout on the hosted application.

### Day 6 - 2026-10-14 - Landing Page & Theme-Aware Branding

- Done: Added a responsive, database-independent landing page; created transparent dark and light logo assets; made logo rendering adapt reliably to Streamlit light and dark modes; added Home navigation back to the landing page while keeping its sidebar hidden; retained the full sidebar and shared filters on business pages; and removed landing-page footer clutter and heading permalink icons across the application. The automated suite passes 38 tests and 24 subtests.
- Files: `app.py`, `pages/landing.py`, `src/ui/components.py`, `src/ui/theme.py`, `assets/logo_original.jpg`, `assets/logo_dark.png`, `assets/logo_light.png`, `README.md`.
- Commit: `Add responsive landing page and theme-aware branding`.
- Next: Capture final hosted screenshots in both themes and confirm the production deployment reflects the new landing experience.

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
