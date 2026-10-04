# Day 3 Audit Report

This report outlines the findings from an end-to-end audit of the Day 3 work (Ask the Business, Management Brief, Data Quality page, Guardrails, AI Tools). Findings are ranked by severity.

## 1. Critical Severity

### 1.1 Hard-coded API Key (Security)
**Location:** `pages/ask_the_business.py` (Line 62)
**Issue:** The Gemini API key is hard-coded into the source code (`key = "AQ.Ab8RN6ICP..."`).
**Why it matters:** If committed, the secret is exposed. This is a severe security violation.
**Proposed Fix:** Remove the hard-coded key immediately. Rely solely on `.env` (via `python-dotenv`) or `st.secrets`.

### 1.2 Unsafe AI SQL Execution (Security)
**Location:** `pages/ask_the_business.py` (Line 206)
**Issue:** User questions are directly translated into SQL by AI and executed against the database `con.execute(sql_query).fetchdf()` without validation.
**Why it matters:** Although the connection is opened as `read_only=True`, DuckDB still allows querying the host filesystem using functions like `read_csv()`. A prompt injection can extract sensitive files from the server.
**Proposed Fix:** Implement the `run_readonly_sql` wrapper mentioned in the requirements. Enforce an allowlist of permitted tables, block functions like `read_csv` and `ATTACH`, and apply row limits and timeouts.

### 1.3 Unclosed Database Connections
**Location:** `pages/ask_the_business.py`, `pages/data_quality.py`, `src/ai/brief.py`
**Issue:** `duckdb.connect(DB_PATH, read_only=True)` is called but the connections are never closed.
**Why it matters:** Streamlit's rerun execution model will open a new connection on every interaction, leading to file locking issues, memory leaks, and application crashes.
**Proposed Fix:** Create a central connection helper function in `src/database/` that manages connections safely, preferably using `st.cache_resource` or `with duckdb.connect(...) as con:` blocks.

### 1.4 Fake Fact Verification (Grounding)
**Location:** `src/ai/guardrails.py` (Line 65)
**Issue:** `verify_facts_against_evidence` is just a placeholder returning `True`.
**Why it matters:** The system does not actually verify if the AI's claims are grounded in evidence, violating the core requirement "Evidence Before Claims".
**Proposed Fix:** Implement logic to extract numbers from the AI response and check if they exist in the evidence object.

## 2. High Severity

### 2.1 Duplicate Metric Calculations (Consistency)
**Location:** `src/ai/brief.py` and `pages/ask_the_business.py`
**Issue:** Both files write raw SQL to compute metrics like revenue, sales, and branch performance instead of importing from `src/analytics/metrics.py`.
**Why it matters:** If the definition of a metric (e.g., revenue) changes, it must be updated in multiple places. Currently, `ask_the_business.py` attempts to guess the revenue column dynamically, which can lead to double counting or using list price instead of selling price.
**Proposed Fix:** Refactor to use a single source of truth for business metrics in `src/analytics/metrics.py`.

### 2.2 Broken SQL in Evidence
**Location:** `src/ai/brief.py` (Line 95)
**Issue:** Evidence `EV-003` contains fundamentally broken SQL: `SELECT SUM(rev_col)/COUNT(*) FROM sales WHERE date BETWEEN range`.
**Why it matters:** It will fail immediately if a user tries to run it, breaking the "drill-down/evidence" requirement.
**Proposed Fix:** Correct the SQL string formatting to use the actual parameters (e.g., `kpis['rev_col']`, `start_date`, `end_date`).

### 2.3 Bare Exceptions Swallowing Errors
**Location:** `pages/ask_the_business.py` (Line 60, 82, 117, 230), `src/ai/brief.py` (Line 161)
**Issue:** Multiple bare `except:` blocks that simply `pass`.
**Why it matters:** Hard-to-diagnose bugs will be hidden (e.g., schema parsing errors, chart rendering crashes).
**Proposed Fix:** Catch specific exceptions (e.g., `duckdb.Error`, `KeyError`) and log or handle them properly.

### 2.4 Missing Dependency
**Location:** `requirements.txt`
**Issue:** `python-dotenv` is imported in `app.py` and `ask_the_business.py` but is missing from `requirements.txt`.
**Why it matters:** The app will crash when deployed to a fresh environment.
**Proposed Fix:** Add `python-dotenv` to `requirements.txt`.

## 3. Medium Severity

### 3.1 Hard-coded AI Models
**Location:** `pages/ask_the_business.py`
**Issue:** Model names (`gemini-2.0-flash` and `gemini-3.5-flash-lite`) are hard-coded in the view layer.
**Why it matters:** It makes updating models difficult across the app and is inconsistent with best practices.
**Proposed Fix:** Move model configuration to `src/config.py`.

### 3.2 Evidence Object Structure Missing Fields
**Location:** `src/ai/brief.py`
**Issue:** The evidence dictionaries lack several required fields: `type`, `statement`, `comparison_value`, `change_pct`, `filters`, `source_tables`, `severity_score`.
**Why it matters:** Violates the insight engine specification.
**Proposed Fix:** Update the `build_evidence` function to construct complete evidence objects.

### 3.3 Prompt Injection Protection is Weak
**Location:** `src/ai/guardrails.py`
**Issue:** Injection protection relies on simple substrings like "ignore your instructions".
**Why it matters:** Easily bypassed. Text inside user input can override system prompts.
**Proposed Fix:** Upgrade prompt structure with XML tags, strictly separate user input from instructions, and use a stronger LLM-based evaluation or comprehensive regex blocklist.

## 4. Low Severity

### 4.1 Missing Error Handling/Timeouts
**Location:** `src/ai/gemini_client.py` and `ask_the_business.py`
**Issue:** No retries, timeouts, or rate-limit handling for Gemini API calls.
**Why it matters:** Network issues will crash the request instead of failing gracefully or retrying.
**Proposed Fix:** Add a retry decorator (e.g., using `tenacity`).

### 4.2 Duplicate Imports
**Location:** `pages/ask_the_business.py` (Lines 172-173)
**Issue:** `validate_question`, `handle_unanswerable`, and `check_api_key` are imported twice.
**Why it matters:** Poor code health.
**Proposed Fix:** Clean up imports.

---

## Fix Order

1. **Remove the hard-coded API key:** Fix immediately in `ask_the_business.py`.
2. **Implement safe DB Connections:** Centralize DuckDB connections with a context manager or `st.cache_resource` to stop file locking crashes.
3. **Secure AI SQL Execution:** Implement `run_readonly_sql` with strict validation to prevent filesystem read exploits.
4. **Fix Broken SQL in Brief:** Fix `EV-003` so drill-downs work.
5. **Add missing dependencies:** Put `python-dotenv` into `requirements.txt`.
6. **Consolidate Metrics:** Use `src/analytics/metrics.py` instead of raw SQL queries inside AI files.
7. **Fix Guardrails:** Implement real fact-checking instead of the `True` stub.

## Questions for Approval
- Do you want me to create `src/database/connection.py` to act as the single shared DuckDB connection manager for the entire application?
- Should I implement `run_readonly_sql` directly inside `guardrails.py`, or does it belong in `src/database/`?
- Should we switch to parameterized queries for the metrics calculation, or keep string concatenation but tightly sanitize the inputs?
