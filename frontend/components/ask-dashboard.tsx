"use client";

import { FormEvent, useEffect, useState } from "react";
import { EvidenceTable } from "@/components/evidence-table";
import { ApiEnvelope } from "@/lib/overview";
import { protectedPost } from "@/lib/mutations";

type Summary = { values: Record<string, number>; display: Record<string, string> };
type Suggestion = { label: string; question: string };
type Evidence = { id: string; type: string; statement: string; value: Record<string, unknown>; source_table: string };
type Answer = { status: string; mode: string; answer: string; facts: string | null; interpretation: string | null; recommendations: string[]; evidence: Evidence[]; table: Record<string, unknown>[] };
type Message = { question: string; result: Answer };

const cards = [
  ["Revenue", "revenue", "Completed-sale revenue", "revenue"],
  ["Completed sales", "completed_sales", "Valid completed transactions", "sales"],
  ["Branches", "branches", "Branches represented in the data", "branches"],
  ["Available over 90 days", "available_over_90_days", "Available inventory aged beyond 90 days", "inventory"],
] as const;

function SummaryIcon({ name }: { name: string }) {
  const common = { fill: "none", stroke: "currentColor", strokeWidth: 1.8, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };
  return <svg viewBox="0 0 24 24" aria-hidden="true" {...common}>
    {name === "revenue" ? <><rect x="3" y="6" width="18" height="12" rx="2"/><path d="M7 10h.01M17 14h.01M9 12h6"/></> : null}
    {name === "sales" ? <><path d="M5 12l4 4L19 6"/><path d="M4 4h16v16H4z"/></> : null}
    {name === "branches" ? <><circle cx="12" cy="6" r="2"/><circle cx="6" cy="17" r="2"/><circle cx="18" cy="17" r="2"/><path d="M12 8v4M6 15v-3h12v3"/></> : null}
    {name === "inventory" ? <><path d="M4 8h16v11H4zM3 5h18v3H3zM9 12h6"/></> : null}
  </svg>;
}

async function getData<T>(path: string, signal: AbortSignal): Promise<T> {
  const response = await fetch(path, { credentials: "include", signal });
  if (!response.ok) throw new Error("Ask the Business is temporarily unavailable.");
  return (await response.json() as ApiEnvelope<T>).data;
}

export function AskDashboard() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();
    Promise.all([getData<Summary>("/api/v1/ask/summary", controller.signal), getData<Suggestion[]>("/api/v1/ask/suggestions", controller.signal)])
      .then(([nextSummary, nextSuggestions]) => { setSummary(nextSummary); setSuggestions(nextSuggestions); setLoading(false); })
      .catch((reason: unknown) => { if (!(reason instanceof DOMException && reason.name === "AbortError")) { setError("Ask the Business is temporarily unavailable."); setLoading(false); } });
    return () => controller.abort();
  }, []);

  async function ask(value: string) {
    const trimmed = value.trim();
    if (!trimmed || pending) return;
    setPending(true); setError("");
    try {
      const result = await protectedPost<Answer>("/api/v1/ask/questions", { question: trimmed });
      setMessages((current) => [...current, { question: trimmed, result }]);
      setQuestion("");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The question could not be answered safely.");
    } finally { setPending(false); }
  }

  function submit(event: FormEvent) { event.preventDefault(); void ask(question); }

  if (loading) return <div className="ask-loading" aria-label="Loading Ask the Business"/>;
  if (!summary) return <section className="ask-state error" role="alert"><h2>Ask the Business is unavailable</h2><p>{error || "Please try again."}</p></section>;

  return <>
    <section className="ask-summary-grid" aria-label="Business summary">
      {cards.map(([label, key, caption, icon]) => <article className="ask-summary-card" key={key}><span className="summary-icon"><SummaryIcon name={icon}/></span><div><span>{label}</span><strong>{summary.display[key]}</strong><p>{caption}</p></div></article>)}
    </section>
    <section className="ask-workspace">
      <div className="ask-toolbar"><div><h2>Ask</h2><p>Quick questions</p></div>{messages.length ? <button type="button" onClick={() => { setMessages([]); setError(""); }}>Clear chat</button> : null}</div>
      <div className="suggestion-row">{suggestions.map((item) => <button type="button" key={item.label} disabled={pending} onClick={() => void ask(item.question)}>{item.label}</button>)}</div>
      <div className="conversation" aria-live="polite">
        {!messages.length ? <p className="conversation-empty">Ask a question or choose a reviewed prompt. Every numeric answer is checked against evidence.</p> : messages.map((message, index) => <article className="exchange" key={`${message.question}-${index}`}>
          <div className="user-question"><span aria-hidden="true">?</span><p>{message.question}</p></div>
          <div className="assistant-answer"><span aria-hidden="true">V</span><div>
            {message.result.mode === "deterministic" ? <p className="fallback-note">Verified data result</p> : null}
            {message.result.facts ? <section><h3>Facts</h3><p>{message.result.facts}</p></section> : <p>{message.result.answer}</p>}
            {message.result.interpretation ? <section><h3>Interpretation</h3><p>{message.result.interpretation}</p></section> : null}
            {message.result.recommendations.length ? <section><h3>Recommendations</h3><ul>{message.result.recommendations.map((item) => <li key={item}>{item}</li>)}</ul></section> : null}
          </div></div>
          {message.result.table.length ? <details className="evidence-expander"><summary>Supporting evidence ({message.result.table.length})</summary><EvidenceTable records={message.result.table} caption={`Evidence for: ${message.question}`}/></details> : null}
        </article>)}
      </div>
      <form className="ask-form" onSubmit={submit}><label className="sr-only" htmlFor="business-question">Ask about the business</label><input id="business-question" value={question} maxLength={500} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask about revenue, branches, inventory, or complaints" disabled={pending}/><button type="submit" disabled={pending || !question.trim()} aria-label="Send question">{pending ? "..." : <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 19V5m-6 6 6-6 6 6"/></svg>}</button></form>
      {error ? <p className="ask-error" role="alert">{error}</p> : null}
    </section>
  </>;
}
