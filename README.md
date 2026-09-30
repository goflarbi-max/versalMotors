# Project Name

**versalMotors — Automotive Business Intelligence System**

## Business Problem

versalMotors has sales, inventory, service, warranty, complaint, and customer-satisfaction data spread across separate operational records. Management needs a reliable way to monitor performance, investigate problems, understand customer outcomes, and identify data-quality risks without manually reconciling those sources.

## Solution

This project is building a multipage business-intelligence application that will combine those operational areas into decision-ready reporting. The current implementation provides a realistic synthetic dataset, a documented data profile, and a working five-page Streamlit navigation shell; database-backed analytics are not implemented yet.

## Dataset

The repository contains nine synthetic raw CSV tables covering branches, models, salespeople, inventory, sales, service records, warranty claims, complaints, and satisfaction. The data spans approximately 2.5 years, uses Ghanaian cedi (`GHS`), and deliberately contains realistic quality problems for testing. `docs/data_dictionary.md` records the observed schema and profile.

## How the System Works

1. `scripts/generate_dataset.py` creates deterministic synthetic raw CSVs.
2. `scripts/profile_raw_data.py` profiles columns, duplicates, suspicious values, and relationships.
3. The planned cleaning layer will validate and load curated data into DuckDB.
4. `app.py` currently routes users to five placeholder Streamlit pages: Overview, Investigate, Ask the Business, Management Brief, and Data Quality.

## Architecture

```text
Business Data -> Data Processing -> Database -> Analysis -> AI Layer -> Dashboard -> Management
Raw CSVs      -> Planned Cleaning -> DuckDB   -> Planned  -> Planned  -> Streamlit -> Decisions
```

Only raw-data generation, profiling, documentation, and the Streamlit application shell currently exist.

## Technologies (What + Why)

- **Python:** generates and profiles the dataset with reproducible scripts.
- **Streamlit:** provides simple multipage navigation for the business-facing application.
- **CSV:** keeps the synthetic source data portable and easy to inspect.
- **Git and GitHub:** provide version control, traceability, and project history.
- **DuckDB (planned):** will provide a local analytical database suitable for joining and aggregating the CSV-scale dataset.

## AI Usage

AI has assisted development by drafting code, documentation, dataset patterns, and quality checks. The planned AI layer may help users ask business questions and prepare management summaries, but no runtime AI feature exists yet. AI does not currently clean data automatically, make business decisions, or replace validation against source records and approved business rules.

## Data Quality

The raw data intentionally includes missing values, duplicates, name and category variants, invalid dates, negative amounts, malformed VINs, arithmetic inconsistencies, and orphan references. `docs/data_dictionary.md` documents observed issues, while `docs/assumptions.md` lists unresolved cleaning decisions as questions. Raw files remain unchanged; a curated cleaning pipeline and quality dashboard are still planned.

## Challenges

- Defining safe cleaning rules without inventing answers for ambiguous business fields.
- Separating exact duplicates from legitimate repeated transactions and near-duplicates.
- Preserving referential integrity across nine related tables with deliberately orphaned keys.
- Keeping the private generator answer key out of the public repository while retaining it locally for verification.

## AI Mistakes

- **Situation:** An AI-assisted `git add .` included the private generator answer key in an early public commit.
- **How discovered:** The committed-file list showed `data/generator_truth.md` among the published files.
- **How corrected:** The file was added to `.gitignore`, removed from current Git tracking, and retained locally. It still exists in earlier Git history, so a history rewrite would be required for complete removal.

## What You Learned

- Profile raw data before designing dashboards or committing to cleaning rules.
- Keep observed facts separate from business assumptions and request clarification when meaning is uncertain.
- Treat generated answer keys, secrets, local databases, and caches as private artifacts from the start.
- Build navigation and data foundations before investing in presentation details.

## Future Improvements

- Resolve the open business-rule questions in `docs/assumptions.md`.
- Build an auditable raw-to-clean pipeline and DuckDB analytical model.
- Add automated data-quality and relationship tests.
- Implement KPIs, filters, charts, investigation workflows, and management reporting.
- Add a validated business-question interface and clearly governed AI summaries.

## Daily Progress Log

### Day 1 - 2026-09-30 - Streamlit App Skeleton

- Done: Generated and profiled the synthetic automotive dataset, documented its structure and assumptions, and launched a Streamlit shell on `localhost:8501` with Overview, Investigate, Ask the Business, Management Brief, and Data Quality pages.
- Files: `app.py`, `pages/`, `data/raw/`, `docs/data_dictionary.md`, `docs/assumptions.md`, `scripts/generate_dataset.py`, `scripts/profile_raw_data.py`, `.env.example`, `.gitignore`, `requirements.txt`.
- Commit: `cca4a75 Create Streamlit app skeleton`
- Next: Confirm cleaning rules and build the auditable DuckDB data pipeline.
