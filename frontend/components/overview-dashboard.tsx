"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import { useBusinessFilters } from "@/components/filter-provider";
import {
  ApiEnvelope, BranchRevenueRecord, formatChange, formatKpi, KpiRecord,
  ModelMarginRecord, RevenueTrendRecord,
} from "@/lib/overview";

const RevenueTrendChart = dynamic(() => import("@/components/overview-charts").then((module) => module.RevenueTrendChart), { ssr: false, loading: () => <ChartSkeleton/> });
const BranchRevenueChart = dynamic(() => import("@/components/overview-charts").then((module) => module.BranchRevenueChart), { ssr: false, loading: () => <ChartSkeleton/> });
const ModelMarginChart = dynamic(() => import("@/components/overview-charts").then((module) => module.ModelMarginChart), { ssr: false, loading: () => <ChartSkeleton/> });

type DashboardData = {
  kpis: KpiRecord[];
  trend: RevenueTrendRecord[];
  branches: BranchRevenueRecord[];
  models: ModelMarginRecord[];
};

const cardDetails: Record<string, { caption: string; icon: string }> = {
  "Revenue": { caption: "How much sales value did the selected period generate?", icon: "▣" },
  "Gross margin": { caption: "How much value remained after vehicle acquisition cost?", icon: "▤" },
  "Units sold": { caption: "How many distinct vehicles were sold?", icon: "▰" },
  "Discount rate": { caption: "How much of gross price was given up through discounts?", icon: "%" },
};

async function getData<T>(path: string, signal: AbortSignal): Promise<T> {
  const response = await fetch(path, { credentials: "include", signal });
  if (!response.ok) throw new Error("Overview data could not be loaded.");
  return (await response.json() as ApiEnvelope<T>).data;
}

function DashboardSkeleton() {
  return <div className="overview-skeleton" aria-label="Loading business overview"><div className="kpi-grid">{[0,1,2,3].map((item) => <div className="skeleton-block" key={item}/>)}</div><ChartSkeleton/><ChartSkeleton/></div>;
}
function ChartSkeleton() { return <div className="chart-skeleton" aria-hidden="true"/>; }

function ChartCard({ eyebrow, title, caption, children }: { eyebrow: string; title: string; caption: string; children: React.ReactNode }) {
  return <section className="overview-chart-card"><header><span>{eyebrow}</span><h2>{title}</h2><p>{caption}</p></header>{children}</section>;
}

export function OverviewDashboard() {
  const { query, loading: filtersLoading, error: filtersError } = useBusinessFilters();
  const [result, setResult] = useState<{ query: string; data: DashboardData | null; error: string | null }>({ query: "", data: null, error: null });

  useEffect(() => {
    if (!query) return;
    const controller = new AbortController();
    Promise.all([
      getData<KpiRecord[]>(`/api/v1/overview/kpis?${query}`, controller.signal),
      getData<RevenueTrendRecord[]>(`/api/v1/overview/revenue-trend?${query}`, controller.signal),
      getData<BranchRevenueRecord[]>(`/api/v1/overview/revenue-by-branch?${query}`, controller.signal),
      getData<ModelMarginRecord[]>(`/api/v1/overview/margin-by-model?${query}`, controller.signal),
    ]).then(([kpis, trend, branches, models]) => setResult({ query, data: { kpis, trend, branches, models }, error: null }))
      .catch((reason: unknown) => {
        if (!(reason instanceof DOMException && reason.name === "AbortError")) setResult({ query, data: null, error: "Overview data is temporarily unavailable. Please try again." });
      });
    return () => controller.abort();
  }, [query]);

  const loading = filtersLoading || !query || result.query !== query;
  const data = result.data;
  if (loading) return <DashboardSkeleton/>;
  if (filtersError || result.error || !data) return <div className="overview-state error" role="alert"><h2>We could not load the overview</h2><p>{filtersError ?? result.error ?? "Please try again."}</p><button type="button" onClick={() => location.reload()}>Try again</button></div>;
  const empty = data.kpis.length === 0 || data.kpis.every((row) => !row.value || Number.isNaN(row.value));
  if (empty) return <div className="overview-state"><h2>No records match these filters</h2><p>Broaden the date range or remove one or more filters.</p></div>;

  return <>
    <section className="kpi-grid" aria-label="Overview key performance indicators">
      {data.kpis.map((row) => {
        const detail = cardDetails[row.metric];
        const change = formatChange(row.change_rate);
        return <article className="overview-kpi" key={row.metric} data-metric={row.metric}>
          <div className="kpi-top"><span className="kpi-label">{row.metric}</span><span className="kpi-icon" aria-hidden="true">{detail?.icon}</span></div>
          <div className="kpi-value-row"><strong>{formatKpi(row.metric, row.value)}</strong>{change ? <span className={`kpi-badge ${row.change_rate! < 0 ? "down" : "up"}`}>{row.change_rate! < 0 ? "↓" : "↑"} {change.split(" vs")[0].replace(/^\+/, "")}</span> : null}</div>
          <p>{detail?.caption}</p>
          <footer>{change ? <><strong>{change.split(" vs")[0]}</strong> vs prior period</> : <span>Prior-period comparison unavailable</span>}</footer>
        </article>;
      })}
    </section>
    <ChartCard eyebrow="Performance trend" title="Revenue trend" caption="Is sales revenue rising, falling, or showing seasonal movement over time?">{data.trend.length ? <RevenueTrendChart data={data.trend}/> : <p className="chart-empty">No revenue trend is available for the selected filters.</p>}</ChartCard>
    <div className="overview-chart-grid">
      <ChartCard eyebrow="Branch performance" title="Revenue by branch" caption="Which locations contribute most to sales revenue?">{data.branches.length ? <BranchRevenueChart data={data.branches}/> : <p className="chart-empty">No branch revenue is available for the selected filters.</p>}</ChartCard>
      <ChartCard eyebrow="Model performance" title="Gross margin by model" caption="Which vehicle models contribute the most gross margin after acquisition cost?">{data.models.length ? <ModelMarginChart data={data.models}/> : <p className="chart-empty">No model margin is available for the selected filters.</p>}</ChartCard>
    </div>
  </>;
}
