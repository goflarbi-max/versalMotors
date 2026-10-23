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
