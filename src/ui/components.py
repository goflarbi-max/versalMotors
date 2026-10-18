"""Reusable, presentation-only components for the VersalMotors interface."""

from __future__ import annotations

import base64
import hashlib
from html import escape
import math
from pathlib import Path
from collections.abc import Mapping
from functools import partial
from typing import Any

import pandas as pd
import streamlit as st
from streamlit.errors import StreamlitAPIException

from src.ui.theme import TABLE_COMPONENT_CSS, active_table_theme


ROOT = Path(__file__).resolve().parents[2]
ASSETS_DIR = ROOT / "assets"
LOGO_DARK = ASSETS_DIR / "logo_dark.png"
LOGO_LIGHT = ASSETS_DIR / "logo_light.png"
GITHUB_URL = "https://github.com/goflarbi-max/versalMotors"

_TABLE_COMPONENT = st.components.v2.component(
    "versal_table",
    html='<div class="versal-table-root" aria-live="polite"></div>',
    css=TABLE_COMPONENT_CSS,
    js="""
export default function (component) {
  const { data, parentElement, setTriggerValue } = component
  const root = parentElement.querySelector(".versal-table-root")
  if (!root || !data) return

  Object.entries(data.theme || {}).forEach(([name, value]) => {
    const token = name.startsWith("table_") ? name.slice(6) : name
    root.style.setProperty(`--table-${token.replaceAll("_", "-")}`, String(value))
  })

  if (data.empty) {
    root.innerHTML = `<div class="versal-table-empty" role="status">${data.empty_message}</div>`
    return
  }

  const headers = data.columns.map((column) => {
    const active = data.sort_column === column.key
    const arrow = active ? (data.sort_direction === "asc" ? "&#8593;" : "&#8595;") : "&#8597;"
    const direction = active
      ? (data.sort_direction === "asc" ? "ascending" : "descending")
      : "none"
    return `
      <th scope="col" aria-sort="${direction}">
        <button class="versal-table-sort" type="button" data-sort="${column.position}">
          <span>${column.label}</span>
          <span class="versal-table-sort-indicator" aria-hidden="true">${arrow}</span>
        </button>
      </th>`
  }).join("")

  const body = data.rows.map((row) => `
    <tr>${row.map((cell) => `<td>${cell}</td>`).join("")}</tr>`
  ).join("")

  root.innerHTML = `
    <div class="versal-table-card">
      <div class="versal-table-scroll" tabindex="0" aria-label="Scrollable table">
        <table class="versal-table">
          <thead><tr>${headers}</tr></thead>
          <tbody>${body}</tbody>
        </table>
      </div>
      <div class="versal-table-footer">
        <span>${data.showing_text}</span>
        <div class="versal-table-controls"></div>
      </div>
    </div>`

  root.querySelectorAll("[data-sort]").forEach((button) => {
    button.addEventListener("click", () => {
      const position = Number(button.dataset.sort)
      const column = data.columns[position]
      if (column) setTriggerValue("action", { kind: "sort", column: column.key })
    })
  })

  const controls = root.querySelector(".versal-table-controls")
  if (!controls || data.total_rows <= 10) return

  const sizeLabel = document.createElement("label")
  sizeLabel.textContent = "Rows "
  const size = document.createElement("select")
  size.className = "versal-table-size"
  size.setAttribute("aria-label", "Rows per page")
  ;[10, 25, 50].forEach((value) => {
    const option = document.createElement("option")
    option.value = String(value)
    option.textContent = String(value)
    option.selected = value === data.page_size
    size.appendChild(option)
  })
  size.addEventListener("change", () => {
    setTriggerValue("action", { kind: "page_size", value: Number(size.value) })
  })
  sizeLabel.appendChild(size)
  controls.appendChild(sizeLabel)

  const pagination = document.createElement("nav")
  pagination.className = "versal-table-pagination"
  pagination.setAttribute("aria-label", "Table pages")

  const addPageButton = (label, page, active = false, disabled = false, ariaLabel = "") => {
    const button = document.createElement("button")
    button.type = "button"
    button.className = `versal-table-page${active ? " is-active" : ""}`
    button.textContent = label
    button.disabled = disabled
    if (ariaLabel) button.setAttribute("aria-label", ariaLabel)
    if (active) button.setAttribute("aria-current", "page")
    button.addEventListener("click", () => {
      if (!disabled) setTriggerValue("action", { kind: "page", value: page })
    })
    pagination.appendChild(button)
  }

  addPageButton("\u00ab", data.page - 1, false, data.page <= 1, "Previous page")
  data.page_tokens.forEach((token) => {
    if (token === "ellipsis") {
      const ellipsis = document.createElement("span")
      ellipsis.className = "versal-table-ellipsis"
      ellipsis.textContent = "\u2026"
      pagination.appendChild(ellipsis)
    } else {
      addPageButton(String(token), token, token === data.page, false, `Page ${token}`)
    }
  })
  addPageButton("\u00bb", data.page + 1, false, data.page >= data.total_pages, "Next page")
  controls.appendChild(pagination)
}
""",
)

_OVERVIEW_ICONS = {
    "payments",
    "account_balance_wallet",
    "directions_car",
    "percent",
    "show_chart",
    "location_on",
}


def _overview_icon(icon: str, *, size: int = 20) -> str:
    """Return a whitelisted Material Symbol using Streamlit's loaded font."""
    icon_name = icon if icon in _OVERVIEW_ICONS else "show_chart"
    return (
        f'<span class="material-symbols-rounded" aria-hidden="true" '
        f'style="font-size:{size}px">{icon_name}</span>'
    )


def current_theme_type() -> str | None:
    """Return Streamlit's active theme when the installed version exposes it."""
    try:
        theme_type = st.context.theme.type
    except (AttributeError, RuntimeError):
        return None
    return theme_type if theme_type in {"light", "dark"} else None


def active_logo_path() -> Path:
    """Return the contrasting logo for the active theme, defaulting safely to light."""
    return LOGO_LIGHT if current_theme_type() == "dark" else LOGO_DARK


def _data_uri(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def render_logo(width: int) -> None:
    """Render the logo using Streamlit's current text colour as its artwork colour.

    The transparent logo supplies the alpha mask. Inheriting ``currentColor``
    makes the artwork dark in light mode and white in dark mode, including the
    first render when Python theme context is not yet available.
    """
    st.html(
        f"""
        <div
          class="versal-theme-logo"
          role="img"
          aria-label="VersalMotors"
          style="
            width: min(100%, {width}px);
            aspect-ratio: 505 / 202;
            margin-inline: auto;
            background-color: currentColor;
            -webkit-mask: url('{_data_uri(LOGO_DARK)}') center / contain no-repeat;
            mask: url('{_data_uri(LOGO_DARK)}') center / contain no-repeat;
          "
        ></div>
        """
    )


def kpi_card(
    label: str,
    value: str,
    change: str | None,
    footer_text: str,
    icon: str,
) -> None:
    """Render an escaped, presentation-only Overview KPI card."""
    safe_label = escape(str(label))
    safe_value = escape(str(value))
    safe_footer = escape(str(footer_text))
    safe_icon = escape(str(icon))

    badge_html = ""
    comparison_html = ""
    if change:
        change_text = str(change).strip()
        badge_value, separator, comparison = change_text.partition(" vs ")
        tone = "down" if badge_value.startswith("-") else "up" if badge_value.startswith("+") else "neutral"
        arrow = "↓" if tone == "down" else "↑" if tone == "up" else "→"
        safe_badge = escape(badge_value)
        comparison_text = f"vs {comparison}" if separator else ""
        badge_html = (
            f'<span class="versal-overview-change versal-overview-change--{tone}">'
            f'<span aria-hidden="true">{arrow}</span>{safe_badge}</span>'
        )
        comparison_html = (
            '<div class="versal-overview-kpi-divider"></div>'
            '<div class="versal-overview-kpi-footer">'
            '<div class="versal-overview-kpi-footer-copy">'
            f'<strong>{safe_badge}</strong><span>{escape(comparison_text)}</span>'
            '</div></div>'
        )

    st.html(
        f"""
        <div class="versal-overview-kpi-outer">
          <div class="versal-overview-kpi-inner">
            <div class="versal-overview-kpi-head">
              <p class="versal-overview-kpi-label">{safe_label}</p>
              <span class="versal-overview-icon-tile" aria-hidden="true">
                {_overview_icon(safe_icon)}
              </span>
            </div>
            <div class="versal-overview-kpi-value-row">
              <span class="versal-overview-kpi-value">{safe_value}</span>
              {badge_html}
            </div>
            <p class="versal-overview-kpi-question">{safe_footer}</p>
            {comparison_html}
          </div>
        </div>
        """
    )


def overview_chart_header(eyebrow: str, title: str, caption: str, icon: str) -> None:
    """Render an escaped header for an Overview chart card."""
    st.html(
        f"""
        <div class="versal-overview-chart-head">
          <div class="versal-overview-chart-copy">
            <p class="versal-overview-chart-eyebrow">{escape(str(eyebrow))}</p>
            <p class="versal-overview-chart-title">{escape(str(title))}</p>
            <p class="versal-overview-chart-caption">{escape(str(caption))}</p>
          </div>
          <span class="versal-overview-icon-tile" aria-hidden="true">
            {_overview_icon(str(icon))}
          </span>
        </div>
        """
    )


def _table_fingerprint(df: pd.DataFrame) -> str:
    """Return a stable content fingerprint used to reset pagination after filtering."""
    digest = hashlib.sha256()
    digest.update(repr(tuple(df.columns)).encode("utf-8"))
    digest.update(repr(tuple(map(str, df.dtypes))).encode("utf-8"))
    digest.update(repr(tuple(df.index.names)).encode("utf-8"))
    try:
        digest.update(pd.util.hash_pandas_object(df, index=True).to_numpy().tobytes())
    except (TypeError, ValueError):
        digest.update(df.to_json(orient="split", date_format="iso", default_handler=str).encode("utf-8"))
    return digest.hexdigest()


def _sort_table_frame(
    df: pd.DataFrame,
    column: str | None,
    direction: str | None,
) -> pd.DataFrame:
    """Stable-sort a copy by its native dtype, always placing nulls last."""
    result = df.copy(deep=True)
    if column not in result.columns or direction not in {"asc", "desc"}:
        return result

    series = result[column]
    key = None
    if pd.api.types.is_string_dtype(series.dtype) or series.dtype == object:
        key = lambda values: values.astype("string").str.casefold()

    try:
        return result.sort_values(
            by=column,
            ascending=direction == "asc",
            kind="mergesort",
            na_position="last",
            key=key,
        )
    except (TypeError, ValueError):
        return result.sort_values(
            by=column,
            ascending=direction == "asc",
            kind="mergesort",
            na_position="last",
            key=lambda values: values.astype("string").str.casefold(),
        )


def _paginate_table_frame(
    df: pd.DataFrame,
    page: int,
    page_size: int,
) -> tuple[pd.DataFrame, int, int, int, int]:
    """Return one copied page plus its clamped boundaries."""
    safe_size = page_size if page_size in {10, 25, 50} else 10
    total_pages = max(1, math.ceil(len(df) / safe_size))
    safe_page = min(max(int(page), 1), total_pages)
    start_index = (safe_page - 1) * safe_size
    page_frame = df.iloc[start_index : start_index + safe_size].copy(deep=True)
    shown_start = start_index + 1 if len(df) else 0
    shown_end = min(start_index + safe_size, len(df))
    return page_frame, safe_page, total_pages, shown_start, shown_end


def _pagination_tokens(page: int, total_pages: int) -> list[int | str]:
    """Return at most five numbered page buttons with compact ellipses."""
    if total_pages <= 5:
        return list(range(1, total_pages + 1))
    if page <= 3:
        return [1, 2, 3, 4, "ellipsis", total_pages]
    if page >= total_pages - 2:
        return [1, "ellipsis", total_pages - 3, total_pages - 2, total_pages - 1, total_pages]
    return [1, "ellipsis", page - 1, page, page + 1, "ellipsis", total_pages]


def _is_missing_table_value(value: Any) -> bool:
    try:
        missing = pd.isna(value)
    except (TypeError, ValueError):
        return False
    if hasattr(missing, "__len__"):
        return False
    try:
        return bool(missing)
    except (TypeError, ValueError):
        return False


def _format_table_value(value: Any, format_name: str | None = None) -> str:
    """Format and HTML-escape one display value without changing source data."""
    if value is None or _is_missing_table_value(value):
        return ""

    if format_name == "percent":
        try:
            rendered = f"{float(value):.2%}"
        except (TypeError, ValueError):
            rendered = str(value)
    elif format_name == "DD MMM YYYY":
        try:
            rendered = pd.Timestamp(value).strftime("%d %b %Y")
        except (TypeError, ValueError):
            rendered = str(value)
    elif format_name and "%" in format_name:
        try:
            rendered = format_name % float(value)
        except (TypeError, ValueError):
            rendered = str(value)
    else:
        rendered = str(value)
    return escape(rendered, quote=True)


def _build_table_payload(
    df: pd.DataFrame,
    *,
    sort_column: str | None = None,
    sort_direction: str | None = None,
    page: int = 1,
    page_size: int = 10,
    column_config: Mapping[str, Mapping[str, str]] | None = None,
    theme: Mapping[str, str] | None = None,
    empty_message: str = "No records match the current filters",
) -> dict[str, Any]:
    """Build the escaped, current-page payload consumed by the table component."""
    config = column_config or {}
    sorted_frame = _sort_table_frame(df, sort_column, sort_direction)
    page_frame, safe_page, total_pages, shown_start, shown_end = _paginate_table_frame(
        sorted_frame, page, page_size
    )
    columns = []
    for position, column in enumerate(df.columns):
        settings = config.get(str(column), {})
        columns.append(
            {
                "key": str(column),
                "label": escape(settings.get("label", str(column)), quote=True),
                "position": position,
            }
        )

    rows = []
    for values in page_frame.itertuples(index=False, name=None):
        rows.append(
            [
                _format_table_value(value, config.get(str(column), {}).get("format"))
                for column, value in zip(df.columns, values)
            ]
        )

    return {
        "columns": columns,
        "rows": rows,
        "empty": df.empty,
        "empty_message": escape(empty_message, quote=True),
        "sort_column": sort_column if sort_column in df.columns else None,
        "sort_direction": sort_direction if sort_direction in {"asc", "desc"} else None,
        "page": safe_page,
        "page_size": page_size if page_size in {10, 25, 50} else 10,
        "total_pages": total_pages,
        "total_rows": len(df),
        "showing_text": f"Showing {shown_start} to {shown_end} of {len(df)} entries",
        "page_tokens": _pagination_tokens(safe_page, total_pages),
        "theme": dict(theme or {}),
    }


def _table_action_callback(
    component_key: str,
    state_key: str,
    allowed_columns: tuple[str, ...],
) -> None:
    """Apply a component event to its table-specific Session State entry."""
    component_state = st.session_state.get(component_key)
    if component_state is None:
        return
    action = component_state.get("action") if hasattr(component_state, "get") else getattr(component_state, "action", None)
    if not isinstance(action, Mapping):
        return

    state = dict(st.session_state.get(state_key, {}))
    kind = action.get("kind")
    if kind == "sort":
        column = str(action.get("column", ""))
        if column not in allowed_columns:
            return
        if state.get("sort_column") != column:
            state["sort_column"], state["sort_direction"] = column, "asc"
        elif state.get("sort_direction") == "asc":
            state["sort_direction"] = "desc"
        else:
            state["sort_column"], state["sort_direction"] = None, None
        state["page"] = 1
    elif kind == "page":
        try:
            state["page"] = max(1, int(action.get("value", 1)))
        except (TypeError, ValueError):
            return
    elif kind == "page_size":
        try:
            page_size = int(action.get("value", 10))
        except (TypeError, ValueError):
            return
        if page_size not in {10, 25, 50}:
            return
        state["page_size"] = page_size
        state["page"] = 1
    else:
        return
    st.session_state[state_key] = state


def render_table(
    df: pd.DataFrame,
    key: str,
    *,
    column_config: Mapping[str, Mapping[str, str]] | None = None,
    empty_message: str = "No records match the current filters",
) -> None:
    """Render a safe, sortable, paginated copy of ``df`` without mutating it."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("render_table expects a pandas DataFrame")
    if not key:
        raise ValueError("render_table requires a stable, non-empty key")

    state_key = f"_versal_table_state_{key}"
    component_key = f"_versal_table_component_{key}"
    fingerprint = _table_fingerprint(df)
    state = dict(st.session_state.get(state_key, {}))
    state.setdefault("sort_column", None)
    state.setdefault("sort_direction", None)
    state.setdefault("page", 1)
    state.setdefault("page_size", 10)
    if state.get("fingerprint") != fingerprint:
        state["fingerprint"] = fingerprint
        state["page"] = 1
        if state.get("sort_column") not in df.columns:
            state["sort_column"], state["sort_direction"] = None, None
    st.session_state[state_key] = state

    payload = _build_table_payload(
        df,
        sort_column=state["sort_column"],
        sort_direction=state["sort_direction"],
        page=state["page"],
        page_size=state["page_size"],
        column_config=column_config,
        theme=active_table_theme(),
        empty_message=empty_message,
    )
    if payload["page"] != state["page"]:
        state["page"] = payload["page"]
        st.session_state[state_key] = state

    try:
        _TABLE_COMPONENT(
            key=component_key,
            data=payload,
            width="stretch",
            height="content",
            on_action_change=partial(
                _table_action_callback,
                component_key,
                state_key,
                tuple(map(str, df.columns)),
            ),
        )
    except StreamlitAPIException as exc:
        if "is not registered" not in str(exc):
            raise
        # AppTest can import this module before creating its simulated runtime.
        # A native table preserves the data and keeps that environment usable.
        st.dataframe(df.copy(deep=True), hide_index=True, width="stretch")
