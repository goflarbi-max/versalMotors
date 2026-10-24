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

## Vercel frontend

Create a Vercel project from the same repository with Root Directory set to `frontend`. Configure `API_ORIGIN` as the HTTPS Railway service origin in Preview and Production environments. `next.config.ts` proxies browser `/api/*` requests to that origin, so cookies and application requests remain same-origin. It also applies CSP, HSTS, frame denial, referrer, permissions, and MIME-sniffing headers.

Do not add `NEXT_PUBLIC_` to `API_ORIGIN`; it is server-only. Environment changes apply only to new Vercel deployments, so redeploy after updating it.

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

## Rollback boundary

Phase 7 creates preview/staging deployments only. Do not change Cloudflare DNS, attach `autobusiness.goflarbi.com` to Vercel, remove the Worker, stop Streamlit, or move Streamlit files. If staging fails, roll Railway/Vercel back to their prior deployment and leave production unchanged.
