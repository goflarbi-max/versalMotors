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
# Phase 1 backend parity harness corrections (2026-10-23)

## Login attempts were cleared before reaching lockout

- **What went wrong:** The first implementation of the backend login limiter removed an entry whenever `locked_until <= now`. Pre-lock entries use `locked_until = 0`, so each status check erased the accumulated failure count and the fifth failure never produced the required 60-second lockout.
- **How it was discovered:** The focused backend security test expected HTTP 429 on the fifth failed login and received HTTP 401.
- **How it was corrected:** Expiry cleanup now runs only when a positive lock timestamp exists. Pre-lock failures remain accumulated, the fifth failure locks for 60 seconds, and successful authentication still clears the entry.

## Immutable baseline provenance was compared with the moving Git HEAD

- **What went wrong:** The Phase 0 snapshot test compared `metadata.source_git_commit` with the current HEAD. That value correctly records the pre-migration source commit, so it necessarily differs after the Phase 0 commit and every later phase even when all data and business outputs are unchanged.
- **How it was discovered:** The Phase 1 focused suite failed only at `metadata.source_git_commit`; every stored business output and direct-SQL comparison remained equal.
- **How it was corrected:** The parity test now treats the recorded commit as immutable provenance and excludes only that moving repository-state comparison. Database hashes, raw-file hashes, row counts, all returned records, display values, and direct-SQL checks remain enforced.
# Phase 2 frontend shell corrections (2026-10-23)

## Duplicate accessible labels made the mobile close-control test ambiguous

- **What went wrong:** The first mobile shell gave both the hamburger/X control and the dimmed backdrop the accessible name "Close navigation menu." Both controls worked, but assistive-technology and Playwright queries could not identify the intended control uniquely.
- **How it was discovered:** The first Playwright mobile-drawer run failed strict locator resolution because two buttons had the same role and name.
- **How it was corrected:** The X retains "Close navigation menu" and the backdrop now uses the distinct, accurate name "Dismiss navigation menu." The behavior and visual design are unchanged.

## Public client navigation was unreliable during the first development-server test

- **What went wrong:** The first port used Next.js client navigation for the public Sign in link. During the initial development-server browser run, the React Server Component destination stream errored and the URL stayed on the landing page.
- **How it was discovered:** Two Playwright public-flow tests timed out despite the rendered link having the correct destination.
- **How it was corrected:** The public authentication boundary now uses a normal same-origin anchor, producing a reliable full navigation. The server still selects `/login` for signed-out users and `/overview` for authenticated users.

## Phase 3 filter-option test assumed title-case status values

- **What went wrong:** I initially asserted that the filter-options endpoint would contain `Completed`, although the cleaned sales table and existing Streamlit filter expose the exact lowercase value `completed`.
- **How it was found:** The new backend filter-options test failed while comparing the endpoint response with the current application choices.
- **How it was fixed:** I corrected only the test expectation to the source-of-truth lowercase value. The adapter, data, filters, and metric formulas were left unchanged.

## Phase 3 first frontend build exposed two implementation errors

- **What went wrong:** The first Overview build mixed `||` with `??` without parentheses in date-input props, and the initial data effect synchronously reset React state in a pattern rejected by the configured React hooks lint rule.
- **How it was found:** `npm run lint` and the Next.js production build failed before any commit was created.
- **How it was fixed:** I made the nullish-coalescing precedence explicit and modeled request status by the query attached to each asynchronous result, so a changed URL naturally shows the loading state without a synchronous state reset inside the effect.

## Phase 3 Overview requests aborted themselves and default filters raced navigation

- **What went wrong:** The first browser implementation made the Overview request effect depend on a reconstructed filter object, so renders could abort and restart the KPI request. Default dates were also canonicalized with a router navigation that could win a race against a user immediately selecting another page.
- **How it was found:** Playwright showed the three chart requests completing while the KPI card never appeared, and a tablet navigation click returned to Overview.
- **How it was fixed:** The request effect now depends only on the stable serialized query string. Default dates use the browser history replacement supported by Next.js, updating the shareable URL without starting a competing route navigation.

## Phase 3 error-state test selected Next.js's route announcer

- **What went wrong:** The first error-state assertion selected every element with the ARIA `alert` role, which included both the intended Overview error card and Next.js's built-in route announcer.
- **How it was found:** Playwright strict mode rejected the ambiguous locator even though the friendly Overview error message was rendered correctly.
- **How it was fixed:** The test now targets the scoped `.overview-state[role=alert]` component, preserving the accessibility role while avoiding framework-owned elements.

## Phase 4 investigation route parameters collided with global filters

- **What went wrong:** I initially named the FastAPI drill-down path variables `model` and `branch`. Those names already belong to the shared global-filter dependency, so FastAPI treated the dependency parameters as path parameters and rejected application startup.
- **How it was found:** The first focused backend test failed while importing the application, before any endpoint or data mutation ran.
- **How it was fixed:** I renamed only the Python path variables to `selected_model` and `selected_branch`. The public endpoint shape, global filters, existing analytics functions, and returned values remain unchanged.

## Phase 4 integer Literal did not accept HTTP query strings

- **What went wrong:** I modeled `page_size` as `Literal[10, 25, 50]`. With the installed FastAPI/Pydantic versions, query-string values such as `page_size=50` were not coerced to those integer literals and returned HTTP 422.
- **How it was found:** The new API parity and export tests failed for every request that explicitly supplied a page size.
- **How it was fixed:** The route now parses `page_size` as an integer and applies an explicit allowlist of 10, 25, or 50 before calling the paging adapter. Invalid values still return HTTP 422, while valid URL query strings work as designed.

## Phase 4 breadcrumb made an older browser locator ambiguous

- **What went wrong:** The new Investigate breadcrumb and the existing sidebar both expose a legitimate link named “Overview.” An older browser test used an unscoped role/name locator and therefore matched both links.
- **How it was found:** The full Playwright regression run passed 20 tests and failed only the shared-filter navigation test with a strict-locator ambiguity.
- **How it was fixed:** I scoped the existing assertion to the `Primary navigation` complementary landmark. The breadcrumb, sidebar links, accessible names, filters, and routing behavior remain unchanged.
## Phase 5 browser verification used a stale preview server (2026-10-24)

- **What went wrong:** The first Ask and Management Brief Playwright run reused an older Next.js process on port 3000, so it tested migration placeholders instead of the current production build. Two assertions also targeted wording and the transparent `body` rather than the existing `.app-shell` theme surface.
- **How it was found:** The Playwright accessibility snapshot showed the exact old placeholder copy despite the current source and successful Next.js build.
- **How it was fixed:** The stale test-port processes were identified by command line and restarted, deterministic AI-disabled browser-test environment variables were added, and assertions were aligned with the actual safe-refusal copy and app-shell theme surface. The responsive brief controls were tightened at tablet width after the browser test exposed a 20-pixel overflow.
