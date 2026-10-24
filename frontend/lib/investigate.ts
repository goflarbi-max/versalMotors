import { ApiEnvelope } from "@/lib/overview";

export type SortDirection = "original" | "asc" | "desc";

export type PageResult<T> = {
  records: T[];
  total: number;
  page: number;
  page_size: number;
  sort_by: string | null;
  sort_dir: SortDirection;
};

export type ModelWarrantyRecord = {
  model: string;
  claim_count: number;
  claim_cost: number;
  previous_claim_cost: number;
  cost_change: number;
  cost_change_rate: number | null;
};

export type BranchWarrantyRecord = {
  branch: string;
  claim_count: number;
  claim_cost: number;
  share_of_model_cost: number | null;
};

export type WarrantyClaimRecord = {
  claim_id: number;
  claim_date: string | null;
  model: string;
  branch: string;
  failure_category: string | null;
  claim_description: string | null;
  claim_status: string | null;
  claim_amount: number | null;
  approved_amount: number | null;
  manufacturer_recovery_amount: number | null;
  sale_id: number | null;
  service_id: number | null;
  inventory_id: number | null;
  _row_quality_status: string | null;
};

export async function getInvestigationPage<T>(path: string, signal: AbortSignal): Promise<PageResult<T>> {
  const response = await fetch(path, { credentials: "include", signal });
  if (!response.ok) throw new Error("Investigation data could not be loaded.");
  return (await response.json() as ApiEnvelope<PageResult<T>>).data;
}

export function formatGhs(value: unknown): string {
  if (typeof value !== "number" || Number.isNaN(value)) return "—";
  return `GHS ${value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export function formatInteger(value: unknown): string {
  return typeof value === "number" ? value.toLocaleString("en-US", { maximumFractionDigits: 0 }) : "—";
}

export function formatPercent(value: unknown): string {
  return typeof value === "number" ? value.toLocaleString("en-US", { style: "percent", minimumFractionDigits: 1, maximumFractionDigits: 1 }) : "—";
}

export function formatDate(value: unknown): string {
  return typeof value === "string" && value ? value.slice(0, 10) : "—";
}
