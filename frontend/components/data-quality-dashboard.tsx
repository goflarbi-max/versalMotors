"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { InvestigateTable, TableColumn } from "@/components/investigate-table";
import { CleaningLogPage, formatCount, formatQualityPercent, getQualityData, QualityCheck, QualitySummary } from "@/lib/data-quality";
import { PageResult, SortDirection } from "@/lib/investigate";

const checkColumns: TableColumn<QualityCheck>[] = [
  { key: "table", label: "Table" }, { key: "issue", label: "Issue" },
  { key: "count", label: "Count", format: formatCount }, { key: "total_rows", label: "Total rows", format: formatCount },
  { key: "share_pct", label: "Share of table", format: formatQualityPercent }, { key: "impact", label: "Which conclusions it might affect" },
];
const cards = [
  ["Issues Found", "issues_found", "Validation checks requiring visibility"],
  ["Tables Affected", "tables_affected", "Source tables represented in the checks"],
  ["Total Affected", "total_affected", "Sum of affected rows across all checks"],
  ["Highest Share", "highest_share", "Largest affected share within one table"],
] as const;

function queryPage(params: URLSearchParams, prefix: string) {
  const page = Math.max(1, Number(params.get(`${prefix}_page`) ?? "1") || 1);
  const rawSize = Number(params.get(`${prefix}_size`) ?? "10");
  const pageSize = [10, 25, 50].includes(rawSize) ? rawSize : 10;
  const sortBy = params.get(`${prefix}_sort`) ?? "";
  const value = params.get(`${prefix}_dir`) ?? "original";
  const sortDir = (["original", "asc", "desc"].includes(value) ? value : "original") as SortDirection;
  return { page, pageSize, sortBy, sortDir };
}

export function DataQualityDashboard() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const checkState = queryPage(searchParams, "quality");
  const logState = queryPage(searchParams, "log");
  const [summary, setSummary] = useState<QualitySummary | null>(null);
  const [checks, setChecks] = useState<PageResult<QualityCheck> | null>(null);
  const [details, setDetails] = useState<QualityCheck[]>([]);
  const [log, setLog] = useState<CleaningLogPage | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const requestKey = useMemo(() => {
    const check = new URLSearchParams({ page: String(checkState.page), page_size: String(checkState.pageSize), sort_dir: checkState.sortDir });
    if (checkState.sortBy) check.set("sort_by", checkState.sortBy);
    const clean = new URLSearchParams({ page: String(logState.page), page_size: String(logState.pageSize), sort_dir: logState.sortDir });
    if (logState.sortBy) clean.set("sort_by", logState.sortBy);
    return { checks: `/api/v1/data-quality/checks?${check}`, log: `/api/v1/data-quality/cleaning-log?${clean}` };
  }, [checkState.page, checkState.pageSize, checkState.sortBy, checkState.sortDir, logState.page, logState.pageSize, logState.sortBy, logState.sortDir]);

  useEffect(() => {
    const controller = new AbortController();
    Promise.all([
      getQualityData<QualitySummary>("/api/v1/data-quality/summary", controller.signal),
      getQualityData<PageResult<QualityCheck>>(requestKey.checks, controller.signal),
      getQualityData<PageResult<QualityCheck>>("/api/v1/data-quality/checks?page=1&page_size=25&sort_by=share_pct&sort_dir=desc", controller.signal),
      getQualityData<CleaningLogPage>(requestKey.log, controller.signal),
    ]).then(([nextSummary, nextChecks, highImpact, nextLog]) => {
      setSummary(nextSummary); setChecks(nextChecks); setDetails(highImpact.records); setLog(nextLog); setError(""); setLoading(false);
    }).catch((reason: unknown) => {
      if (!(reason instanceof DOMException && reason.name === "AbortError")) { setError("Data Quality is temporarily unavailable. Please try again."); setLoading(false); }
    });
    return () => controller.abort();
  }, [requestKey]);

  function navigate(prefix: string, updates: Record<string, string | null>) {
    const params = new URLSearchParams(searchParams.toString());
    for (const [key, value] of Object.entries(updates)) {
      const name = `${prefix}_${key}`;
      if (value === null) params.delete(name); else params.set(name, value);
    }
    router.push(`${pathname}?${params}`, { scroll: false });
  }
  function sort(prefix: string, key: string, direction: SortDirection) {
    navigate(prefix, { page: "1", sort: direction === "original" ? null : key, dir: direction === "original" ? null : direction });
  }

  if (loading) return <div className="quality-loading" aria-label="Loading Data Quality"/>;
  if (error || !summary || !checks || !log) return <section className="quality-state error" role="alert"><h2>We could not load Data Quality</h2><p>{error || "Please try again."}</p></section>;
  if (!summary.issues_found) return <section className="quality-state"><h2>No issues found</h2><p>All current validation checks passed.</p></section>;

  const values: Record<string, string> = {
    issues_found: formatCount(summary.issues_found), tables_affected: formatCount(summary.tables_affected),
    total_affected: formatCount(summary.total_affected), highest_share: `${summary.highest_share.toFixed(1)}%`,
  };
  return <>
    <section className="quality-summary-grid" aria-label="Data Quality summary">
      {cards.map(([label, key, caption]) => <article className="quality-summary-card" key={key}><span>{label}</span><strong>{values[key]}</strong><p>{caption}</p>{key === "highest_share" && summary.highest_share_table ? <small>Highest affected table: {summary.highest_share_table}</small> : null}</article>)}
    </section>
    <section className="quality-section"><div className="quality-heading"><div><h2>Validation Checks</h2><p>Every check remains visible; downloads contain all {checks.total.toLocaleString("en-US")} checks.</p></div><div className="quality-downloads"><a href="/api/v1/data-quality/checks.csv" download>Download CSV</a><a href="/api/v1/data-quality/checks.pdf" download>Download PDF</a></div></div>
      <InvestigateTable caption="Validation checks" columns={checkColumns} result={checks} onPage={(value) => navigate("quality", { page: String(value) })} onPageSize={(value) => navigate("quality", { size: String(value), page: "1" })} onSort={(key, direction) => sort("quality", key, direction)}/>
      <div className="quality-details"><h3>Highest-impact checks</h3><p>Detailed context for the 25 checks with the largest affected share.</p>{details.map((item, index) => <details key={`${item.table}-${item.issue}-${index}`}><summary>{item.table} — {item.issue} — {item.count.toLocaleString("en-US")} rows ({item.share_pct.toFixed(2)}%)</summary><div><dl><dt>Count</dt><dd>{item.count.toLocaleString("en-US")}</dd><dt>Share</dt><dd>{item.share_pct.toFixed(2)}%</dd><dt>Total rows</dt><dd>{item.total_rows.toLocaleString("en-US")}</dd></dl><div><progress aria-label={`${item.table} affected share`} max="100" value={item.share_pct}>{item.share_pct.toFixed(2)}%</progress><p><strong>Impact:</strong> {item.impact}</p></div></div></details>)}</div>
    </section>
    <section className="quality-section"><div className="quality-heading"><div><h2>Cleaning Log (Raw)</h2></div></div><div className="quality-log-empty">No cleaning log file found - showing live checks only (acceptable).</div></section>
  </>;
}
