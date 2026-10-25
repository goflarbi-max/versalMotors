"use client";

import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { useBusinessFilters } from "@/components/filter-provider";
import { InvestigateTable, TableColumn } from "@/components/investigate-table";
import {
  BranchWarrantyRecord, formatDate, formatGhs, formatInteger, formatPercent,
  getInvestigationPage, ModelWarrantyRecord, PageResult, SortDirection, WarrantyClaimRecord,
} from "@/lib/investigate";

const modelColumns: TableColumn<ModelWarrantyRecord>[] = [
  { key: "model", label: "Model" },
  { key: "claim_count", label: "Claims", format: formatInteger },
  { key: "claim_cost", label: "Claim cost", format: formatGhs },
  { key: "previous_claim_cost", label: "Previous cost", format: formatGhs },
  { key: "cost_change", label: "Cost change", format: formatGhs },
  { key: "cost_change_rate", label: "Change rate", format: formatPercent },
];

const branchColumns: TableColumn<BranchWarrantyRecord>[] = [
  { key: "branch", label: "Branch" },
  { key: "claim_count", label: "Claims", format: formatInteger },
  { key: "claim_cost", label: "Claim cost", format: formatGhs },
  { key: "share_of_model_cost", label: "Share of model cost", format: formatPercent },
];

const claimColumns: TableColumn<WarrantyClaimRecord>[] = [
  { key: "claim_id", label: "Claim ID", format: formatInteger },
  { key: "claim_date", label: "Claim date", format: formatDate },
  { key: "failure_category", label: "Failure category" },
  { key: "claim_status", label: "Status" },
  { key: "claim_amount", label: "Claim amount", format: formatGhs },
  { key: "approved_amount", label: "Approved amount", format: formatGhs },
  { key: "manufacturer_recovery_amount", label: "Manufacturer recovery", format: formatGhs },
  { key: "claim_description", label: "Description" },
  { key: "sale_id", label: "Sale ID", format: formatInteger },
  { key: "service_id", label: "Service ID", format: formatInteger },
  { key: "inventory_id", label: "Inventory ID", format: formatInteger },
  { key: "_row_quality_status", label: "Row quality" },
];

type Result = PageResult<ModelWarrantyRecord | BranchWarrantyRecord | WarrantyClaimRecord>;

export function InvestigateDashboard() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { query, loading: filtersLoading, error: filtersError } = useBusinessFilters();
  const selectedModel = searchParams.get("focus_model") ?? "";
  const selectedBranch = searchParams.get("focus_branch") ?? "";
  const page = Math.max(1, Number(searchParams.get("table_page") ?? "1") || 1);
  const pageSize = [10,25,50].includes(Number(searchParams.get("page_size"))) ? Number(searchParams.get("page_size")) : 10;
  const sortBy = searchParams.get("sort_by") ?? "";
  const sortDir = (["original","asc","desc"].includes(searchParams.get("sort_dir") ?? "") ? searchParams.get("sort_dir") : "original") as SortDirection;
  const level = selectedModel ? (selectedBranch ? "claims" : "branches") : "models";
  const [state, setState] = useState<{ key: string; data: Result | null; error: string | null }>({ key: "", data: null, error: null });
  const [drillChoice, setDrillChoice] = useState("");

  const requestKey = useMemo(() => {
    if (!query) return "";
    const paging = new URLSearchParams({ page: String(page), page_size: String(pageSize), sort_dir: sortDir });
    if (sortBy) paging.set("sort_by", sortBy);
    const root = "/api/v1/investigate/warranty/models";
    const path = level === "models" ? root : level === "branches"
      ? `${root}/${encodeURIComponent(selectedModel)}/branches`
      : `${root}/${encodeURIComponent(selectedModel)}/branches/${encodeURIComponent(selectedBranch)}/claims`;
    return `${path}?${query}&${paging.toString()}`;
  }, [level, page, pageSize, query, selectedBranch, selectedModel, sortBy, sortDir]);

  useEffect(() => {
    if (!requestKey) return;
    const controller = new AbortController();
    getInvestigationPage<ModelWarrantyRecord | BranchWarrantyRecord | WarrantyClaimRecord>(requestKey, controller.signal)
      .then((data) => { setState({ key: requestKey, data, error: null }); setDrillChoice(""); })
      .catch((reason: unknown) => {
        if (!(reason instanceof DOMException && reason.name === "AbortError")) setState({ key: requestKey, data: null, error: "Warranty investigation is temporarily unavailable. Please try again." });
      });
    return () => controller.abort();
  }, [requestKey]);

  function navigate(updates: Record<string, string | null>) {
    const params = new URLSearchParams(searchParams.toString());
    for (const [key, value] of Object.entries(updates)) {
      if (value === null) params.delete(key);
      else params.set(key, value);
    }
    router.push(`${pathname}?${params.toString()}`, { scroll: false });
  }
  function resetTable(extra: Record<string, string | null>) {
    navigate({ table_page: "1", sort_by: null, sort_dir: null, ...extra });
  }
  function onSort(key: string, direction: SortDirection) {
    navigate({ table_page: "1", sort_by: direction === "original" ? null : key, sort_dir: direction === "original" ? null : direction });
  }

  const loading = filtersLoading || !requestKey || state.key !== requestKey;
  const result = state.data;
  const modelRecords = (result?.records ?? []) as ModelWarrantyRecord[];
  const branchRecords = (result?.records ?? []) as BranchWarrantyRecord[];
  const overviewHref = `/overview${query ? `?${query}` : ""}`;
  const exportQuery = new URLSearchParams(query);
  if (sortBy) exportQuery.set("sort_by", sortBy);
  exportQuery.set("sort_dir", sortDir);
  const exportRoot = `/api/v1/investigate/warranty/models/${encodeURIComponent(selectedModel)}/branches/${encodeURIComponent(selectedBranch)}/claims`;

  return <>
    <nav className="investigate-breadcrumbs" aria-label="Breadcrumb">
      <Link href={overviewHref}>Overview</Link><span aria-hidden="true">›</span>
      <button type="button" aria-current={level === "models" ? "page" : undefined} onClick={() => resetTable({ focus_model: null, focus_branch: null })}>Warranty cost</button>
      {selectedModel ? <><span aria-hidden="true">›</span><button type="button" aria-current={level === "branches" ? "page" : undefined} onClick={() => resetTable({ focus_branch: null })}>{selectedModel}</button></> : null}
      {selectedBranch ? <><span aria-hidden="true">›</span><span aria-current="page">{selectedBranch}</span></> : null}
    </nav>
    {loading ? <div className="investigate-loading" aria-label="Loading warranty investigation"/> : filtersError || state.error || !result ? <section className="investigate-state error" role="alert"><h2>We could not load the investigation</h2><p>{filtersError ?? state.error ?? "Please try again."}</p></section> : level === "models" ?
      <><InvestigateTable caption="Warranty cost by model" columns={modelColumns} result={result as PageResult<ModelWarrantyRecord>} onPage={(value) => navigate({ table_page: String(value) })} onPageSize={(value) => navigate({ page_size: String(value), table_page: "1" })} onSort={onSort}/><div className="drill-controls"><label>Choose a model to investigate<select value={drillChoice || String(modelRecords[0]?.model ?? "")} onChange={(event) => setDrillChoice(event.target.value)}>{modelRecords.map((record) => <option key={record.model}>{record.model}</option>)}</select></label><button type="button" onClick={() => resetTable({ focus_model: drillChoice || String(modelRecords[0]?.model ?? ""), focus_branch: null })}>View branches <span aria-hidden="true">→</span></button></div></>
    : level === "branches" ?
      <><InvestigateTable caption={`${selectedModel} warranty cost by branch`} columns={branchColumns} result={result as PageResult<BranchWarrantyRecord>} onPage={(value) => navigate({ table_page: String(value) })} onPageSize={(value) => navigate({ page_size: String(value), table_page: "1" })} onSort={onSort}/><div className="drill-controls"><label>Choose a branch to inspect<select value={drillChoice || String(branchRecords[0]?.branch ?? "")} onChange={(event) => setDrillChoice(event.target.value)}>{branchRecords.map((record) => <option key={record.branch}>{record.branch}</option>)}</select></label><button type="button" onClick={() => resetTable({ focus_branch: drillChoice || String(branchRecords[0]?.branch ?? "") })}>View claims <span aria-hidden="true">→</span></button></div></>
    : <>
      <div className="investigate-record-header"><div><span>Claim records</span><strong>{result.total.toLocaleString("en-US")}</strong><p>{selectedModel} · {selectedBranch}</p></div><div className="export-links"><a href={`${exportRoot}.csv?${exportQuery.toString()}`} download>Download CSV</a><a href={`${exportRoot}.pdf?${exportQuery.toString()}`} download>Download PDF</a></div></div>
      <InvestigateTable caption={`${selectedModel} claims in ${selectedBranch}`} columns={claimColumns} result={result as PageResult<WarrantyClaimRecord>} onPage={(value) => navigate({ table_page: String(value) })} onPageSize={(value) => navigate({ page_size: String(value), table_page: "1" })} onSort={onSort}/>
    </>}
  </>;
}
