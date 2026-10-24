"use client";

type Props = { records: Record<string, unknown>[]; caption: string };

function display(value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "number") return value.toLocaleString("en-US", { maximumFractionDigits: 2 });
  return String(value).replace("T00:00:00", "");
}

export function EvidenceTable({ records, caption }: Props) {
  if (!records.length) return <div className="evidence-empty">No supporting records were returned.</div>;
  const columns = Object.keys(records[0]);
  return <div className="evidence-table-card">
    <div className="evidence-scroll"><table><caption>{caption}</caption><thead><tr>{columns.map((column) => <th key={column}>{column.replaceAll("_", " ")}</th>)}</tr></thead><tbody>{records.map((record, index) => <tr key={index}>{columns.map((column) => <td key={column}>{display(record[column])}</td>)}</tr>)}</tbody></table></div>
    <footer>Showing {records.length.toLocaleString("en-US")} verified {records.length === 1 ? "record" : "records"}</footer>
  </div>;
}
