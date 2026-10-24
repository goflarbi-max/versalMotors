export type FilterOptions = {
  date_range: { minimum: string | null; maximum: string | null; default_start: string | null };
  branches: string[];
  brands: string[];
  models: string[];
  salespeople: string[];
  statuses: string[];
};

export type BusinessFilters = {
  start_date: string;
  end_date: string;
  branch: string[];
  brand: string[];
  model: string[];
  salesperson: string[];
  status: string[];
};

export type KpiRecord = {
  metric: string;
  value: number | null;
  previous_value: number | null;
  change: number | null;
  change_rate: number | null;
};

export type RevenueTrendRecord = { period: string; revenue: number; transaction_count: number };
export type BranchRevenueRecord = { branch: string; revenue: number; units_sold: number };
export type ModelMarginRecord = { model: string; revenue: number; gross_margin: number; gross_margin_rate: number | null };
export type ApiEnvelope<T> = { data: T; meta: { filters: Record<string, unknown>; data_version: string; generated_at: string } };

export const filterKeys = ["branch", "brand", "model", "salesperson", "status"] as const;

export function readFilters(params: URLSearchParams, options: FilterOptions): BusinessFilters {
  return {
    start_date: params.get("start_date") ?? options.date_range.default_start ?? "",
    end_date: params.get("end_date") ?? options.date_range.maximum ?? "",
    branch: params.getAll("branch"),
    brand: params.getAll("brand"),
    model: params.getAll("model"),
    salesperson: params.getAll("salesperson"),
    status: params.getAll("status"),
  };
}

export function serializeFilters(filters: BusinessFilters): string {
  const params = new URLSearchParams();
  if (filters.start_date) params.set("start_date", filters.start_date);
  if (filters.end_date) params.set("end_date", filters.end_date);
  for (const key of filterKeys) for (const value of filters[key]) params.append(key, value);
  return params.toString();
}

export function formatKpi(metric: string, value: number | null): string {
  if (value === null || Number.isNaN(value)) return "—";
  if (metric === "Revenue" || metric === "Gross margin") return `GHS ${value.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
  if (metric === "Units sold") return value.toLocaleString("en-US", { maximumFractionDigits: 0 });
  return value.toLocaleString("en-US", { style: "percent", minimumFractionDigits: 1, maximumFractionDigits: 1 });
}

export function formatChange(value: number | null): string | null {
  if (value === null || Number.isNaN(value)) return null;
  return `${value >= 0 ? "+" : ""}${(value * 100).toFixed(1)}% vs prior period`;
}

export function formatCompactGhs(value: number): string {
  const magnitude = Math.abs(value);
  if (magnitude >= 1_000_000_000) return `GHS ${(value / 1_000_000_000).toFixed(1)}B`;
  if (magnitude >= 1_000_000) return `GHS ${(value / 1_000_000).toFixed(0)}M`;
  if (magnitude >= 1_000) return `GHS ${(value / 1_000).toFixed(0)}K`;
  return `GHS ${value.toFixed(0)}`;
}

export function formatMonth(value: string): string {
  return new Intl.DateTimeFormat("en", { month: "short", year: "2-digit", timeZone: "UTC" }).format(new Date(value));
}
