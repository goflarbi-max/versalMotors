import { PageResult } from "@/lib/investigate";
import { ApiEnvelope } from "@/lib/overview";

export type QualitySummary = { issues_found: number; tables_affected: number; total_affected: number; highest_share: number; highest_share_table?: string };
export type QualityCheck = { table: string; issue: string; count: number; total_rows: number; share_pct: number; impact: string };
export type CleaningLogRecord = { step: string; table: string; rows_affected: number; reason: string; action_taken: string };
export type CleaningLogPage = PageResult<CleaningLogRecord> & { available: boolean };

export async function getQualityData<T>(path: string, signal: AbortSignal): Promise<T> {
  const response = await fetch(path, { credentials: "include", signal });
  if (!response.ok) throw new Error("Data Quality information could not be loaded.");
  return (await response.json() as ApiEnvelope<T>).data;
}

export function formatCount(value: unknown): string {
  return typeof value === "number" ? value.toLocaleString("en-US", { maximumFractionDigits: 0 }) : "—";
}

export function formatQualityPercent(value: unknown): string {
  return typeof value === "number" ? `${value.toFixed(2)}%` : "—";
}
