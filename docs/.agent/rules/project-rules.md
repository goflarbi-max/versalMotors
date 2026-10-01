---
trigger: always_on
---

# Project Rules
- Stack: Python, Pandas, DuckDB, Streamlit, Plotly. Do not add new frameworks without asking.
- All business metrics live in src/analytics/metrics.py. UI code never calculates metrics.
- The AI layer must never compute numbers or invent facts. It receives evidence objects and tool results only.
- Never silently modify data. Every cleaning action is logged in the cleaning log with the reason and row count.
- Every insight must be an evidence object with: id, type (fact|interpretation|recommendation), value, comparison, filters, source table.
- Every metric needs a unit test with a manually verified expected value.
- Mobile-first layouts. Test at 375px, 768px, 1280px widths.
- Commit messages must be descriptive (e.g. "Add data cleaning pipeline"), never "update" or "fix".
- Before large changes, propose a plan and wait for approval.
- The full project brief is in docs/project_brief.md. Refer to it when in doubt.