"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import {
  ApiEnvelope, BusinessFilters, FilterOptions, filterKeys, readFilters, serializeFilters,
} from "@/lib/overview";

type FilterContextValue = {
  options: FilterOptions | null;
  filters: BusinessFilters | null;
  query: string;
  loading: boolean;
  error: string | null;
  update: (key: keyof BusinessFilters, value: string | string[]) => void;
  clear: () => void;
};

const FilterContext = createContext<FilterContextValue | null>(null);

export function FilterProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [options, setOptions] = useState<FilterOptions | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    fetch("/api/v1/filters/options", { credentials: "include", signal: controller.signal })
      .then(async (response) => {
        if (!response.ok) throw new Error("Business filters are temporarily unavailable.");
        return response.json() as Promise<ApiEnvelope<FilterOptions>>;
      })
      .then((payload) => setOptions(payload.data))
      .catch((reason: unknown) => {
        if (!(reason instanceof DOMException && reason.name === "AbortError")) setError("Business filters are temporarily unavailable.");
      });
    return () => controller.abort();
  }, []);

  const filters = useMemo(
    () => options ? readFilters(new URLSearchParams(searchParams.toString()), options) : null,
    [options, searchParams],
  );
  const query = filters ? serializeFilters(filters) : "";

  useEffect(() => {
    if (!filters || (searchParams.has("start_date") && searchParams.has("end_date"))) return;
    window.history.replaceState(null, "", `${pathname}?${query}`);
  }, [filters, pathname, query, searchParams]);

  const replaceFilters = useCallback((next: BusinessFilters) => {
    const serialized = serializeFilters(next);
    router.replace(serialized ? `${pathname}?${serialized}` : pathname, { scroll: false });
  }, [pathname, router]);

  const update = useCallback((key: keyof BusinessFilters, value: string | string[]) => {
    if (!filters) return;
    replaceFilters({ ...filters, [key]: value });
  }, [filters, replaceFilters]);

  const clear = useCallback(() => {
    if (!options) return;
    replaceFilters({
      start_date: options.date_range.default_start ?? "",
      end_date: options.date_range.maximum ?? "",
      branch: [], brand: [], model: [], salesperson: [], status: [],
    });
  }, [options, replaceFilters]);

  return <FilterContext.Provider value={{ options, filters, query, loading: !options && !error, error, update, clear }}>{children}</FilterContext.Provider>;
}

export function useBusinessFilters() {
  const value = useContext(FilterContext);
  if (!value) throw new Error("useBusinessFilters must be used inside FilterProvider");
  return value;
}

const labels: Record<(typeof filterKeys)[number], string> = {
  branch: "Branch", brand: "Brand", model: "Model", salesperson: "Salesperson", status: "Sale status",
};

function MultiSelectFilter({ label, values, selected, onChange }: { label: string; values: string[]; selected: string[]; onChange: (value: string[]) => void }) {
  const summary = selected.length === 0 ? "Choose options" : selected.length <= 2 ? selected.join(", ") : `${selected.length} selected`;
  return <div className="filter-select">
    <span>{label}</span>
    <details>
      <summary aria-label={label}>{summary}</summary>
      <div className="filter-options" role="group" aria-label={`${label} options`}>
        {values.map((value) => <label key={value}><input type="checkbox" checked={selected.includes(value)} onChange={(event) => onChange(event.target.checked ? [...selected, value] : selected.filter((item) => item !== value))}/><span>{value}</span></label>)}
      </div>
    </details>
  </div>;
}

export function BusinessFilterPanel() {
  const { options, filters, loading, error, update, clear } = useBusinessFilters();
  if (loading) return <div className="filter-panel filter-loading" aria-label="Loading business filters" />;
  if (error || !options || !filters) return <p className="filter-error">{error ?? "Business filters are unavailable."}</p>;
  const optionMap = {
    branch: options.branches, brand: options.brands, model: options.models,
    salesperson: options.salespeople, status: options.statuses,
  };
  return (
    <section className="filter-panel" aria-label="Business filters">
      <div className="filter-heading"><div><strong>Business filters</strong><span>Selections persist between pages.</span></div><button type="button" onClick={clear}>Reset</button></div>
      <div className="date-filter-row">
        <label>From<input type="date" min={options.date_range.minimum ?? undefined} max={(filters.end_date || options.date_range.maximum) ?? undefined} value={filters.start_date} onChange={(event) => update("start_date", event.target.value)} /></label>
        <label>To<input type="date" min={(filters.start_date || options.date_range.minimum) ?? undefined} max={options.date_range.maximum ?? undefined} value={filters.end_date} onChange={(event) => update("end_date", event.target.value)} /></label>
      </div>
      {filterKeys.map((key) => <MultiSelectFilter key={key} label={labels[key]} values={optionMap[key]} selected={filters[key]} onChange={(value) => update(key, value)}/>)}
    </section>
  );
}
