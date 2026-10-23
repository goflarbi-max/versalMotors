# VersalMotors API (Phase 1)

This FastAPI service is a parallel, read-only adapter over the existing VersalMotors
analytics layer. The Streamlit application remains the live application during the
migration.

Install and run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
```

The OpenAPI document is available at `/openapi.json` and the interactive documentation
at `/docs`. Obtain a CSRF token from `GET /api/v1/auth/csrf` before posting to the login
or logout endpoints. All Overview endpoints require the signed session cookie.

Production must set `VERSALMOTORS_SESSION_SECRET`, `VERSALMOTORS_AUTH_USERS_JSON`, and
`VERSALMOTORS_ALLOWED_ORIGINS`. Keep secure cookies enabled outside explicit local HTTP
development.
