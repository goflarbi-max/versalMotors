# VersalMotors production web migration plan

## Decision summary

Migrate incrementally to a Next.js frontend and FastAPI backend while the current Streamlit deployment remains live. The existing Python business layer remains the source of truth: `src/analytics`, `src/ai`, `src/data`, `scripts`, the DuckDB data, and the cleaning log are not rewritten. The FastAPI service loads the same tables and calls the same public analytics, drill-down, AI, guardrail, and database-tool functions.

The migration is a parallel build, not an in-place rewrite. Nothing moves into `legacy/streamlit_app/` until Phase 8, parity passes, the new production deployment is healthy, and cutover is explicitly approved.

Recommended choices:

- Backend: FastAPI, Pydantic, uvicorn, one Docker container and one worker initially.
- Frontend: Next.js App Router, TypeScript, Tailwind CSS, and Inter through `next/font`.
- Charts: Recharts, loaded only on chart pages. The current app uses small monthly, branch, and model datasets and simple line/bar charts; Recharts gives direct React composition and responsive SVG without shipping the broader ECharts runtime. ECharts would become preferable only if the system later needs dense, high-frequency series or thousands of interactive points, where its Canvas renderer is stronger.
- API hosting: Railway Hobby in Amsterdam, with Serverless disabled for production. It is the simplest Docker/Git deployment, has health checks and rollback support, and avoids a sleeping API's first-request delay or possible 502. Fly.io in Johannesburg is the alternative if measured Ghana-to-Amsterdam latency is unacceptable.
- PDF: keep the existing deterministic `fpdf2` backend exporters for parity. Do not introduce browser-based PDF rendering during the migration.
- Browser-to-API path: `/api/*` on `autobusiness.goflarbi.com` is rewritten by Next.js/Vercel to the external FastAPI origin. The browser sees one origin, and the session cookie remains first-party.

## Constraints and current-repository findings

- The tracked rules file is `docs/.agent/rules/project-rules.md`; the requested root path `.agent/rules/project-rules.md` does not exist. The tracked file should be updated after plan approval unless a root-level replacement is explicitly requested.
- `data/raw/*.csv` is tracked. `data/cleaned/` and `data/business.duckdb` are ignored. The current deterministic build is `python scripts/build_database.py`.
- The local DuckDB file is about 26 MB; the nine cleaned CSVs total about 61 MB. A multi-stage image can build the database and copy only the read-only DuckDB file plus required documentation into the runtime image.
- The repository currently has no `src/analytics/insights.py` registry. This migration will not invent a new feature while claiming parity. If the previously planned insight registry is still required, it should be approved as a separate functional phase.
- Existing authentication is coupled to `st.session_state`. The bcrypt algorithm, dummy-hash timing protection, validation messages, five-attempt threshold, and 60-second lockout will be preserved, but the web backend needs a request-safe state adapter rather than Streamlit session state.
- Existing Ask the Business summary cards are unfiltered, while Overview and Investigate use the shared filters. Migration parity preserves that behavior unless filtered Ask cards are separately approved.

## Target folder structure

During Phases 0-7, the current root `app.py`, `pages/`, `src/ui/`, `.streamlit/`, and Streamlit requirements stay in place and deployable.

```text
VersalMotors/
|-- backend/
|   |-- app/
|   |   |-- main.py                 # FastAPI application and lifespan
|   |   |-- api/
|   |   |   |-- dependencies.py     # auth, filters, DuckDB/data dependencies
|   |   |   `-- routes/             # auth, overview, investigate, ask, brief, quality
|   |   |-- core/
|   |   |   |-- config.py           # environment-only settings
|   |   |   |-- security.py         # signed cookie, CSRF/origin checks, headers
|   |   |   |-- rate_limit.py       # login and Ask limits
|   |   |   `-- cache.py            # bounded TTL cache
|   |   |-- schemas/                 # Pydantic request and response models
|   |   `-- services/                # thin adapters calling existing src modules
|   |-- tests/
|   |-- Dockerfile
|   `-- requirements.txt
|-- frontend/
|   |-- app/
|   |   |-- (public)/               # landing and login
|   |   |-- (protected)/             # overview and four protected pages
|   |   |-- api-health/              # optional internal diagnostic route
|   |   |-- layout.tsx
|   |   `-- globals.css
|   |-- components/                  # sidebar, filters, tables, charts, evidence
|   |-- lib/                         # typed API client, formatting, filter URL state
|   |-- public/                      # existing approved logo/background assets
|   |-- tests/                       # component tests if introduced
|   |-- playwright/
|   |-- next.config.ts               # same-origin /api rewrite
|   |-- package.json
|   `-- tsconfig.json
|-- legacy/
|   `-- streamlit_app/               # created only after approved Phase 8 cutover
|-- src/                              # existing business source of truth; retained
|-- scripts/                          # retained unchanged
|-- data/                             # retained unchanged
|-- tests/
|   |-- parity_baseline.json
|   `-- test_api_parity.py
|-- docs/
|   |-- migration_plan.md
|   |-- architecture.md
|   `-- ...
|-- app.py                            # retained through Phase 7
`-- requirements.txt                 # retained through Phase 7
```

The Python container sets the repository root on `PYTHONPATH`, so adapters import the current modules rather than copying their formulas.

## Phase 0: immutable baseline and parity gate

Before any backend or frontend implementation:

1. Build the database from the tracked raw CSVs with the existing script.
2. Record the Git commit, database SHA-256, source CSV hashes, table row counts, maximum source update date, and Python/package versions.
3. Call the existing functions directly and write `tests/parity_baseline.json`.
4. Serialize timestamps as ISO 8601, `NaN` as `null`, and money at full returned precision plus its exact current display string. Parity checks compare display strings exactly and raw finite floats with a maximum absolute tolerance of `1e-9` (or `0.005` for independently serialized currency values).
5. Store ordered records for small datasets and a stable schema/row-count/content hash for large record tables.

Baseline filter scenarios:

- Current default 90-day range, with no dimensional filters.
- Full available date range.
- One exact branch over the full range.
- One exact model over the full range.
- One exact brand plus salesperson combination.
- All shared filters together using a known non-empty combination.
- A single-day range.
- A known empty-result combination.

Baseline outputs:

- Overview: four KPI rows including previous value/change, revenue trend, revenue by branch, and gross margin by model.
- Investigate: warranty by model, one selected model by branch, and one model/branch claim record set.
- Ask the Business: revenue, completed sales, branches, available-over-90-days cards; the four reviewed quick-question result tables and deterministic answers.
- Management Brief: KPI values and evidence objects for fixed dates; Markdown and PDF content checks excluding nondeterministic PDF metadata if any.
- Data Quality: summary counts, the ordered validation-check table, CSV bytes, and cleaning-log presence/content hash.

`tests/test_api_parity.py` will call the new API and compare it with this file. A phase cannot pass if the API changes a value, row order, null policy, quality exclusion, filter behavior, or display format without explicit approval.

## Shared API conventions

Base path: `/api/v1`.

Shared filter query parameters where the current feature supports them:

| Parameter | Type | Rule |
|---|---|---|
| `start_date`, `end_date` | ISO date | Both optional; inclusive; `end_date >= start_date` |
| `branch`, `brand`, `model`, `salesperson`, `status` | repeated string query parameters | Exact matching only; maximum 50 values per dimension |
| `period` | enum | `D`, `W`, `M`, `Q`, `Y`; default `M` |

Responses use `{ "data": ..., "meta": { "filters": ..., "data_version": ..., "generated_at": ... } }`. Errors use one consistent problem shape with a safe public message, status, request ID, and no stack trace or credentials.

Paginated tables accept `page` (minimum 1), `page_size` (`10`, `25`, or `50`), `sort_by` from a route-specific allowlist, and `sort_dir` (`original`, `asc`, `desc`). Sorting is stable and nulls remain last. CSV endpoints apply the same filters and requested stable sort but ignore pagination, returning the full filtered data. No client-supplied column name is interpolated into SQL without an allowlist lookup.

## API design

| Method | Path | Parameters/body | Response shape | Existing source called |
|---|---|---|---|---|
| `GET` | `/health/live` | none | process status | no business query |
| `GET` | `/health/ready` | none | database presence, required-table check, data version | `src.database.bootstrap.database_is_ready` or equivalent read-only check |
| `POST` | `/auth/login` | `{email,password}` plus CSRF/origin checks | user summary; sets signed cookie | existing bcrypt/user-loading/validation rules from `src.auth.auth` through a request-safe adapter |
| `POST` | `/auth/logout` | none | `204`; clears cookie | preserves current logout outcome |
| `GET` | `/auth/me` | none | `{authenticated,email}` | signed-session validator |
| `GET` | `/filters/options` | optional date bounds | valid branch, brand, model, salesperson, status options and min/max dates | same table/column sources used by `src.ui.filters` |
| `GET` | `/overview/kpis` | shared filters | four KPI records with current/prior/change/change rate | `src.analytics.metrics.overview_kpis` |
| `GET` | `/overview/revenue-trend` | shared filters | ordered `{period,revenue,sales_count}` records | `src.analytics.metrics.revenue` |
| `GET` | `/overview/revenue-by-branch` | shared filters | ordered branch records | `src.analytics.metrics.revenue_by_branch` |
| `GET` | `/overview/margin-by-model` | shared filters | ordered model records | `src.analytics.metrics.gross_margin_by_model` |
| `GET` | `/investigate/warranty/models` | shared filters plus paging/sort | model summary page | `src.analytics.drilldown.warranty_by_model` |
| `GET` | `/investigate/warranty/models/{model}/branches` | shared filters plus paging/sort | branch summary page | `src.analytics.drilldown.warranty_by_branch` |
| `GET` | `/investigate/warranty/models/{model}/branches/{branch}/claims` | shared filters plus paging/sort | claim record page | `src.analytics.drilldown.warranty_claim_records` |
| `GET` | `/investigate/warranty/.../claims.csv` | shared filters plus optional sort | full filtered CSV stream | same claim DataFrame, no page slicing |
| `GET` | `/investigate/warranty/.../claims.pdf` | shared filters plus optional sort | PDF bytes | same claim DataFrame + current `dataframe_to_pdf` behavior |
| `GET` | `/ask/summary` | none for current parity | four summary values | current reviewed `run_readonly_sql` statements from Ask page |
| `POST` | `/ask/questions` | `{question}`; optional shared filter object reserved but disabled until approved | `{answer,status,evidence,table,mode}` with Facts/Interpretation/Recommendations fields kept separate when present | `validate_question`, `handle_unanswerable`, `generate_text`, `run_with_reviewed_fallback`, `build_fallback_evidence`, `fallback_response`, `build_grounded_response`, `run_readonly_sql` |
| `GET` | `/ask/suggestions` | none | the four reviewed labels/questions | current `SUGGESTIONS` values moved into the backend route adapter, not business formulas |
| `POST` | `/management-brief` | `{start_date,end_date}` | brief sections, evidence records, supporting tables, short-lived `report_id` | `get_kpis_for_period`, `build_evidence`, `generate_brief_sections` |
| `GET` | `/management-brief/{report_id}.md` | none | Markdown download | cached output from the same generation request |
| `GET` | `/management-brief/{report_id}.pdf` | none | PDF download | cached Markdown + current `text_to_pdf` behavior |
| `GET` | `/data-quality/summary` | none | issues, tables affected, total affected, highest share | current live validation-check rules |
| `GET` | `/data-quality/checks` | paging/sort | validation-check table | same current checks, executed read-only |
| `GET` | `/data-quality/checks.csv` | optional sort | full CSV | same unsliced check DataFrame |
| `GET` | `/data-quality/checks.pdf` | optional sort | PDF | same DataFrame + current exporter |
| `GET` | `/data-quality/cleaning-log` | paging/sort | existing cleaning log records or current friendly absence state | bundled cleaning log / `cleaning_log` DuckDB table, subject to the open question below |

The API adapter loads the nine tables once per data version into the existing `AnalyticsData` dataclass. It must not reimplement formulas in SQL merely for convenience.

## Authentication and authorization

Preserve these current behaviors exactly: normalized lowercase email, email validation, bcrypt hashes, a dummy bcrypt check for unknown accounts, identical wrong-email/wrong-password message, maximum five failures, 60-second lockout, no password in logs or session, and the demo credential source only on the backend.

The current `verify_credentials()` is bound to `st.session_state`. In Phase 1, extract its framework-neutral validation and bcrypt operation into a shared pure helper while leaving the Streamlit public functions and tests compatible. The FastAPI adapter supplies a request-safe lockout store. This is an authentication plumbing refactor, not a change to verification rules.

- Successful login sets an HMAC-signed, expiring session cookie containing only normalized email, issued/expiry timestamps, and a random session ID.
- Cookie flags: `HttpOnly`, `Secure`, `SameSite=Lax`, `Path=/`, no JavaScript access, and no broad `Domain` attribute.
- Logout expires the cookie and invalidates the session ID for its remaining lifetime.
- Default session lifetime: 8 hours, configurable by backend environment variable.
- All API routes except health and login are protected by a FastAPI dependency.
- Next.js middleware/server layouts call `/api/v1/auth/me`; signed-out users may access only landing and login. Direct protected URLs redirect to login.
- The login rate limit uses normalized email plus client IP; Ask the Business uses authenticated email plus IP. Initial limits: login 5 failures/60 seconds to match current behavior and Ask 10 requests/minute with a burst of 3. Return `429` with `Retry-After`.
- The first deployment uses a bounded in-memory TTL store because it is one API process. Before multiple workers/replicas, move lockouts, revoked sessions, report IDs, and rate limits to Redis; otherwise replicas could disagree.
- Mutating routes require an allowed `Origin` and a CSRF token/header in addition to `SameSite=Lax`.

Secrets are backend environment variables only: user JSON/hashes, session-signing secret, Gemini key/model, allowed origins, and optional proxy/origin secret. No `NEXT_PUBLIC_*` variable contains a credential or API key.

## Security controls

- Keep `run_readonly_sql` and its SELECT/WITH, single-statement, function, keyword, extension, and table allowlists. AI-generated SQL never bypasses it.
- Pydantic models enforce date order, question length, list sizes, enum values, page bounds, and allowed sort columns.
- Route adapters use existing exact filters and parameterized values. They do not accept raw SQL from the browser.
- CORS permits only `https://autobusiness.goflarbi.com` and explicit Vercel preview origins during preview testing; production browser requests use same-origin `/api` rewrites.
- Add Content-Security-Policy, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy`, frame denial, and HSTS at Vercel/API as appropriate.
- Escape all free-text table/evidence content in React. Do not use unsanitized `dangerouslySetInnerHTML`.
- Logs contain request IDs, route, duration, response status, cache result, and normalized error category—not questions with sensitive content, passwords, cookies, hashes, SQL bodies, or Gemini keys.
- Run the container as a non-root user with a read-only root filesystem where the host permits it. The DuckDB file is opened read-only.

## Frontend behavior and parity

- Landing page remains public and uses the fixed black hero, white logo, icon row, current copy/cards, and reduced-motion-aware animations.
- Login remains public and fixed light-only with the existing glass card and charcoal Sign In button.
- Protected layout contains the current sidebar, hamburger/drawer behavior, signed-in email, sign-out, theme switch, and shared filters.
- Light is the default. Dark selection is persisted in a cookie/local storage and mirrored before first paint by an inline theme bootstrap in the root layout, preventing a light/dark flash. The protected dark main background remains `#0F172A`; landing and login keep their fixed designs.
- Filters live in URL search parameters, so they persist across page links, browser navigation, refresh, and shareable URLs. A typed filter provider keeps controls synchronized.
- Tables use server-side sorting/paging and the same default row order. Only the current page renders. CSV/PDF links use the same filter/sort query but export all matching records.
- Recharts components receive the API records unchanged; formatting stays in one frontend formatter module that is parity-tested against current display strings.
- Ask keeps the reviewed fallback and evidence table. The browser never receives the Gemini key and never executes SQL.
- Facts, Interpretation, and Recommendations remain separate data fields/components; empty sections are omitted rather than fabricated.

## Performance and removal of Streamlit artifacts

The Next.js app is native HTML/CSS/React, not an iframe, so it has no Streamlit toolbar, branding, “Made with Streamlit” footer, iframe border, or script rerun model.

- Protected layouts and navigation are persistent; route changes update only the content segment.
- Use App Router server components for initial page data where authenticated proxying is reliable, then small client components for filters, tables, drill-down, theme, and Ask.
- Each route has a `loading.tsx` skeleton with final dimensions to avoid layout shift. Existing data remains visible during filter transitions where appropriate.
- Native `fetch`, `useTransition`, and AbortController prevent duplicate/stale responses; no whole-page reload is required.
- Backend cache: bounded in-memory TTL/LRU keyed by data-version + function + canonical filters. Suggested TTL: 5 minutes for metrics/drill-down/filter options/data-quality, 15 minutes for generated brief artifacts, no shared cache for authenticated chat response text. Cache DataFrames/results, never user credentials.
- Build `AnalyticsData` once per DuckDB data version. Invalidate all caches when the database hash changes.
- Start with one uvicorn worker to avoid duplicated DataFrames/cache memory and DuckDB concurrency ambiguity. Load-test before adding workers.
- Dynamically import Recharts only on pages that use charts. Keep series small and responsive; render no off-screen chart libraries on landing/login.
- Targets after warm start: health under 100 ms, cached KPI response under 300 ms, uncached overview under 1 second, page navigation feedback under 100 ms, and non-AI content usable while AI is pending.

## Data and container build

Use a multi-stage backend Docker build:

1. Install the pinned Python dependencies.
2. Copy tracked `data/raw`, `src/data`, `scripts`, and required source.
3. Run the unchanged `python scripts/build_database.py` at image build time.
4. Verify required tables, row counts, cleaning-log table, and the baseline data hash.
5. Copy only the built `data/business.duckdb`, required docs/log artifact, Python source, and backend application into a slim non-root runtime stage.
6. Open DuckDB read-only at runtime. Do not rebuild on every container start and do not depend on ephemeral writes.

This makes deployments reproducible from the public repository while keeping ignored generated files out of Git. A future real-data system would move to object storage or a managed analytical store, but that is outside this synthetic project migration.

Backend secrets are configured in the container host dashboard. Frontend receives only `API_ORIGIN` as a server-side Vercel variable for the rewrite and non-secret public build metadata.

## Hosting comparison and recommendation

Platform facts were checked against official documentation on 23 October 2026.

| Host | Cold-start behavior | Cost shape | Closest useful region for Ghana | Ease for this project | Assessment |
|---|---|---|---|---|---|
| Render | Free services sleep after 15 minutes and take about one minute to resume; paid compute stays active. | Free preview option; paid instance required to remove sleep. | Frankfurt. | Very easy Git/Docker UI, health checks, logs and rollback. | Easiest trial, but the free cold start is unacceptable for the production hostname. A paid plan remains viable. |
| Railway | Optional Serverless sleeps after roughly 5-10 idle minutes; first request has a cold delay and may return 502. It can be disabled. | Free experimentation provides limited resources; Hobby has a $5 minimum including $5 usage, then metered CPU/RAM/egress. | Amsterdam. | Easiest paid path: Dockerfile/GitHub deploy, environment variables, health check and rollback in one UI. | **Recommended:** Hobby, Serverless off, one always-on service in Amsterdam. Measure actual monthly RAM/CPU because DuckDB/Pandas may exceed the $5 included usage. |
| Fly.io | Scale-to-zero cold starts are about 2 seconds or more; suspend/resume can be a few hundred milliseconds. One machine can remain running. | No platform minimum; smallest always-on machine is listed at $2.19/month, 512 MB at $3.69 and 1 GB at $6.70 in lowest-cost US regions; regional prices vary. | Johannesburg. | Best geographic option, but more CLI, `fly.toml`, Machine sizing and operational responsibility. | Best fallback if latency testing favors Johannesburg enough to justify extra operations. |

Official references: [Render free-instance behavior](https://render.com/docs/free), [Render regions](https://render.com/docs/regions), [Railway pricing](https://docs.railway.com/pricing), [Railway Serverless behavior](https://docs.railway.com/deployments/serverless), [Railway regions](https://docs.railway.com/deployments/regions), [Fly.io pricing](https://fly.io/docs/about/pricing/), [Fly.io autostop/autostart](https://fly.io/docs/launch/autostop-autostart/), and [Fly.io regions](https://fly.io/docs/reference/regions/).

Before production DNS cutover, deploy the same image to Railway and Fly.io trial environments and measure Ghana client latency, cold/warm API response, build time, and peak memory. Change the recommendation only from those measurements.

## Phases and stopping points

Every phase ends with a descriptive commit only after its tests pass. The Streamlit production URL remains the rollback target through Phase 7.

| Phase | Deliverable and tests | Estimate | Safe stopping point |
|---|---|---:|---|
| 0. Baseline | Build deterministic baseline JSON, direct-function snapshots, database hashes, and failing-first parity test harness. | 0.5-1 day | Streamlit remains unchanged and live; baseline documents current truth. |
| 1. Backend API | FastAPI shell, schemas, auth cookie/lockout/rate limits, data loader, Overview and health endpoints, backend unit/security tests and OpenAPI. | 1.5-2.5 days | Streamlit remains production; API can be exercised privately and compared with baseline. |
| 2. Frontend shell | Next.js public/protected layouts, fixed landing/login, auth redirects, light/dark themes, Inter, sidebar/hamburger, reduced motion, responsive shell, Playwright auth/navigation tests. | 2-3 days | New frontend is a working preview with authentication but no business cutover. |
| 3. Overview and filters | Shared URL filters, KPI cards, Recharts charts, loading/empty/error states, exact display parity and mobile tests. | 1-1.5 days | New preview provides a trustworthy Overview; remaining links can show “migration in progress.” |
| 4. Investigate and tables | Three-level warranty drill-down, breadcrumbs, server sorting/paging, full CSV/PDF exports, download-byte/data parity tests. | 1-2 days | Overview + investigation are complete; Streamlit serves all other production features. |
| 5. Ask and Management Brief | Grounded Ask flow, reviewed fallback, evidence/guardrails, rate limit, chat resilience, brief sections and Markdown/PDF exports; failed-AI tests. | 2-3 days | New preview contains the full decision workflow except Data Quality. |
| 6. Data Quality | Summary cards, checks table, expanders/details, cleaning log, CSV/PDF, empty/failure states and parity tests. | 0.5-1 day | Feature parity is complete in preview; Streamlit is still production. |
| 7. Docker and deployment | Multi-stage image, Railway staging/production, Vercel preview, same-origin rewrite, headers, secrets, health checks, Playwright desktop/mobile smoke, load/cold-start measurements. | 1-2 days | Both apps are deployed; old production DNS still points to Streamlit/Worker. |
| 8. Cutover and docs | Explicit approval gate, DNS switch, monitoring, rollback rehearsal, move Streamlit to `legacy/streamlit_app/`, update docs/rules/submission. | 0.5-1 day | New app is production; tagged old deployment and DNS rollback remain available. |

Expected total: roughly 10-16 focused development days, depending mainly on exact visual parity, authentication proxy behavior, and AI/PDF integration testing. Compressing this into a few days is possible only by reducing visual parity or test coverage, which is not recommended.

## DNS cutover and rollback

Preparation:

1. Deploy frontend to its Vercel project and API to Railway without changing `autobusiness.goflarbi.com`.
2. Test through Vercel's preview hostname, including external `/api/*` rewrites. Vercel documents external-origin rewrites as a reverse-proxy feature: [Vercel rewrites](https://vercel.com/docs/routing/rewrites).
3. Add `autobusiness.goflarbi.com` to Vercel and copy the project-specific CNAME value Vercel displays; do not assume a generic target. Vercel's current guide says subdomains use a project-specific CNAME: [Vercel custom domains](https://vercel.com/docs/domains/working-with-domains/add-a-domain).
4. Record the current Cloudflare Worker route/DNS target and export the current DNS record. Lower TTL in advance where editable.
5. Keep the Streamlit deployment and Worker configuration intact under a temporary fallback URL.

Cutover:

1. In Cloudflare, replace the `autobusiness` Worker/DNS routing with the Vercel CNAME shown for this project.
2. Set the record to **DNS Only** (grey cloud), matching the portfolio approach, so Vercel owns TLS/routing without a second CDN proxy. Cloudflare explains that DNS-only resolves directly and does not proxy HTTP traffic: [Cloudflare proxy status](https://developers.cloudflare.com/dns/proxy-status/).
3. Verify DNS, Vercel certificate, landing/login, cookie flags, protected direct URLs, all five pages, API health, exports, AI fallback, mobile widths, and parity values.
4. Monitor Vercel and Railway errors/latency for at least one full business day before moving files to `legacy/`.

Rollback:

1. Restore the recorded Cloudflare Worker route or previous DNS record.
2. Keep the old Streamlit app deployed and unchanged until rollback TTL has passed and the new app has been stable for the agreed observation period.
3. Invalidate/revoke new sessions if the rollback is security-related.
4. Tag the failed frontend/backend releases and preserve logs; do not rewrite production data because the DuckDB image is read-only.

## Required automated and manual checks

- Backend pytest: schemas, filters, exact metrics, auth timing behavior, lockout, cookie flags, rate limits, CSRF/origin, SQL allowlist, cache invalidation, empty data, and API-baseline parity.
- Frontend/Playwright: signed-out landing/login only; protected direct URL redirect; login/logout; shared filters across pages; Overview values/charts; full drill-down; table sort/page; CSV download; Ask reviewed question and AI-down fallback; Management Brief Markdown/PDF; Data Quality; light/dark; reduced motion; 375/768/1280 widths.
- Security: no Gemini/session secret in browser chunks, cookies inaccessible to JavaScript, disallowed origin blocked, generated SQL rejected when unsafe, response security headers present.
- Performance: production-build bundle report, Lighthouse on landing/Overview/mobile, cached/uncached API timing, Docker cold start, memory under baseline/full-filter/table export load.
- Parity: every number and table baseline passes before cutover. Screenshots alone are not parity evidence.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Existing auth is Streamlit-session coupled. | Extract only the framework-neutral credential operation; preserve Streamlit wrappers and tests until cutover. Add backend state tests before enabling cookie auth. |
| In-memory lockout/cache/report state diverges with multiple workers. | Run one worker/replica initially; require Redis before scaling horizontally. |
| DuckDB/Pandas memory exceeds a low-cost container. | Load-test the full table bundle, use one worker, bounded caches, streamed exports, and choose at least 1 GB RAM if measurements require it. |
| Railway Serverless cold boot or 502 harms first visit. | Disable Serverless for production and use a readiness health check. |
| External Vercel rewrite does not preserve `Set-Cookie` as expected. | Make this a Phase 2 acceptance test before building protected pages; fall back to a Next.js route handler/BFF that forwards auth and rewrites cookies explicitly. |
| AI latency exceeds proxy/host timeouts. | Keep deterministic fallback, backend timeouts/retries, nonblocking UI, and report clear grounded fallback instead of raw errors. |
| Management Brief AI output is nondeterministic, complicating export. | Generate once, cache by authenticated report ID, and export that exact artifact. Compare numeric evidence rather than prose in parity. |
| Recharts formatting differs from Plotly. | Compare source records and displayed labels; centralize formatters; retain chart type, order, axes and values. |
| Current modules import Streamlit even when used server-side. | Use thin adapters and keep Streamlit installed in the backend image initially if required. Remove that dependency only in a separately approved cleanup after parity. |
| Data Quality currently reports a friendly missing-log state despite a generated cleaning log/table existing. | Resolve expected parity in the open questions before implementing that endpoint. |
| Moving files early breaks the live Streamlit deployment. | No move before explicit Phase 8 approval; test cutover from a release tag and keep rollback deployment. |

## Open questions requiring approval

1. Approve Recharts, or prefer ECharts despite the larger/general-purpose runtime?
2. Approve Railway Hobby in Amsterdam with Serverless disabled as the initial API host, with Fly.io Johannesburg tested as the latency fallback?
3. Approve `fpdf2` for backend PDF parity, rather than introducing Chromium/HTML-to-PDF?
4. Should the tracked `docs/.agent/rules/project-rules.md` be updated after approval, or should it be moved/copied to the requested root `.agent/rules/project-rules.md`? The plan recommends updating the existing tracked file and avoiding duplicate rule sources.
5. May Phase 1 refactor `src/auth/auth.py` into a framework-neutral credential core plus unchanged Streamlit wrappers? The verification behavior and tests will remain identical; directly using `st.session_state` in FastAPI is not safe.
6. For Data Quality, should the new app reproduce today's “No cleaning log file found” state exactly, or show the existing `cleaning_log` DuckDB table / `docs/cleaning_log.csv`? The latter is more useful but is a visible behavior correction rather than strict parity.
7. Is the absent insight registry intentionally out of scope, or should a separately approved `src/analytics/insights.py` implementation happen before migration?
8. What observation window is required before Phase 8 moves Streamlit into `legacy/`—one business day, three days, or one week?

## Documentation changes at approval and cutover

After this plan is approved:

- Update `docs/.agent/rules/project-rules.md` once, replacing the Streamlit-only stack restriction with the approved parallel FastAPI/Next.js migration while preserving evidence, metric, data-cleaning, mobile, testing, and planning rules.
- Update `README.md` progressively with local setup, dual-app status, API/frontend deployment, authentication/secrets, testing and final URLs.
- Update `docs/architecture.md` first to a transitional dual-stack diagram, then to the production diagram after cutover. Keep the legacy Streamlit path visible as rollback until Phase 8 completes.
- Add one line to Assignment 4a: “Migrated the presentation and access layers from Streamlit to a Next.js frontend and FastAPI API while retaining the tested Python analytics, AI guardrails, DuckDB data pipeline, and exact metric parity.”
- Update deployment/test logs with baseline hashes, parity results, host measurements, DNS change time, smoke-test results, and rollback verification.

## Approval gate

No application code, dependency, rule-file, deployment, DNS, or folder move should occur until this plan and the open questions are approved. The first implementation action after approval is Phase 0 baseline capture—not framework scaffolding.
