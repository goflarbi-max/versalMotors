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

Numerical parity is strong: **zero mismatches** were found across ten filter combinations for KPI records, revenue-trend records and totals, branch-chart records and totals, model-margin records and totals, warranty drill-down row counts/totals, and the four Ask the Business summary cards.

Feature and visual parity is incomplete. The highest-impact gaps are:

1. The migrated Overview omits the reference “Investigate the evidence” action.
2. Ask the Business does not preserve the reference Ask/History experience or the same fallback/warning presentation.
3. Shared filters appear on every protected Next.js page, while the reference shows them only on Overview and Investigate.
4. Overview charts differ in height, axis titles, legend, tooltip formatting and one series colour.
5. The reference Streamlit mobile sidebar currently leaves a backdrop active after navigation, which blocks controls. This is a reference regression and prevented the automated dark/1280 matrix from completing without altering the reference DOM.

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
| Filters | Filters shown only where reference uses them | Different | `pages/overview.py`, `pages/investigate.py` | `frontend/components/app-shell.tsx` | Next.js displays the filter panel on Ask, Brief and Data Quality too. |
| Overview | Revenue KPI and comparison | Matches | `pages/overview.py` | `frontend/components/overview-dashboard.tsx` | Same source result and caption. |
| Overview | Gross margin KPI and comparison | Matches | same | same | Same source result and caption. |
| Overview | Units sold KPI and comparison | Matches | same | same | Same source result and caption. |
| Overview | Discount rate KPI and comparison | Matches | same | same | Same source result and caption. |
| Overview | KPI material icons | Different | `src/ui/components.py` | `frontend/components/overview-dashboard.tsx` | React source uses replacement glyph strings for three cards rather than the reference material icons. |
| Overview | Revenue trend chart | Different | `pages/overview.py`, `src/ui/charts.py` | `frontend/components/overview-charts.tsx` | Data matches; rendering details differ. |
| Overview | Revenue by branch chart | Different | same | same | Data matches; rendering details differ. |
| Overview | Gross margin by model chart | Different | same | same | Data matches; colour, height, labels and tooltip differ. |
| Overview | “Investigate the evidence” navigation card | Missing | `pages/overview.py` | — | No equivalent link/card appears after the charts. |
| Overview | Empty-filter friendly state | Matches | `pages/overview.py` | `frontend/components/overview-dashboard.tsx` | Both avoid crashing and provide a reset/recovery path. |
| Investigate | Breadcrumbs: warranty cost → model → branch | Matches | `pages/investigate.py` | `frontend/components/investigate-dashboard.tsx` | Same hierarchy. |
| Investigate | Model-level warranty table | Matches | `pages/investigate.py` | `frontend/components/investigate-dashboard.tsx` | Data and totals match. |
| Investigate | Branch-level warranty table | Matches | same | same | Data and totals match. |
| Investigate | Claim-record table | Matches | same | same | Same records are available. |
| Investigate | Drill-down selection workflow | Different | `pages/investigate.py` | `frontend/components/investigate-dashboard.tsx` | Streamlit uses a selectbox plus View button; Next.js exposes row actions/query state. |
| Investigate | Sorting, paging and “Showing x to y of z entries” | Matches | `src/ui/components.py` | `frontend/components/data-table.tsx` | Both preserve source data and paginate display copies. |
| Investigate | Full filtered CSV download | Matches | `pages/investigate.py` | Investigate download route/component | Not limited to the visible page. |
| Investigate | PDF download | Matches | `pages/investigate.py` | backend export endpoint | Same deterministic exporter family. |
| Ask | Four summary cards | Matches | `pages/ask_the_business.py` | `frontend/components/ask-dashboard.tsx` | Values exactly match. |
| Ask | Four reviewed quick questions | Matches | `pages/ask_the_business.py` | backend ask suggestions + `ask-dashboard.tsx` | Same labels and reviewed questions. |
| Ask | Ask / History tabs | Missing | `pages/ask_the_business.py` | — | Next.js has a single conversation view. |
| Ask | Clear chat | Different | `pages/ask_the_business.py` | `frontend/components/ask-dashboard.tsx` | Streamlit places it in the sidebar; Next.js shows it in the toolbar only after a message exists. |
| Ask | Typed questions and Enter/submit | Matches | `pages/ask_the_business.py` | `frontend/components/ask-dashboard.tsx` | Input is capped at 500 characters in Next.js. |
| Ask | Facts / Interpretation / Recommendations | Different | current Streamlit answer renderer | `frontend/components/ask-dashboard.tsx` | Current Streamlit intentionally does not show a FACTS heading; Next.js shows `Facts` when `facts` is populated. |
| Ask | Evidence display | Different | `pages/ask_the_business.py` | `frontend/components/ask-dashboard.tsx` | Streamlit renders the evidence table inline; Next.js uses a collapsed Supporting evidence expander. |
| Ask | Evidence SQL hidden from users | Matches | `pages/ask_the_business.py` | `frontend/components/ask-dashboard.tsx` | Neither user UI displays raw SQL. |
| Ask | Unanswerable question message | Matches | ask page/tools | backend ask service | Both return a safe reviewed-scope response. |
| Ask | “Unverified” guardrail warning | Missing from current data-only Next flow | `src/ai/guardrails.py`, ask page | — | The migrated Ask flow is deliberately deterministic/data-only, so the model-verification state is not exposed. Strict parity is missing. |
| Ask | AI outage fallback notice | Different | `pages/ask_the_business.py` | backend ask service | Streamlit can show “AI temporarily unavailable” before a deterministic result; Next.js always presents deterministic mode as “Verified data result.” |
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
| Data Quality | Top-25 issue detail expanders | Different | same | same | Streamlit includes a progress/share visualization; Next.js omits the progress bar. |
| Data Quality | CSV and PDF exports | Matches | same | backend exports | Present. |
| Data Quality | Cleaning log | Different | same | same | Reference currently shows a friendly missing-log state; Next.js shows the available cleaning-log table. The migration plan explicitly identified this as an unresolved visible correction. |
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
| Revenue trend | Plotly spline line, 2.4 px, green `#16C060`, vertical translucent green fill, 400 px high; explicit Month and Revenue (GHS) axis titles; horizontal legend top-right; 12 px Inter; hover shows month plus full comma-formatted value | Recharts monotone area, 2.5 px, green `#16C060`, similar gradient, 310 px high (300 px mobile); no axis titles or legend; 11 px Inter ticks; compact-GHS hover | **Medium:** same data/type intent, but height, axis titles, legend and tooltip precision differ. |
| Revenue by branch | Plotly horizontal bars, primary green, 400 px; rounded 6 px ends; bargap 0.28; explicit axis titles; top-right legend; full-value hover | Recharts horizontal bars, green, 360 px (300 px mobile); rounded 7 px ends; max 24 px; no axis titles/legend; compact hover | **Medium:** semantic parity, visible layout/label/tooltip differences. |
| Gross margin by model | Plotly horizontal bars using primary green, 400 px; explicit axis titles; top-right legend; full-value hover | Recharts horizontal bars using teal `#3DB2A0`, 310 px; no axis titles/legend; compact hover | **High:** series colour is not the same, in addition to height/label/tooltip differences. |

Both implementations use Inter and transparent chart surfaces. Both remove axis lines, use muted labels, dashed grid treatment, rounded bars, responsive width and hover tooltips. Recharts uses CSS variables for theme-aware text/grid/tooltip surfaces; Plotly reads the Streamlit theme palette.

## Visual comparison findings

The harness names assets as `<state>-<width>-<theme>-streamlit.png`, `...-nextjs.png`, and `...-diff.png`. It produced 72 responsive light-mode image artifacts plus the numeric report before the reference mobile navigation defect stopped the full matrix. Dark-mode and 1280px paths are encoded in the harness but were not claimed as completed evidence.

Pixel-difference percentages are useful for locating change, not for deciding correctness: Streamlit and React produce different DOM geometry, and sub-pixel font rendering is intentionally ignored by the review.

| Page/state | Observed difference | Severity |
|---|---|---:|
| Landing | Content is close, but logo/hero sizing, text wrapping and bottom-card overlap differ by viewport. | Medium |
| Login | Card width, vertical centering, input height and forgot-password presentation differ. | Low |
| Overview | Next.js card and chart skeletons were visible in early captures because the generic settle delay did not wait for API content; the final tool should wait on page-specific readiness before screenshotting. | Audit-tool issue |
| Overview | Migrated KPI icons do not match the material icons used by Streamlit. | Medium |
| Overview | The reference evidence-navigation card is absent. | High |
| Overview charts | Chart heights, axis titles, legends, tooltip formatting and model-series colour differ as documented above. | High |
| Sidebar open | Next.js drawer correctly shows logo, navigation, filters and close control. At 375px the Streamlit reference can show only a dimmed backdrop while the drawer remains off-canvas. | High (reference bug) |
| Sidebar/filter panel | Next.js native multi-selects show multiple raw options at once; Streamlit uses compact popover multiselects. This makes the drawer much taller in Next.js. | Medium |
| Investigate models | Same data hierarchy; table chrome, action placement and breadcrumb geometry differ. | Medium |
| Investigate branches | Streamlit uses select + View; Next.js uses explicit row drill actions/query state. | Medium |
| Investigate claims | Same records available; pagination controls and download placement differ. | Medium |
| Ask before | Four values match. Card radius/shadow, prompt-chip sizing and empty-conversation guidance differ. | Medium |
| Ask after | Streamlit inline evidence and tabbed history differ from Next.js collapsed evidence and `Facts` heading. | High |
| Management Brief | Section content exists in both; Next.js uses a report-card layout and Streamlit uses sequential markdown/expanders. | Medium |
| Data Quality | Next.js displays the cleaning log while Streamlit reports it missing; detail progress visuals differ. | High until product decision |
| Empty filter | Number audit confirms the empty combination. Automated screenshot capture was the final interrupted step because the Streamlit mobile overlay intercepted its sidebar fields. | High (reference bug / incomplete visual evidence) |

### Visual-run limitation

At 375px the Streamlit source adds `versal-mobile-nav-open` whenever a collapse control exists, even when the sidebar remains off-canvas. Its `.versal-sidebar-backdrop` is then recreated by a MutationObserver and intercepts clicks after navigation. This is visible in the Playwright traces and is itself a user-visible regression. The audit tool contains a narrowly scoped cleanup for content screenshots but does not alter application files. The run was stopped rather than modifying the reference app, as required.

## Ranked fix list

| Rank | Fix | Estimate | Why |
|---:|---|---:|---|
| 1 | Fix the Streamlit reference mobile sidebar state/backdrop, or formally declare the Next.js behavior authoritative before completing screenshot baseline approval. | 0.5-1 day | It blocks reference interaction and the complete visual matrix. |
| 2 | Restore Overview's “Investigate the evidence” action in Next.js with the same destination and caption. | 1-2 hours | Clearly missing management workflow. |
| 3 | Decide strict Ask parity versus the approved data-only product direction; then restore History/fallback-warning semantics or record them as intentionally retired. | 0.5-1.5 days | Current behavior is materially different, but some difference was previously requested. |
| 4 | Align Overview charts: 400 px height, axis titles, legend policy, full-value tooltips, and green model-margin bars. | 0.5-1 day | Largest visual mismatch on the primary management page. |
| 5 | Restrict shared filters to Overview and Investigate, unless the always-visible panel is explicitly approved. | 2-4 hours | Current new-app placement does not match reference behavior. |
| 6 | Replace Overview placeholder glyphs with the same semantic line icons as the reference. | 1-2 hours | Obvious card-level mismatch. |
| 7 | Match Ask evidence/history and clear-chat placement after the product decision in item 3. | 0.5-1 day | High workflow visibility. |
| 8 | Resolve Data Quality cleaning-log policy and progress visualization. | 2-4 hours | Migration plan already calls this out as an open parity decision. |
| 9 | Tighten table chrome, prompt chips, card spacing and login spacing from the diff images. | 0.5-1 day | Cosmetic after functional gaps. |
| 10 | Add page-specific Playwright readiness markers so screenshots never capture skeletons. | 2-4 hours | Makes future visual gates deterministic. |

## Questions requiring approval

1. Should Ask the Business follow strict Streamlit parity (History tab, AI-unavailable/unverified states) or retain the newer explicitly requested deterministic data-only experience?
2. Should Data Quality reproduce the reference's “No cleaning log file found” message, or keep the more useful migrated cleaning-log table?
3. Should filters be removed from Ask, Management Brief and Data Quality to match the reference exactly?
4. May the reference Streamlit mobile-sidebar regression be fixed solely to complete the visual baseline, or should the audit treat the migrated drawer as the authoritative behavior?
5. Should chart parity include the Plotly legend and axis titles even for single-series charts, or may the cleaner Recharts presentation remain?

No application, analytics, AI, data, cleaning, script or database file was changed by this audit.
