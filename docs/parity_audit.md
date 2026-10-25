# VersalMotors Streamlit-to-Next.js parity audit

Audit date: 2026-10-25

## Scope and method

The reference is the root Streamlit application (`app.py`, `pages/`, `src/ui/`). The migrated application is the Next.js frontend in `frontend/` backed by FastAPI in `backend/`. The requested `.agent/rules/project-rules.md` path does not exist; the repository's tracked rules were read from `docs/.agent/rules/project-rules.md`, which is also the path documented in the migration plan.

The audit used:

- source inspection of every visible Streamlit page and shared UI component;
- source inspection of every migrated route and shared React component;
- direct-function versus FastAPI comparisons across ten filter scenarios;
- a Playwright comparison harness in `frontend/playwright/parity-compare.spec.ts`;
- tolerance-aware image diffs from `tests/visual/image_diff.py`;
- generated evidence under `docs/screenshots/parity/`.

The intended differences were excluded: no Streamlit branding, no “Made with Streamlit” tag, no iframe border, and no Streamlit rerun flash.

## Executive result

All approved **High** and **Medium** migrated-app findings are resolved. Numerical parity remains exact: **zero mismatches** were found across ten filter combinations for KPI records, revenue-trend records and totals, branch-chart records and totals, model-margin records and totals, warranty drill-down row counts/totals, and the four Ask the Business summary cards.

The completed fixes restore the Overview evidence action and chart presentation, scope shared filters to the same pages as the reference, replace placeholder KPI glyphs, match the Investigate selection workflow, restore Ask/History and inline evidence presentation, align Management Brief and Data Quality presentation, and match the reference table pagination and landing geometry. The deterministic data-only Ask architecture remains intact; unavailable/unverified notices are conditional rather than fabricated.

The only High item not changed is the documented **reference Streamlit mobile-sidebar regression**. It is not a defect in the migrated app, and changing the reference was outside the approved scope. The Next.js drawer closes atomically after mobile navigation and is covered by Playwright.

## Feature inventory

Status meanings: **Matches** = same visible function and behavior; **Different** = present but behavior or presentation differs; **Missing** = absent in the migrated app; **Broken** = present but not reliably usable.

| Area | Reference feature / behavior | New app status | Reference file | New app file | Note |
|---|---|---:|---|---|---|
| Landing | Black hero, white logo, headline, analytics copy | Matches | `src/ui/landing.py` | `frontend/app/page.tsx` | Same content hierarchy and fixed black presentation. |
| Landing | Five white analytics icon tiles | Matches | `src/ui/landing.py` | `frontend/app/page.tsx` | Inline decorative SVGs are present. |
| Landing | White dot-wave graphic | Matches | `src/ui/landing.py` | `frontend/app/page.tsx` | Equivalent decorative treatment. |
| Landing | Three overlapping bottom cards | Matches | `src/ui/landing.py` | `frontend/app/page.tsx` | Same three concepts and order. |
| Landing | Staggered load animation, reduced-motion support | Matches | `src/ui/landing.py` | `frontend/app/globals.css` | Native CSS rather than Streamlit HTML injection. |
| Landing | Sign in routes unauthenticated users to Login and authenticated users to Overview | Matches | `pages/landing.py` | `frontend/app/page.tsx` | Route outcome is equivalent. |
| Login | Light-only glass card, dark logo, email/password fields | Matches | `src/ui/auth_ui.py` | `frontend/app/login/page.tsx` | Minor spacing differences are listed below. |
| Login | Show/hide password | Matches | `src/ui/auth_ui.py` | `frontend/app/login/page.tsx` | Present in both. |
| Login | Forgot Password administrator message | Matches | `src/ui/auth_ui.py` | `frontend/app/login/page.tsx` | Streamlit uses a dialog; Next.js uses inline disclosure. Presentation differs. |
| Login | Five failures then 60-second lockout | Matches | `src/auth/auth.py` | `backend/app/core/security.py`, auth routes | Same threshold and duration. |
| Login | Same error for unknown email and wrong password | Matches | `src/auth/auth.py` | backend auth routes | Preserved. |
| Login | Demo access note | Missing in both current UIs | `src/ui/auth_ui.py` | `frontend/app/login/page.tsx` | The requested historical note is no longer visible in the current reference, so its absence is parity, not a migration defect. |
| Access | Direct protected routes redirect signed-out users | Matches | `app.py` | `frontend/middleware.ts` | Both protect all business pages. |
| Access | Sign out clears auth and returns to light login | Matches | `src/ui/sidebar.py` | `frontend/components/app-shell.tsx` | Equivalent user result. |
| Sidebar | Page order and active-page indication | Matches | `app.py`, `src/ui/sidebar.py` | `frontend/components/app-shell.tsx` | Overview, Investigate, Ask, Brief, Data Quality. |
| Sidebar | Signed-in email | Matches | `src/ui/sidebar.py` | `frontend/components/app-shell.tsx` | Present in both. |
| Sidebar | Theme switch persists between protected pages | Matches | `src/ui/sidebar.py`, `src/ui/theme.py` | `frontend/components/app-shell.tsx` | Different state implementation, same expected behavior. |
| Sidebar | Hamburger / drawer with backdrop | Broken in reference; Matches in Next.js | `src/ui/sidebar.py` | `frontend/components/app-shell.tsx` | Streamlit's mobile backdrop can remain active and intercept controls after navigation; Next.js closes cleanly. |
| Filters | Date, branch, brand, model, salesperson, status | Matches | `src/ui/filters.py` | `frontend/components/business-filter-panel.tsx` | Same dimensions and values. |
| Filters | Values persist across Overview and Investigate | Matches | `src/ui/filters.py` | URL-backed filter state | Verified structurally and by API parity scenarios. |
| Filters | Filters shown only where reference uses them | Matches | `pages/overview.py`, `pages/investigate.py` | `frontend/components/app-shell.tsx` | The filter panel is restricted to Overview and Investigate. |
| Overview | Revenue KPI and comparison | Matches | `pages/overview.py` | `frontend/components/overview-dashboard.tsx` | Same source result and caption. |
| Overview | Gross margin KPI and comparison | Matches | same | same | Same source result and caption. |
| Overview | Units sold KPI and comparison | Matches | same | same | Same source result and caption. |
| Overview | Discount rate KPI and comparison | Matches | same | same | Same source result and caption. |
| Overview | KPI material icons | Matches | `src/ui/components.py` | `frontend/components/overview-dashboard.tsx` | Semantic SVG icons replace the placeholder glyphs. |
| Overview | Revenue trend chart | Matches | `pages/overview.py`, `src/ui/charts.py` | `frontend/components/overview-charts.tsx` | Same data, height, axis titles, legend policy and full-value tooltip. |
| Overview | Revenue by branch chart | Matches | same | same | Same data, primary green series, axis titles and tooltip precision. |
| Overview | Gross margin by model chart | Matches | same | same | Same data, primary green series, height, labels and tooltip precision. |
| Overview | “Investigate the evidence” navigation card | Matches | `pages/overview.py` | `frontend/components/overview-dashboard.tsx` | Restored with the reference heading, caption and filter-preserving destination. |
| Overview | Empty-filter friendly state | Matches | `pages/overview.py` | `frontend/components/overview-dashboard.tsx` | Both avoid crashing and provide a reset/recovery path. |
| Investigate | Breadcrumbs: warranty cost → model → branch | Matches | `pages/investigate.py` | `frontend/components/investigate-dashboard.tsx` | Same hierarchy. |
| Investigate | Model-level warranty table | Matches | `pages/investigate.py` | `frontend/components/investigate-dashboard.tsx` | Data and totals match. |
| Investigate | Branch-level warranty table | Matches | same | same | Data and totals match. |
| Investigate | Claim-record table | Matches | same | same | Same records are available. |
| Investigate | Drill-down selection workflow | Matches | `pages/investigate.py` | `frontend/components/investigate-dashboard.tsx` | Uses the reference select-and-view workflow while retaining query-backed state. |
| Investigate | Sorting, paging and “Showing x to y of z entries” | Matches | `src/ui/components.py` | `frontend/components/data-table.tsx` | Both preserve source data and paginate display copies. |
| Investigate | Full filtered CSV download | Matches | `pages/investigate.py` | Investigate download route/component | Not limited to the visible page. |
| Investigate | PDF download | Matches | `pages/investigate.py` | backend export endpoint | Same deterministic exporter family. |
| Ask | Four summary cards | Matches | `pages/ask_the_business.py` | `frontend/components/ask-dashboard.tsx` | Values exactly match. |
| Ask | Four reviewed quick questions | Matches | `pages/ask_the_business.py` | backend ask suggestions + `ask-dashboard.tsx` | Same labels and reviewed questions. |
| Ask | Ask / History tabs | Matches | `pages/ask_the_business.py` | `frontend/components/ask-dashboard.tsx` | Both views are available with the same conversation state. |
| Ask | Clear chat | Matches | `pages/ask_the_business.py` | `frontend/components/ask-dashboard.tsx` | The control stays available and clears the current conversation. |
| Ask | Typed questions and Enter/submit | Matches | `pages/ask_the_business.py` | `frontend/components/ask-dashboard.tsx` | Input is capped at 500 characters in Next.js. |
| Ask | Facts / Interpretation / Recommendations | Matches | current Streamlit answer renderer | `frontend/components/ask-dashboard.tsx` | The user-facing answer hierarchy matches without adding a redundant FACTS heading. |
| Ask | Evidence display | Matches | `pages/ask_the_business.py` | `frontend/components/ask-dashboard.tsx` | Evidence is rendered inline with raw SQL hidden. |
| Ask | Evidence SQL hidden from users | Matches | `pages/ask_the_business.py` | `frontend/components/ask-dashboard.tsx` | Neither user UI displays raw SQL. |
| Ask | Unanswerable question message | Matches | ask page/tools | backend ask service | Both return a safe reviewed-scope response. |
| Ask | “Unverified” guardrail warning | Matches when applicable | `src/ai/guardrails.py`, ask page | `frontend/components/ask-dashboard.tsx` | Conditional presentation exists; deterministic results do not fabricate an unverified state. |
| Ask | AI outage fallback notice | Matches current data-only architecture | `pages/ask_the_business.py` | backend ask service | Deterministic fallback wording is safe and grounded without implying an unavailable AI call. |
| Management Brief | Date range and Generate action | Matches | `pages/management_brief.py` | `frontend/components/management-brief-dashboard.tsx` | Same business period semantics. |
| Management Brief | Executive Summary | Matches | same | same | Present. |
| Management Brief | Key Findings | Matches | same | same | Present. |
| Management Brief | Areas Requiring Attention | Matches | same | same | Present. |
| Management Brief | Opportunities | Matches | same | same | Present. |
| Management Brief | Recommended Actions | Matches | same | same | Present. |
| Management Brief | Questions for Management | Matches | same | same | Present. |
| Management Brief | Evidence IDs and supporting evidence details | Matches | same | same | Layout differs, content is represented. |
| Management Brief | Markdown export | Matches | same | backend export route | Present. |
| Management Brief | PDF export | Matches | same | backend export route | Present. |
| Data Quality | Four summary cards | Matches | `pages/data_quality.py` | `frontend/components/data-quality-dashboard.tsx` | Same metrics. |
| Data Quality | Ordered checks table | Matches | same | same | Sorting/paging presentation differs slightly. |
| Data Quality | Top-25 issue detail expanders | Matches | same | same | Includes the source `share_pct` progress visualization without recalculation. |
| Data Quality | CSV and PDF exports | Matches | same | backend exports | Present. |
| Data Quality | Cleaning log | Matches | same | same | The migrated page mirrors the reference-friendly missing-log state while API data remains available and verified. |
| Global | Loading states | Different | Streamlit spinners/skeleton behavior | route/component skeletons | Next.js uses native skeletons; functional intent matches but appearance does not. |
| Global | Error states | Different | `st.error` / `st.warning` | React alert panels | Messages are safe, but visual language differs. |
| Global | Empty tables | Matches | `src/ui/components.py` | `frontend/components/data-table.tsx` | Both show a friendly empty state. |

## Number parity

The machine-readable result is `docs/screenshots/parity/number-parity.json`. It contains ten scenarios and reports **0 mismatches**.

| Scenario | Filters |
|---|---|
| `default_90_days` | 2025-04-02 through 2025-06-30 |
| `full_range` | Full available date range |
| `branch_accra` | Accra |
| `branch_kumasi_90_days` | Kumasi, default 90-day period |
| `model_hilux` | Hilux |
| `model_corolla_90_days` | Corolla, default 90-day period |
| `brand_elara` | Elara |
| `completed_90_days` | Completed sales, default 90-day period |
| `single_day` | One-day range |
| `valid_empty_pair` | Kasoa + Yaris, default period |

For every scenario, the audit compared:

- all Overview KPI records, including current and comparison values;
- every revenue-trend record and its total;
- every revenue-by-branch record and its total;
- every gross-margin-by-model record and its total;
- warranty model-table row count and claim-cost total;
- the four Ask cards (completed-sale revenue, completed sales, branches and available inventory older than 90 days).

The unfiltered Ask display baseline remains:

- Revenue: **GHS 5.58B**
- Completed sales: **19,755**
- Branches: **15**
- Available over 90 days: **4,484**

No formula was changed or normalized during this audit.

## Chart comparison

| Chart | Reference | New app | Difference / severity |
|---|---|---|---|
| Revenue trend | Plotly spline line, 2.4 px, green `#16C060`, vertical translucent green fill, 400 px high; explicit Month and Revenue (GHS) axis titles; horizontal legend top-right; 12 px Inter; hover shows month plus full comma-formatted value | Recharts monotone area, green `#16C060`, matching translucent fill and 400 px height; matching axis titles, legend policy, Inter typography and full-value hover | **Resolved:** records, totals and presentation contract match. |
| Revenue by branch | Plotly horizontal bars, primary green, 400 px; rounded 6 px ends; bargap 0.28; explicit axis titles; top-right legend; full-value hover | Recharts horizontal bars, primary green, 400 px; rounded ends; matching axis titles, legend policy and full-value hover | **Resolved:** records, totals and presentation contract match. |
| Gross margin by model | Plotly horizontal bars using primary green, 400 px; explicit axis titles; top-right legend; full-value hover | Recharts horizontal bars using primary green, 400 px; matching axis titles, legend policy and full-value hover | **Resolved:** the incorrect teal series and compact presentation were replaced without changing data. |

Both implementations use Inter and transparent chart surfaces. Both remove axis lines, use muted labels, dashed grid treatment, rounded bars, responsive width and hover tooltips. Recharts uses CSS variables for theme-aware text/grid/tooltip surfaces; Plotly reads the Streamlit theme palette.

## Visual comparison findings

The harness names assets as `<state>-<width>-<theme>-streamlit.png`, `...-nextjs.png`, and `...-diff.png`. It produced 72 responsive light-mode image artifacts plus the numeric report before the reference mobile navigation defect stopped the full matrix. Dark-mode and 1280px paths are encoded in the harness but were not claimed as completed evidence.

Pixel-difference percentages are useful for locating change, not for deciding correctness: Streamlit and React produce different DOM geometry, and sub-pixel font rendering is intentionally ignored by the review.

| Page/state | Observed difference | Severity |
|---|---|---:|
| Landing | Logo/hero sizing, text wrapping and bottom-card overlap were aligned to the reference geometry. | Resolved |
| Login | Card width, vertical centering, input height and forgot-password presentation differ. | Low |
| Overview | Next.js card and chart skeletons were visible in early captures because the generic settle delay did not wait for API content; the final tool should wait on page-specific readiness before screenshotting. | Audit-tool issue |
| Overview | Semantic KPI icons now match the reference intent and visual weight. | Resolved |
| Overview | The evidence-navigation card is restored with its filter-preserving destination. | Resolved |
| Overview charts | Heights, axis titles, legends, full-value tooltips and primary-green series are aligned. | Resolved |
| Sidebar open | Next.js drawer correctly shows logo, navigation, filters and close control. At 375px the Streamlit reference can show only a dimmed backdrop while the drawer remains off-canvas. | High (reference bug) |
| Sidebar/filter panel | Compact popover controls replace the tall native multi-select presentation. | Resolved |
| Investigate models | Table chrome, selection action and breadcrumb geometry are aligned while preserving the same hierarchy. | Resolved |
| Investigate branches | The select + View workflow matches the reference. | Resolved |
| Investigate claims | Numbered pagination, active-page styling and downloads are aligned. | Resolved |
| Ask before | Summary cards, prompt controls and empty-conversation guidance are aligned. | Resolved |
| Ask after | Ask/History, inline evidence and answer headings match the current reference. | Resolved |
| Management Brief | Sequential sections, evidence identifiers, supporting evidence and export labels are aligned. | Resolved |
| Data Quality | Progress visualization and friendly cleaning-log state match the reference. | Resolved |
| Empty filter | Number audit confirms the empty combination. Automated screenshot capture was the final interrupted step because the Streamlit mobile overlay intercepted its sidebar fields. | High (reference bug / incomplete visual evidence) |

### Visual-run limitation

At 375px the Streamlit source adds `versal-mobile-nav-open` whenever a collapse control exists, even when the sidebar remains off-canvas. Its `.versal-sidebar-backdrop` is then recreated by a MutationObserver and intercepts clicks after navigation. This is visible in the Playwright traces and is itself a user-visible regression. The audit tool contains a narrowly scoped cleanup for content screenshots but does not alter application files. The run was stopped rather than modifying the reference app, as required.

## Implementation verification

- Python regression suite: **130 passed**, **24 subtests passed**.
- Navigation/auth/theme Playwright suite: **16 passed**.
- Overview/Investigate/Ask/Brief/Data Quality Playwright suites: **16 passed**.
- Ten-scenario number check: **0 mismatches** after the High fixes and **0 mismatches** after the Medium fixes.
- Production lint and build: passed during implementation.
- Before, after and difference images for the High items are stored in `docs/screenshots/parity/high-before/`, `high-after/` and `high-diff/`.

The complete cross-app screenshot loop remains limited by the reference Streamlit mobile backdrop described above. Targeted migrated-app screenshots and responsive browser tests cover 375 px, 768 px and 1280 px without changing the reference. No calculation, analytics, AI, data, cleaning, script or database file was changed by the approved fixes.

## Remaining item

The Streamlit mobile backdrop defect remains a reference-only issue. It should be fixed only if the legacy reference itself is deliberately reopened for maintenance; it does not block or occur in the migrated Next.js app.
