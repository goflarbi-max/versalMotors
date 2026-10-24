"""Management Brief adapter over the existing KPI, evidence, and AI functions."""

from __future__ import annotations

from datetime import date
from typing import Any

from backend.app.core.report_store import ReportStore
from backend.app.services.serialization import frame_records, json_value
from src.ai.brief import build_evidence, generate_brief_sections, get_kpis_for_period
from src.database.connection import close_connection
from src.ui.pdf_exports import text_to_pdf

SECTION_ORDER = (
    ("executive_summary", "Executive Summary"),
    ("key_findings", "Key Findings"),
    ("areas_attention", "Areas Requiring Attention"),
    ("opportunities", "Opportunities"),
    ("recommended_actions", "Recommended Actions"),
    ("questions", "Questions Requiring Further Investigation"),
)


def _evidence_record(item: dict[str, Any], start_date: str, end_date: str) -> dict[str, Any]:
    source_table = "inventory" if item["id"] == "EV-006" else "sales"
    return {
        "id": item["id"],
        "type": "fact",
        "label": item["label"],
        "statement": f"{item['label']} = {item['value']}",
        "value": item["value"],
        "number": json_value(item["number"]),
        "comparison": None,
        "filters": {"start_date": start_date, "end_date": end_date},
        "source_table": source_table,
        "data": frame_records(item["df"]),
    }


def _markdown(start_date: str, end_date: str, sections: dict[str, str], evidence: list[dict]) -> str:
    lines = [f"# Management Brief {start_date} to {end_date}", ""]
    if sections.get("raw"):
        lines.extend([sections["raw"].strip(), ""])
    else:
        for key, heading in SECTION_ORDER:
            value = sections.get(key, "").strip()
            if value:
                lines.extend([f"## {heading}", value, ""])
    lines.extend(["## Supporting Evidence", "", "| Evidence ID | Description | Value |", "|---|---|---|"])
    for item in evidence:
        label = str(item["label"]).replace("|", "\\|").replace("\n", " ")
        value = str(item["value"]).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {item['id']} | {label} | {value} |")
    return "\n".join(lines).rstrip() + "\n"


def generate(start_date: date, end_date: date, store: ReportStore) -> dict[str, Any]:
    start, end = start_date.isoformat(), end_date.isoformat()
    try:
        kpis = get_kpis_for_period(start, end)
    finally:
        close_connection()
    source_evidence = build_evidence(kpis, start, end)
    brief = generate_brief_sections(kpis, source_evidence, start, end)
    sections = {
        key: str(value)
        for key, value in brief.items()
        if key in {"raw", *(item[0] for item in SECTION_ORDER)} and value
    }
    evidence = [_evidence_record(item, start, end) for item in source_evidence]
    markdown = _markdown(start, end, sections, evidence).encode("utf-8")
    pdf = text_to_pdf(f"VersalMotors management brief: {start} to {end}", markdown.decode("utf-8"))
    report_id = store.create(markdown, pdf)
    return {
        "report_id": report_id,
        "start_date": start,
        "end_date": end,
        "sections": sections,
        "evidence": evidence,
    }
