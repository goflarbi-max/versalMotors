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

## Theme toggle and hamburger regression - Oct 22 2026

- **Situation:** I coupled the custom dark-mode toggle to Streamlit's private `stActiveTheme-*` browser storage and styled an obsolete sidebar-toggle selector. A theme click could remount the frontend, collapse the sidebar, and leave only some custom cards dark, while the native double-chevron remained visible instead of the hamburger.
- **How discovered:** The user reported both regressions. The follow-up investigation in `docs/regression_diagnosis.md` traced the split theme state and inspected the installed Streamlit frontend to identify its actual `stExpandSidebarButton` and `stSidebarCollapseButton` controls.
- **How corrected:** I made `sidebar_dark_mode` the protected app's single theme source, removed the private browser-theme bridge, applied one shared runtime palette before protected-page rendering, and targeted the installed Streamlit controls while retaining their native behavior and accessible labels. Regression tests now cover palette selection, one-rerun toggling, login's fixed light theme, preservation of sidebar state, and the installed frontend selectors.
# Phase 0 diagnostic SQL alias error — 2026-10-23

- **What went wrong:** During read-only inspection for the migration parity baseline, I used `name` as an unquoted SQL alias in a diagnostic salesperson query. DuckDB rejected the query as a parser error.
- **How it was discovered:** The diagnostic command failed immediately before any files or database rows were changed.
- **How it was corrected:** I changed the alias to the explicit, non-reserved `salesperson_name`, reran the query successfully, and kept all baseline access read-only.

# Phase 0 Management Brief export assumption — 2026-10-23

- **What went wrong:** I initially assumed the current Management Brief Markdown export could be executed while capturing parity. The export uses `DataFrame.to_markdown()`, but the current environment and `requirements.txt` do not include its optional `tabulate` dependency.
- **How it was discovered:** The first baseline capture failed with `ModuleNotFoundError: No module named 'tabulate'` before writing the baseline file.
- **How it was corrected:** I did not change dependencies or application behavior in the baseline phase. The capture now records Markdown and PDF export as unavailable with the exact error type and reason, so the migration cannot silently claim that the current export works.

# Phase 0 direct-SQL dimension ambiguity — 2026-10-23

- **What went wrong:** The first parity verifier joined branch/model dimension aliases to test the same exact-filter fields as the metrics layer, but selected `branch_name` and `model_name` without qualifying which relation supplied them.
- **How it was discovered:** The new direct-SQL parity test failed with a DuckDB `BinderException` before comparing any values.
- **How it was corrected:** I qualified displayed branch/model fields with the verified one-row-per-sale base alias and reran the parity test. No metric formula or source data was changed.

# Phase 0 DuckDB test-connection leak — 2026-10-23

- **What went wrong:** The baseline helper called the existing Management Brief KPI function, which opens a thread-local read-only DuckDB connection. I initially left that connection open after capture, so a later existing test could not open the same database read-write to create its temporary compatibility view.
- **How it was discovered:** The full pytest suite failed in the existing metrics SQL-parity test with “different configuration than existing connections,” while the new focused tests had passed.
- **How it was corrected:** The Phase 0 helper now closes only the thread-local connection it invokes immediately after Management Brief capture. The database and application connection code remain unchanged.
