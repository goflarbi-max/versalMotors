"use client";

import { PageResult, SortDirection } from "@/lib/investigate";

export type TableColumn<T> = {
  key: keyof T & string;
  label: string;
  format?: (value: T[keyof T], record: T) => string;
};

type Props<T> = {
  caption: string;
  columns: TableColumn<T>[];
  result: PageResult<T>;
  onPage: (page: number) => void;
  onPageSize: (pageSize: number) => void;
  onSort: (key: string, direction: SortDirection) => void;
  rowAction?: { label: string; onSelect: (record: T) => void };
};

function nextDirection(active: boolean, direction: SortDirection): SortDirection {
  if (!active || direction === "original") return "asc";
  if (direction === "asc") return "desc";
  return "original";
}

function pageTokens(page: number, totalPages: number): (number | "ellipsis")[] {
  if (totalPages <= 5) return Array.from({ length: totalPages }, (_, index) => index + 1);
  if (page <= 3) return [1, 2, 3, 4, "ellipsis", totalPages];
  if (page >= totalPages - 2) return [1, "ellipsis", totalPages - 3, totalPages - 2, totalPages - 1, totalPages];
  return [1, "ellipsis", page - 1, page, page + 1, "ellipsis", totalPages];
}

export function InvestigateTable<T extends object>({ caption, columns, result, onPage, onPageSize, onSort, rowAction }: Props<T>) {
  const totalPages = Math.max(1, Math.ceil(result.total / result.page_size));
  const first = result.total ? (result.page - 1) * result.page_size + 1 : 0;
  const last = Math.min(result.page * result.page_size, result.total);

  if (!result.total) {
    return <section className="investigate-table-card empty"><h2>{caption}</h2><p>No records match the current filters.</p></section>;
  }

  return <section className="investigate-table-card">
    <div className="table-heading"><h2>{caption}</h2><label>Rows per page<select aria-label={`${caption} rows per page`} value={result.page_size} onChange={(event) => onPageSize(Number(event.target.value))}>{[10,25,50].map((size) => <option key={size}>{size}</option>)}</select></label></div>
    <div className="table-scroll">
      <table>
        <thead><tr>{columns.map((column) => {
          const active = result.sort_by === column.key && result.sort_dir !== "original";
          const marker = active ? (result.sort_dir === "asc" ? "▲" : "▼") : "↕";
          return <th key={column.key} scope="col"><button type="button" onClick={() => onSort(column.key, nextDirection(active, result.sort_dir))} aria-label={`Sort ${column.label} ${active ? result.sort_dir : "original"}`}>{column.label}<span aria-hidden="true">{marker}</span></button></th>;
        })}{rowAction ? <th scope="col"><span className="sr-only">Action</span></th> : null}</tr></thead>
        <tbody>{result.records.map((record, index) => <tr key={`${String(record[columns[0].key as keyof T])}-${index}`}>{columns.map((column) => {
          const value = record[column.key as keyof T];
          return <td key={column.key}>{column.format ? column.format(value, record) : value === null || value === undefined ? "—" : String(value)}</td>;
        })}{rowAction ? <td><button className="row-action" type="button" onClick={() => rowAction.onSelect(record)}>{rowAction.label}<span aria-hidden="true">→</span></button></td> : null}</tr>)}</tbody>
      </table>
    </div>
    <footer className="table-footer"><span>Showing {first} to {last} of {result.total.toLocaleString("en-US")} entries</span>{totalPages > 1 ? <nav aria-label={`${caption} pages`}><button type="button" aria-label="Previous page" disabled={result.page <= 1} onClick={() => onPage(result.page - 1)}>«</button>{pageTokens(result.page, totalPages).map((token, index) => token === "ellipsis" ? <span className="table-ellipsis" key={`ellipsis-${index}`}>…</span> : <button type="button" key={token} className={token === result.page ? "active" : undefined} aria-label={`Page ${token}`} aria-current={token === result.page ? "page" : undefined} onClick={() => onPage(token)}>{token}</button>)}<button type="button" aria-label="Next page" disabled={result.page >= totalPages} onClick={() => onPage(result.page + 1)}>»</button></nav> : null}</footer>
  </section>;
}
