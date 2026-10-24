# Phase 7 Deployment Runbook

Phase 7 prepares and verifies the parallel FastAPI and Next.js stack. It does **not** change `autobusiness.goflarbi.com`; the existing Streamlit deployment remains the production and rollback target until Phase 8 is explicitly approved.

## Backend image

The root `Dockerfile` is a reproducible multi-stage build. The builder installs the exact versions in `backend/requirements.lock`, runs the unchanged `scripts/build_database.py`, and rejects the image if the generated DuckDB row counts or SHA-256 differ from `tests/parity_baseline.json`. The runtime contains only the API, required Python source, cleaning-log artifact, and verified DuckDB file. It runs as UID/GID 10001, uses one Uvicorn worker, and opens DuckDB read-only through the existing loader.

Build and test locally when Docker is available:

```powershell
docker build --tag versalmotors-api:phase7 .
docker run --rm --read-only --tmpfs /tmp -p 8000:8000 `
  -e VERSALMOTORS_SESSION_SECRET="replace-with-a-long-random-value" `
  -e VERSALMOTORS_AUTH_USERS_JSON='{"demo@versalmotors.com":"<bcrypt-hash>"}' `
  -e VERSALMOTORS_ALLOWED_ORIGINS="http://localhost:3000" `
  versalmotors-api:phase7
```

Never put secrets in the Dockerfile, repository, build arguments, logs, or frontend environment.

## Railway API

The current Railway platform uses `.railway/railway.ts`. Link the repository and apply that configuration to a **staging** environment first. Confirm in the Railway dashboard that the service uses the root Dockerfile, one Amsterdam (`europe-west4`) replica, Serverless is disabled, and `/health/ready` is the deployment health check. Railway injects `PORT`; the container command listens on it.

Configure these service/shared variables in Railway:

- `VERSALMOTORS_SESSION_SECRET`: long random secret.
- `VERSALMOTORS_AUTH_USERS_JSON`: JSON object containing bcrypt hashes only.
- `VERSALMOTORS_ALLOWED_ORIGINS`: exact Vercel preview URL(s); later add the production hostname. Do not use `*` with credentialed requests.
- `VERSALMOTORS_SECURE_COOKIES=true`.
- `GEMINI_API_KEY`: optional; deterministic fallback remains available when absent.

The API logs only request ID, route path, method, duration, status, cache result, and normalized error category. It does not log query strings, request bodies, credentials, cookies, SQL, or provider keys.

### Create and deploy the Railway service

1. Push the tested Phase 7 commits to the GitHub `main` branch.
2. Sign in to Railway, select **New Project**, then **Deploy from GitHub repo**. Connect GitHub if prompted and choose `goflarbi-max/versalMotors` on `main`.
3. Open the new service's **Settings**. Confirm Railway detected the root `Dockerfile`, set the region to Amsterdam (`europe-west4`), keep one replica, and disable Serverless for the always-on production service.
4. Set the health-check path to `/health/ready` with a 300-second deployment timeout. Do not override the image command or `PORT`; Railway supplies `PORT` and the Docker command reads it.
5. In **Variables**, add the following runtime values. Paste values in the Railway dashboard, never into Git, build arguments, or frontend variables:

   ```text
   VERSALMOTORS_SESSION_SECRET=<long random value>
   VERSALMOTORS_AUTH_USERS_JSON={"demo@versalmotors.com":"<bcrypt hash>"}
   VERSALMOTORS_ALLOWED_ORIGINS=https://<vercel-preview>,https://autobusiness.goflarbi.com
   VERSALMOTORS_SECURE_COOKIES=true
   VERSALMOTORS_SESSION_HOURS=8
   GEMINI_API_KEY=<optional Google AI key>
   GEMINI_MODEL=gemini-3.8-flash
   GEMINI_FALLBACK_MODELS=gemini-3.5-flash-lite
   GEMINI_MAX_ATTEMPTS=2
   ```

   Generate the bcrypt value locally with `.\.venv\Scripts\python.exe scripts\create_user.py`; do not paste the plain password into Railway's JSON variable.
6. Review Railway's staged changes and select **Deploy**. The build must show that the root Dockerfile was detected, database verification passed, and the readiness health check succeeded.
7. In **Settings > Networking**, select **Generate Domain**. Record the resulting HTTPS `*.up.railway.app` origin; this is the server-only `API_ORIGIN` used by Vercel.
8. Verify `https://<railway-origin>/health/live` and `/health/ready` before creating the frontend deployment. The readiness response must contain the frozen database hash and expected table counts.

## Vercel frontend

Create a Vercel project from the same repository with Root Directory set to `frontend`. Configure `API_ORIGIN` as the HTTPS Railway service origin in Preview and Production environments. `next.config.ts` proxies browser `/api/*` requests to that origin, so cookies and application requests remain same-origin. It also applies CSP, HSTS, frame denial, referrer, permissions, and MIME-sniffing headers.

Do not add `NEXT_PUBLIC_` to `API_ORIGIN`; it is server-only. Environment changes apply only to new Vercel deployments, so redeploy after updating it.

### Deploy the frontend from GitHub

1. Sign in to Vercel, select **Add New > Project**, import `goflarbi-max/versalMotors`, and grant the Vercel GitHub app access if prompted.
2. Set **Framework Preset** to Next.js and **Root Directory** to `frontend`. Keep the repository's normal install and build commands.
3. Add `API_ORIGIN=https://<railway-origin>` to both **Preview** and **Production** environments. It must not be named `NEXT_PUBLIC_API_ORIGIN`, and the URL must not end in `/api`.
4. Select **Deploy**. Test the generated Vercel preview hostname before assigning the production domain. If `API_ORIGIN` changes, update it in Project Settings and redeploy; existing deployments do not inherit changed values.
5. In **Settings > Domains**, add `autobusiness.goflarbi.com`. Copy the exact DNS record target Vercel displays for this project; do not substitute a generic Vercel hostname.

### Change the Cloudflare record manually after preview approval

These are operator instructions only. This repository and its deployment scripts do not modify DNS.

1. Before editing anything, record/export the current `autobusiness` DNS record and Cloudflare Worker route so rollback is exact.
2. In Cloudflare **DNS > Records**, locate the existing `autobusiness` record. Remove any Worker route that intercepts the hostname only when the Vercel preview, Railway readiness, login, exports, and responsive smoke tests have passed.
3. Replace the old record with the type, name, and target Vercel showed—normally a `CNAME` with name `autobusiness` and Vercel's project-specific target.
4. Set **Proxy status** to **DNS only** (grey cloud) and save. Do not guess the CNAME target, and do not leave conflicting A, AAAA, or CNAME records on the same hostname.
5. Wait for DNS and Vercel certificate validation, then verify `https://autobusiness.goflarbi.com` in a private browser window.
6. If health, authentication, exports, parity, or TLS fails, immediately restore the recorded Worker route/previous DNS record. Keep Streamlit running until the agreed observation window has completed.

## Staging verification

1. Confirm `GET https://<railway>/health/live` returns `{"status":"ok"}`.
2. Confirm `GET https://<railway>/health/ready` returns `status=ready`, the baseline data version, and expected row counts.
3. Run the browser smoke suite against the Vercel preview:

   ```powershell
   $env:PLAYWRIGHT_EXTERNAL_SERVERS='1'
   $env:PLAYWRIGHT_BASE_URL='https://<vercel-preview>'
   $env:SMOKE_EMAIL='demo@versalmotors.com'
   $env:SMOKE_PASSWORD='<demo-password>'
   npm.cmd --prefix frontend run test:e2e -- --grep "deployment smoke|same-origin API proxy"
   ```

4. Measure the Railway API without printing credentials:

   ```powershell
   $env:SMOKE_EMAIL='demo@versalmotors.com'
   $env:SMOKE_PASSWORD='<demo-password>'
   .\.venv\Scripts\python.exe deployment\measure_api.py --base-url https://<railway> --requests 50 --concurrency 5
   ```

5. Record first readiness response, warm p50/p95, error count, Railway peak memory, image build duration, region, and Vercel deployment URL in `docs/test_log.md`.

6. Inspect the browser Network panel while testing. Application requests must remain on the Vercel/custom origin under `/api/*`; no request URL, request body, response, cookie, or browser bundle may contain `GEMINI_API_KEY`, `VERSALMOTORS_SESSION_SECRET`, or `VERSALMOTORS_AUTH_USERS_JSON`.
7. Search the production frontend output with a unique sentinel before release:

   ```powershell
   $env:GEMINI_API_KEY='PHASE7_AI_KEY_SENTINEL_DO_NOT_DEPLOY'
   npm.cmd --prefix frontend run build
   rg -n -i 'PHASE7_AI_KEY_SENTINEL_DO_NOT_DEPLOY|GEMINI_API_KEY|streamlit' frontend/.next
   ```

   The command must return no match. The sentinel is deliberately fake; never place a real AI key in the frontend environment, command line, or build logs.

## Rollback boundary

Phase 7 creates preview/staging deployments only. Do not change Cloudflare DNS, attach `autobusiness.goflarbi.com` to Vercel, remove the Worker, stop Streamlit, or move Streamlit files. If staging fails, roll Railway/Vercel back to their prior deployment and leave production unchanged.
