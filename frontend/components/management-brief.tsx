"use client";

import { FormEvent, useState } from "react";
import { EvidenceTable } from "@/components/evidence-table";
import { protectedPost } from "@/lib/mutations";

type Evidence = { id: string; label: string; value: string; number: number; source_table: string; data: Record<string, unknown>[] };
type Brief = { report_id: string; start_date: string; end_date: string; sections: Record<string, string>; evidence: Evidence[] };
const sectionOrder = [["executive_summary", "Executive Summary"], ["key_findings", "Key Findings"], ["areas_attention", "Areas Requiring Attention"], ["opportunities", "Opportunities"], ["recommended_actions", "Recommended Actions"], ["questions", "Questions Requiring Further Investigation"]] as const;

export function ManagementBrief() {
  const [startDate, setStartDate] = useState("2024-01-01");
  const [endDate, setEndDate] = useState("2024-12-31");
  const [brief, setBrief] = useState<Brief | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");

  async function generate(event: FormEvent) {
    event.preventDefault(); setPending(true); setError("");
    try { setBrief(await protectedPost<Brief>("/api/v1/management-brief", { start_date: startDate, end_date: endDate })); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "The brief could not be generated safely."); }
    finally { setPending(false); }
  }

  const visibleSections = brief ? sectionOrder.filter(([key]) => Boolean(brief.sections[key]?.trim())) : [];
  return <div className="brief-workspace">
    <form className="brief-controls" onSubmit={generate}>
      <label>Start date<input type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} required/></label>
      <label>End date<input type="date" value={endDate} min={startDate} onChange={(event) => setEndDate(event.target.value)} required/></label>
      <button type="submit" disabled={pending}>{pending ? "Generating..." : "Generate Management Brief"}</button>
    </form>
    {error ? <p className="brief-error" role="alert">{error}</p> : null}
    {!brief && !pending ? <section className="brief-empty"><h2>Ready when you are</h2><p>Select a reporting period to generate an evidence-backed management brief.</p></section> : null}
    {pending ? <div className="brief-loading" aria-label="Generating management brief"/> : null}
    {brief ? <>
      <section className="brief-result-header"><div><span>Reporting period</span><strong>{brief.start_date} to {brief.end_date}</strong></div></section>
      <section className="brief-sections">{brief.sections.raw ? <article><h2>Management Brief</h2><p>{brief.sections.raw}</p></article> : visibleSections.map(([key, heading]) => <article key={key}><h2>{heading}</h2><p>{brief.sections[key]}</p></article>)}</section>
      <section className="brief-evidence" aria-label="Supporting evidence"><h2>Supporting Evidence</h2><EvidenceTable records={brief.evidence.map((item) => ({ "Evidence ID": item.id, Description: item.label, Value: item.value }))} caption="Management brief supporting evidence"/>{brief.evidence.map((item) => <details key={item.id}><summary>{item.id}: {item.label} = {item.value}</summary><EvidenceTable records={item.data} caption={`${item.id} ${item.label}`}/><p className="brief-trace-note">Number {item.number} traced and verified against source data</p></details>)}</section>
      <div className="brief-downloads"><a href={`/api/v1/management-brief/${brief.report_id}.md`}>Export Markdown</a><a href={`/api/v1/management-brief/${brief.report_id}.pdf`}>Export PDF</a></div>
    </> : null}
  </div>;
}
