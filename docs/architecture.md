# VersalMotors Architecture

## System flow

```text
Raw automotive CSVs
        |
        v
Profile and audited cleaning ----> Cleaning log and quality flags
        |
        v
Cleaned CSVs ----> DuckDB ----> Pure analytics metrics
                                  |
                                  v
                         Evidence and drill-downs
                                  |
                                  v
                    Streamlit management application
```

The nine source tables are preserved in `data/raw/`. The cleaning pipeline writes flagged, standardised tables to `data/cleaned/`, and `scripts/build_database.py` loads them into DuckDB. Pure functions in `src/analytics/metrics.py` define business calculations. Streamlit pages consume those results and never silently repair source data.

## Resilient Ask the Business flow

```text
Business question
      |
      v
Input guardrails
      |
      v
Gemini primary model --429/5xx/timeout--> bounded retry
      |                                      |
      |                                      v
      |                              lighter Gemini model
      |                                      |
      +----------------------+---------------+
                             |
                   unavailable or invalid SQL
                             |
                             v
                  Reviewed fallback registry
                             |
                             v
                    Read-only SQL boundary
                             |
                             v
                  Structured evidence objects
                             |
             +---------------+----------------+
             |                                |
       verified AI text              deterministic summary
             |                                |
             +---------------+----------------+
                             v
                    Evidence table and answer
```

`src/ai/gemini_client.py` owns API retry and model failover. It retries only transient failures and returns structured status without exposing provider errors. Model order and attempt limits are environment-configurable.

`src/ai/fallback.py` is the reviewed offline registry. It contains allowlisted queries for supported questions, converts tool results into fact evidence objects, and provides summaries that use only returned values. Invalid generated SQL also enters this path.

`src/database/connection.py` permits a single read-only `SELECT` or `WITH` query against approved business tables and blocks mutation, attachment, extension, and filesystem-reading operations.

`src/ai/guardrails.py` checks narrative numbers against the evidence from that request. Missing, unavailable, or unverified AI output is replaced with the deterministic response. Gemini is therefore an optional interpretation layer rather than a dependency for business facts.

## Configuration

```dotenv
GEMINI_MODEL=gemini-3.8-flash
GEMINI_FALLBACK_MODELS=gemini-3.5-flash-lite
GEMINI_MAX_ATTEMPTS=2
```

No API key is required for registered offline questions or deterministic management briefs. Secrets belong in `.env` or Streamlit secrets and are never committed.

## Failure behavior

| Condition | Result |
|---|---|
| Primary model returns `429`, `5xx`, or timeout | Retry with bounded backoff, then try the lighter model |
| API key is absent | Skip Gemini and use the reviewed fallback |
| Every model is unavailable | Show verified database evidence and a deterministic statement |
| Generated SQL is rejected | Run the reviewed fallback query through the same read-only boundary |
| AI narrative contains an unsupported number | Suppress it and show the deterministic statement |
| No reviewed route exists | Explain the supported question types without guessing |

## Testing boundary

Pure retry and fallback behavior is covered in `tests/test_ai_fallback.py`. The tests simulate `503` and `429` responses, model failover, missing credentials, rejected generated SQL, grounded evidence, and empty results. Streamlit page tests confirm that the user interface renders without uncaught exceptions.
