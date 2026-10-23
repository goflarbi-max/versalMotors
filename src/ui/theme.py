"""Shared visual styling for the Streamlit shell and landing page."""

import streamlit as st


THEME_STATE_KEY = "sidebar_dark_mode"


TYPOGRAPHY_THEME = {
    "font_family": 'Inter, system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif',
    "font_weight_body": 400,
    "font_weight_label": 500,
    "font_weight_strong": 600,
    "font_weight_heading": 700,
    "font_size_body": "16px",
    "font_size_readable_min": "14px",
    "font_size_caption": "12px",
}


def apply_typography() -> None:
    """Apply the shared type system to native and custom Streamlit content."""
    typography = TYPOGRAPHY_THEME
    st.html(
        f"""
        <style id="versal-typography">
        :root {{
            --versal-font-family: {typography["font_family"]};
            --versal-font-weight-body: {typography["font_weight_body"]};
            --versal-font-weight-label: {typography["font_weight_label"]};
            --versal-font-weight-strong: {typography["font_weight_strong"]};
            --versal-font-weight-heading: {typography["font_weight_heading"]};
            --versal-font-size-body: {typography["font_size_body"]};
            --versal-font-size-readable-min: {typography["font_size_readable_min"]};
            --versal-font-size-caption: {typography["font_size_caption"]};
        }}

        html,
        body,
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stSidebar"],
        button,
        input,
        textarea,
        select {{
            font-family: var(--versal-font-family) !important;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}

        body,
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li {{
            font-weight: var(--versal-font-weight-body);
            line-height: 1.5;
        }}

        h1, h2, h3, h4, h5, h6,
        [data-testid="stHeadingWithActionElements"] {{
            font-family: var(--versal-font-family) !important;
            font-weight: var(--versal-font-weight-heading);
            letter-spacing: -0.015em;
        }}

        label,
        nav,
        [role="tab"],
        [data-testid="stWidgetLabel"] {{
            font-weight: var(--versal-font-weight-label);
        }}

        [data-testid="stCaptionContainer"],
        [data-testid="stCaptionContainer"] * {{
            font-size: var(--versal-font-size-caption) !important;
        }}

        [data-testid="stMetricValue"],
        [data-testid="stMetricDelta"],
        .versal-overview-kpi-value,
        .versal-overview-change,
        .versal-summary-value,
        .versal-summary-ring,
        .versal-table td {{
            font-variant-numeric: tabular-nums;
        }}

        /* Icon ligatures must retain their own typeface. */
        [data-testid="stIconMaterial"],
        .material-symbols-rounded {{
            font-family: "Material Symbols Rounded" !important;
        }}
        </style>
        """
    )


PUBLIC_LANDING_THEME = {
    "landing_gradient_start": "#000000",
    "landing_gradient_end": "#0A0A0A",
    "landing_text": "#FFFFFF",
    "landing_text_muted": "rgba(255, 255, 255, 0.86)",
    "landing_band_bg": "#E8EDF4",
    "landing_card_bg": "#FFFFFF",
    "landing_button_border": "rgba(255, 255, 255, 0.92)",
    "landing_card_text": "#12213F",
    "landing_card_muted": "#5B677A",
    "landing_icon": "#1450B8",
    "landing_icon_bg": "#EEF4FF",
    "landing_icon_stroke": "rgba(255, 255, 255, 0.85)",
    "landing_icon_tile_border": "rgba(255, 255, 255, 0.25)",
    "landing_icon_tile_bg": "rgba(255, 255, 255, 0.05)",
    "landing_card_shadow": "0 16px 38px rgba(7, 27, 74, 0.12)",
    "landing_focus": "#F8D14A",
    "landing_anim_duration": "650ms",
    "landing_anim_stagger": "110ms",
    "landing_anim_distance": "14px",
    "landing_icon_sweep": "70ms",
    "landing_wave_duration": "18s",
    "landing_hover_duration": "200ms",
}


SIDEBAR_THEME = {
    "light": {
        "sidebar_bg": "#F1F3F5",
        "sidebar_text": "#242629",
        "sidebar_active_bg": "#242629",
        "sidebar_active_text": "#FFFFFF",
        "sidebar_hover_bg": "#E3E6E9",
        "sidebar_divider": "#D4D8DC",
        "sidebar_danger": "#CF291D",
        "sidebar_focus": "#4F46E5",
        "sidebar_shadow": "6px 0 20px rgba(15, 23, 42, 0.06)",
        "hamburger_line": "#242629",
        "hamburger_border": "#D4D8DC",
        "hamburger_hover_bg": "#E3E6E9",
    },
    "dark": {
        "sidebar_bg": "#211E1D",
        "sidebar_text": "#F4F4F5",
        "sidebar_active_bg": "#F4F4F5",
        "sidebar_active_text": "#211E1D",
        "sidebar_hover_bg": "#34302F",
        "sidebar_divider": "#45403E",
        "sidebar_danger": "#FF6B61",
        "sidebar_focus": "#A5B4FC",
        "sidebar_shadow": "6px 0 20px rgba(0, 0, 0, 0.22)",
        "hamburger_line": "#F4F4F5",
        "hamburger_border": "#45403E",
        "hamburger_hover_bg": "#34302F",
    },
}


RUNTIME_THEME = {
    "light": {
        "background": "#F8FAFC",
        "secondary_background": "#FFFFFF",
        "text": "#0F172A",
        "muted_text": "#64748B",
        "border": "#E2E8F0",
        "focus": "#4F46E5",
        "color_scheme": "light",
    },
    "dark": {
        "background": "#0F172A",
        "secondary_background": "#1E293B",
        "text": "#F1F5F9",
        "muted_text": "#CBD5E1",
        "border": "#334155",
        "focus": "#818CF8",
        "color_scheme": "dark",
    },
}


# Login intentionally has one visual mode. These tokens reuse the existing
# light runtime palette so the access screen cannot drift into a second theme.
LOGIN_THEME = {
    "page_background": RUNTIME_THEME["light"]["background"],
    "text": RUNTIME_THEME["light"]["text"],
    "muted_text": RUNTIME_THEME["light"]["muted_text"],
    "field_background": RUNTIME_THEME["light"]["secondary_background"],
    "field_border": RUNTIME_THEME["light"]["border"],
    "card_background": "rgba(255, 255, 255, 0.64)",
    "fallback_background": "rgba(255, 255, 255, 0.96)",
    "card_border": "rgba(255, 255, 255, 0.78)",
    "card_shadow": "0 24px 65px rgba(15, 23, 42, 0.18)",
    "shape_one": "rgba(99, 102, 241, 0.20)",
    "shape_two": "rgba(56, 189, 248, 0.17)",
    "accent": "#6366F1",
    "login_button_bg_top": "#2A2E37",
    "login_button_bg_bottom": "#1C1F26",
    "login_button_hover": "#2F343E",
    "login_button_text": "#FFFFFF",
    "login_button_shadow": "0 6px 16px rgba(15, 23, 42, 0.25)",
    "login_button_hover_shadow": "0 8px 20px rgba(15, 23, 42, 0.28)",
    "login_button_pressed_shadow": "0 3px 8px rgba(15, 23, 42, 0.20)",
    "login_button_highlight": "inset 0 1px 0 rgba(255, 255, 255, 0.13)",
    "login_button_focus": "#6366F1",
    "login_button_disabled_top": "#6B7280",
    "login_button_disabled_bottom": "#4B5563",
    "login_button_disabled_text": "#E5E7EB",
}


def login_theme_type() -> str:
    """Return the fixed login theme, independently of runtime preferences."""
    return "light"


def active_theme_type(state=None) -> str:
    """Return the protected app theme from its single session-state source.

    A missing key always means light, regardless of the browser, operating system,
    or Streamlit Settings preference. ``state`` is injectable for deterministic
    state tests and defaults to Streamlit's current session state.
    """
    state = st.session_state if state is None else state
    return "dark" if state.get(THEME_STATE_KEY, False) is True else "light"


def initialize_theme_state(state=None) -> bool:
    """Initialize a new protected-app session to light without overwriting a choice."""
    state = st.session_state if state is None else state
    state.setdefault(THEME_STATE_KEY, False)
    return bool(state[THEME_STATE_KEY])


OVERVIEW_THEME = {
    "light": {
        "card_outer_bg": "#F8FAFC",
        "card_bg": "#FFFFFF",
        "card_outer_border": "#E2E8F0",
        "card_shadow": "0 8px 24px rgba(15, 23, 42, 0.06)",
        "card_shadow_hover": "0 14px 30px rgba(15, 23, 42, 0.10)",
        "text": "#0F172A",
        "label_muted": "#64748B",
        "badge_up_bg": "#DCFCE7",
        "badge_up_text": "#15803D",
        "badge_down_bg": "#FEE2E2",
        "badge_down_text": "#B91C1C",
        "badge_neutral_bg": "#F1F5F9",
        "badge_neutral_text": "#475569",
        "icon_tile_bg": "#DCFCE7",
        "icon_tile_fg": "#15803D",
        "chart_palette": ("#16C060", "#3DB2A0", "#94A3B8", "#CBD5E1"),
        "chart_grid": "#E2E8F0",
        "chart_grid_subtle": "rgba(226, 232, 240, 0.58)",
        "chart_tooltip_bg": "#FFFFFF",
        "chart_tooltip_text": "#0F172A",
    },
    "dark": {
        "card_outer_bg": "#172033",
        "card_bg": "#1E293B",
        "card_outer_border": "#334155",
        "card_shadow": "0 8px 24px rgba(0, 0, 0, 0.24)",
        "card_shadow_hover": "0 14px 32px rgba(0, 0, 0, 0.36)",
        "text": "#F1F5F9",
        "label_muted": "#CBD5E1",
        "badge_up_bg": "rgba(22, 192, 96, 0.18)",
        "badge_up_text": "#6EE7A2",
        "badge_down_bg": "rgba(239, 68, 68, 0.18)",
        "badge_down_text": "#FCA5A5",
        "badge_neutral_bg": "#1E293B",
        "badge_neutral_text": "#CBD5E1",
        "icon_tile_bg": "rgba(22, 192, 96, 0.16)",
        "icon_tile_fg": "#6EE7A2",
        "chart_palette": ("#16C060", "#3DB2A0", "#94A3B8", "#CBD5E1"),
        "chart_grid": "#334155",
        "chart_grid_subtle": "rgba(51, 65, 85, 0.56)",
        "chart_tooltip_bg": "#111827",
        "chart_tooltip_text": "#F1F5F9",
    },
}


SUMMARY_CARD_THEME = {
    "light": {
        "summary_card_bg": "#FDFEFE",
        "summary_card_highlight": "rgba(255, 255, 255, 0.96)",
        "summary_card_shadow": "0 16px 30px rgba(15, 23, 42, 0.09), 0 3px 8px rgba(15, 23, 42, 0.05), inset 0 1px 0 rgba(255, 255, 255, 0.94)",
        "summary_card_shadow_hover": "0 21px 38px rgba(15, 23, 42, 0.13), 0 5px 12px rgba(15, 23, 42, 0.07), inset 0 1px 0 rgba(255, 255, 255, 0.98)",
        "summary_card_text": "#111827",
        "summary_card_label": "#374151",
        "summary_card_caption": "#6B7280",
        "icon_tile_bg": "rgba(255, 255, 255, 0.64)",
        "icon_tile_border": "#CBD5E1",
        "icon_tile_fg": "#334155",
        "ring_track": "#E5E7EB",
        "ring_up": "#16A34A",
        "ring_down": "#DC2626",
        "ring_neutral": "#64748B",
    },
    "dark": {
        "summary_card_bg": "#1F232C",
        "summary_card_highlight": "rgba(255, 255, 255, 0.055)",
        "summary_card_shadow": "0 18px 34px rgba(0, 0, 0, 0.28), 0 4px 10px rgba(0, 0, 0, 0.20), inset 0 1px 0 rgba(255, 255, 255, 0.08)",
        "summary_card_shadow_hover": "0 24px 42px rgba(0, 0, 0, 0.38), 0 6px 14px rgba(0, 0, 0, 0.24), inset 0 1px 0 rgba(255, 255, 255, 0.10)",
        "summary_card_text": "#F8FAFC",
        "summary_card_label": "#E2E8F0",
        "summary_card_caption": "#AEB8C6",
        "icon_tile_bg": "rgba(255, 255, 255, 0.035)",
        "icon_tile_border": "#667085",
        "icon_tile_fg": "#E2E8F0",
        "ring_track": "#3B4250",
        "ring_up": "#4ADE80",
        "ring_down": "#F87171",
        "ring_neutral": "#94A3B8",
    },
}


TABLE_THEME = {
    "light": {
        "card_bg": "#FFFFFF",
        "card_shadow": "0 10px 28px rgba(15, 23, 42, 0.08)",
        "table_header_bg": "#46515F",
        "table_header_text": "#FFFFFF",
        "table_row_bg": "#FFFFFF",
        "table_row_alt_bg": "#F8FAFC",
        "table_row_hover": "#F1F5F9",
        "table_border": "#D9DEE5",
        "table_text": "#475569",
        "table_muted_text": "#64748B",
        "table_selected_bg": "#E8F5D8",
        "table_selected_check": "#2F855A",
        "table_footer_bg": "#FFFFFF",
        "table_page_bg": "#FFFFFF",
        "table_page_text": "#475569",
        "table_page_hover": "#EAF7FB",
        "table_page_active_bg": "#5BC0DE",
        "table_page_active_text": "#FFFFFF",
        "table_focus": "#2563EB",
    },
    "dark": {
        "card_bg": "#1B1F27",
        "card_shadow": "0 12px 30px rgba(0, 0, 0, 0.30)",
        "table_header_bg": "#E6EAF0",
        "table_header_text": "#20242D",
        "table_row_bg": "#1B1F27",
        "table_row_alt_bg": "#20242D",
        "table_row_hover": "#292F3A",
        "table_border": "#343B47",
        "table_text": "#F1F5F9",
        "table_muted_text": "#B8C0CC",
        "table_selected_bg": "#1F3A2A",
        "table_selected_check": "#6EE7A2",
        "table_footer_bg": "#1B1F27",
        "table_page_bg": "#20242D",
        "table_page_text": "#E6EAF0",
        "table_page_hover": "#2D3541",
        "table_page_active_bg": "#5BC0DE",
        "table_page_active_text": "#FFFFFF",
        "table_focus": "#93C5FD",
    },
}


TABLE_COMPONENT_CSS = """
.versal-table-root {
    width: 100%;
    min-width: 0;
    color: var(--table-text);
    font-family: var(--versal-font-family, Inter, system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif);
    font-variant-numeric: tabular-nums;
}

.versal-table-card {
    width: 100%;
    min-width: 0;
    overflow: hidden;
    border: 1px solid var(--table-border);
    border-radius: 14px;
    background: var(--table-card-bg);
    box-shadow: var(--table-card-shadow);
}

.versal-table-scroll {
    width: 100%;
    overflow-x: auto;
    overscroll-behavior-inline: contain;
    -webkit-overflow-scrolling: touch;
}

.versal-table {
    width: 100%;
    min-width: max-content;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 14px;
}

.versal-table th,
.versal-table td {
    min-width: 8rem;
    padding: 12px 16px;
    border-right: 1px solid var(--table-border);
    border-bottom: 1px solid var(--table-border);
    text-align: left;
    vertical-align: middle;
    white-space: nowrap;
}

.versal-table th:last-child,
.versal-table td:last-child {
    border-right: 0;
}

.versal-table tbody tr:last-child td {
    border-bottom: 0;
}

.versal-table thead th {
    position: sticky;
    top: 0;
    z-index: 2;
    padding: 0;
    background: var(--table-header-bg);
    color: var(--table-header-text);
}

.versal-table th:first-child,
.versal-table td:first-child {
    position: sticky;
    left: 0;
}

.versal-table thead th:first-child {
    z-index: 3;
    background: var(--table-header-bg);
}

.versal-table tbody td:first-child {
    z-index: 1;
    background: inherit;
}

.versal-table-sort {
    width: 100%;
    min-height: 44px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    padding: 12px 16px;
    border: 0;
    border-radius: 0;
    background: transparent;
    color: inherit;
    font: inherit;
    font-weight: 700;
    text-align: left;
    cursor: pointer;
}

.versal-table-sort:hover {
    background: color-mix(in srgb, var(--table-header-text) 10%, transparent);
}

.versal-table-sort:focus-visible,
.versal-table-page:focus-visible,
.versal-table-size:focus-visible {
    outline: 3px solid var(--table-focus);
    outline-offset: -3px;
}

.versal-table-sort-indicator {
    flex: 0 0 auto;
    font-size: 14px;
    opacity: 0.86;
}

.versal-table tbody tr {
    background: var(--table-row-bg);
    color: var(--table-text);
}

.versal-table tbody tr:nth-child(even) {
    background: var(--table-row-alt-bg);
}

.versal-table tbody tr:hover {
    background: var(--table-row-hover);
}

.versal-table-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
    min-height: 56px;
    padding: 10px 14px;
    border-top: 1px solid var(--table-border);
    background: var(--table-footer-bg);
    color: var(--table-muted-text);
    font-size: 12px;
}

.versal-table-controls,
.versal-table-pagination {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px;
}

.versal-table-size {
    min-height: 40px;
    padding: 7px 30px 7px 10px;
    border: 1px solid var(--table-border);
    border-radius: 8px;
    background: var(--table-page-bg);
    color: var(--table-page-text);
    font: inherit;
}

.versal-table-page {
    min-width: 40px;
    min-height: 40px;
    padding: 7px 10px;
    border: 1px solid var(--table-border);
    border-radius: 999px;
    background: var(--table-page-bg);
    color: var(--table-page-text);
    font: inherit;
    font-weight: 650;
    cursor: pointer;
}

.versal-table-page:hover:not(:disabled) {
    background: var(--table-page-hover);
}

.versal-table-page.is-active {
    border-color: var(--table-page-active-bg);
    background: var(--table-page-active-bg);
    color: var(--table-page-active-text);
}

.versal-table-page:disabled {
    cursor: not-allowed;
    opacity: 0.45;
}

.versal-table-ellipsis {
    min-width: 28px;
    text-align: center;
}

.versal-table-empty {
    padding: 28px 18px;
    border: 1px solid var(--table-border);
    border-radius: 14px;
    background: var(--table-card-bg);
    box-shadow: var(--table-card-shadow);
    color: var(--table-muted-text);
    text-align: center;
    font-size: 14px;
}

@media (max-width: 480px) {
    .versal-table th,
    .versal-table td,
    .versal-table-sort {
        padding: 11px 12px;
    }

    .versal-table-footer {
        align-items: flex-start;
    }

    .versal-table-controls,
    .versal-table-pagination {
        width: 100%;
    }

    .versal-table-pagination {
        justify-content: flex-start;
    }
}
"""


def active_table_theme() -> dict[str, str]:
    """Return table colours for the app's active runtime theme."""
    return TABLE_THEME[active_theme_type()]


def active_overview_theme() -> dict[str, object]:
    """Return Overview colours matching the app's current runtime selection."""
    return OVERVIEW_THEME[active_theme_type()]


def active_summary_card_theme() -> dict[str, str]:
    """Return Ask the Business summary-card colours for the active theme."""
    return SUMMARY_CARD_THEME[active_theme_type()]


def active_runtime_theme() -> dict[str, str]:
    """Return the current main-content palette selected by the sidebar toggle."""
    return RUNTIME_THEME[active_theme_type()]


def apply_runtime_theme() -> None:
    """Inject the active protected-page palette once, before page rendering."""
    palette = active_runtime_theme()
    st.html(
        f"""
        <style id="versal-runtime-theme">
        :root {{
            color-scheme: {palette["color_scheme"]};
            --background-color: {palette["background"]} !important;
            --secondary-background-color: {palette["secondary_background"]} !important;
            --text-color: {palette["text"]} !important;
            --muted-text-color: {palette["muted_text"]} !important;
            --border-color: {palette["border"]} !important;
        }}

        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {{
            background-color: {palette["background"]} !important;
            color: {palette["text"]} !important;
        }}

        [data-testid="stHeader"] {{
            background-color: transparent !important;
        }}

        [data-testid="stVerticalBlockBorderWrapper"],
        div[data-testid="stMetric"] {{
            border-color: {palette["border"]} !important;
        }}

        [data-testid="stMain"] h1,
        [data-testid="stMain"] h2,
        [data-testid="stMain"] h3,
        [data-testid="stMain"] h4,
        [data-testid="stMain"] h5,
        [data-testid="stMain"] h6,
        [data-testid="stMain"] [data-testid="stMarkdownContainer"],
        [data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stMain"] [data-testid="stMarkdownContainer"] li,
        [data-testid="stMain"] [data-testid="stMetricLabel"],
        [data-testid="stMain"] [data-testid="stMetricLabel"] *,
        [data-testid="stMain"] [data-testid="stMetricValue"],
        [data-testid="stMain"] [data-testid="stMetricValue"] *,
        [data-testid="stMain"] label,
        [data-testid="stMain"] legend {{
            color: {palette["text"]} !important;
        }}

        [data-testid="stMain"] [data-testid="stCaptionContainer"],
        [data-testid="stMain"] [data-testid="stCaptionContainer"] *,
        [data-testid="stMain"] small {{
            color: {palette["muted_text"]} !important;
        }}

        [data-testid="stMain"] div[data-testid="stMetric"],
        [data-testid="stMain"] [data-testid="stExpander"],
        [data-testid="stMain"] [data-testid="stExpander"] details {{
            background-color: {palette["secondary_background"]} !important;
            border-color: {palette["border"]} !important;
            color: {palette["text"]} !important;
        }}

        [data-testid="stMain"] input,
        [data-testid="stMain"] textarea,
        [data-testid="stMain"] [data-baseweb="select"] > div,
        [data-testid="stMain"] [data-baseweb="base-input"] {{
            background-color: {palette["secondary_background"]} !important;
            border-color: {palette["border"]} !important;
            color: {palette["text"]} !important;
        }}

        [data-testid="stMain"] input,
        [data-testid="stMain"] textarea,
        [data-testid="stMain"] [data-baseweb="select"] *,
        [data-testid="stMain"] [data-baseweb="base-input"] *,
        [data-testid="stMain"] [data-testid="stExpander"] * {{
            color: {palette["text"]} !important;
        }}

        [data-testid="stMain"] [data-testid="stDataFrame"],
        [data-testid="stMain"] [data-testid="stTable"] {{
            color: {palette["text"]} !important;
            border-color: {palette["border"]} !important;
        }}

        [data-testid="stMain"] [data-testid="stDownloadButton"] button {{
            min-height: 2.75rem;
            background-color: {palette["secondary_background"]} !important;
            border-color: {palette["border"]} !important;
            color: {palette["text"]} !important;
            opacity: 1 !important;
        }}

        [data-testid="stMain"] [data-testid="stDownloadButton"] button * {{
            color: {palette["text"]} !important;
            fill: currentColor !important;
            opacity: 1 !important;
        }}

        [data-testid="stMain"] [data-testid="stDownloadButton"] button:hover {{
            background-color: color-mix(
                in srgb,
                {palette["secondary_background"]} 88%,
                {palette["text"]}
            ) !important;
        }}

        [data-testid="stMain"] [data-testid="stDownloadButton"] button:focus-visible {{
            outline: 3px solid {palette["focus"]} !important;
            outline-offset: 2px;
        }}

        [data-baseweb="popover"],
        [data-baseweb="tooltip"],
        [role="tooltip"],
        [data-testid="stTooltipContent"] {{
            background-color: {palette["secondary_background"]} !important;
            border-color: {palette["border"]} !important;
            color: {palette["text"]} !important;
        }}

        [data-baseweb="popover"] *,
        [data-baseweb="tooltip"] *,
        [role="tooltip"] *,
        [data-testid="stTooltipContent"] * {{
            color: {palette["text"]} !important;
        }}
        </style>
        """
    )


def apply_ask_business_theme() -> None:
    """Keep Ask the Business controls readable in both runtime themes."""
    palette = active_runtime_theme()
    st.html(
        f"""
        <style>
        [class*="st-key-quick_"] button {{
            min-height: 2.5rem;
            border-color: {palette["border"]} !important;
            background: {palette["secondary_background"]} !important;
            color: {palette["text"]} !important;
        }}

        [class*="st-key-quick_"] button * {{
            color: {palette["text"]} !important;
            opacity: 1 !important;
        }}

        [class*="st-key-quick_"] button:hover {{
            border-color: {palette["muted_text"]} !important;
            background: color-mix(
                in srgb,
                {palette["secondary_background"]} 88%,
                {palette["text"]}
            ) !important;
        }}

        [class*="st-key-quick_"] button:focus-visible {{
            outline: 3px solid {palette["muted_text"]};
            outline-offset: 2px;
        }}

        [class*="st-key-clear_business_chat"] button {{
            border-color: {palette["border"]} !important;
            background: transparent !important;
            color: {palette["text"]} !important;
        }}

        [class*="st-key-clear_business_chat"] button * {{
            color: {palette["text"]} !important;
            opacity: 1 !important;
        }}

        [class*="st-key-clear_business_chat"] button:hover {{
            background: color-mix(
                in srgb,
                {palette["secondary_background"]} 82%,
                transparent
            ) !important;
        }}

        [class*="st-key-clear_business_chat"] button:focus-visible {{
            outline: 3px solid {palette["muted_text"]};
            outline-offset: 2px;
        }}

        [data-testid="stChatInput"] {{
            border-color: {palette["border"]} !important;
            background: {palette["secondary_background"]} !important;
        }}

        [data-testid="stChatInput"] textarea {{
            background: transparent !important;
            color: {palette["text"]} !important;
            caret-color: {palette["text"]} !important;
        }}

        [data-testid="stChatInput"] textarea::placeholder {{
            color: {palette["muted_text"]} !important;
            opacity: 1 !important;
        }}

        [data-testid="stChatInput"] button,
        [data-testid="stChatInput"] button * {{
            color: {palette["text"]} !important;
        }}

        [data-baseweb="tab-list"] [data-baseweb="tab"],
        [data-baseweb="tab-list"] [data-baseweb="tab"] * {{
            color: {palette["text"]} !important;
        }}
        </style>
        """
    )


def apply_summary_card_theme() -> None:
    """Style only the four summary cards on Ask the Business."""
    palette = active_summary_card_theme()
    st.html(
        f"""
        <style>
        [class*="st-key-ask_summary_"] {{
            min-width: min(100%, 12rem);
            flex: 1 1 12rem;
        }}

        [class*="st-key-ask_summary_"] .versal-summary-card {{
            box-sizing: border-box;
            min-height: 178px;
            height: 100%;
            padding: 1.2rem 1.25rem 1.15rem;
            overflow: hidden;
            border: 0;
            border-radius: 22px;
            background:
                linear-gradient(180deg, {palette["summary_card_highlight"]} 0%, transparent 42%),
                {palette["summary_card_bg"]};
            box-shadow: {palette["summary_card_shadow"]};
            color: {palette["summary_card_text"]};
            transition: transform 180ms ease, box-shadow 180ms ease;
        }}

        [class*="st-key-ask_summary_"] .versal-summary-card:hover {{
            transform: translateY(-3px);
            box-shadow: {palette["summary_card_shadow_hover"]};
        }}

        [class*="st-key-ask_summary_"] .versal-summary-head {{
            min-height: 46px;
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            margin-bottom: 0.8rem;
        }}

        [class*="st-key-ask_summary_"] .versal-summary-icon {{
            width: 42px;
            height: 42px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            flex: 0 0 auto;
            border: 1px solid {palette["icon_tile_border"]};
            border-radius: 12px;
            background: {palette["icon_tile_bg"]};
            color: {palette["icon_tile_fg"]};
        }}

        [class*="st-key-ask_summary_"] .versal-summary-icon .material-symbols-rounded {{
            color: inherit !important;
            direction: ltr;
            display: inline-block;
            font-family: "Material Symbols Rounded" !important;
            font-size: 1.25rem;
            font-style: normal;
            font-variation-settings: "FILL" 0, "wght" 450, "GRAD" 0, "opsz" 22;
            font-weight: normal;
            letter-spacing: normal;
            line-height: 1;
            text-transform: none;
            white-space: nowrap;
            word-wrap: normal;
            -webkit-font-feature-settings: "liga";
            font-feature-settings: "liga";
            -webkit-font-smoothing: antialiased;
        }}

        [class*="st-key-ask_summary_"] .versal-summary-label,
        [class*="st-key-ask_summary_"] .versal-summary-value,
        [class*="st-key-ask_summary_"] .versal-summary-caption {{
            margin: 0;
        }}

        [class*="st-key-ask_summary_"] .versal-summary-label-row {{
            display: flex;
            align-items: center;
            gap: 0.35rem;
        }}

        [class*="st-key-ask_summary_"] .versal-summary-help {{
            width: 1rem;
            height: 1rem;
            display: inline-grid;
            place-items: center;
            flex: 0 0 auto;
            border: 1px solid {palette["summary_card_caption"]};
            border-radius: 50%;
            color: {palette["summary_card_caption"]};
            font-size: 0.65rem;
            font-weight: 700;
            line-height: 1;
            cursor: help;
        }}

        [class*="st-key-ask_summary_"] .versal-summary-label {{
            color: {palette["summary_card_label"]};
            font-size: 0.94rem;
            font-weight: 600;
            line-height: 1.35;
        }}

        [class*="st-key-ask_summary_"] .versal-summary-value {{
            margin-top: 0.28rem;
            color: {palette["summary_card_text"]};
            font-size: clamp(1.7rem, 2.2vw, 2rem);
            font-weight: 750;
            line-height: 1.12;
            letter-spacing: -0.025em;
            white-space: nowrap;
        }}

        [class*="st-key-ask_summary_"] .versal-summary-caption {{
            margin-top: 0.48rem;
            color: {palette["summary_card_caption"]};
            font-size: 0.75rem;
            line-height: 1.45;
        }}

        [class*="st-key-ask_summary_"] .versal-summary-ring {{
            position: relative;
            width: 46px;
            height: 46px;
            flex: 0 0 auto;
            display: grid;
            place-items: center;
            color: {palette["ring_neutral"]};
        }}

        [class*="st-key-ask_summary_"] .versal-summary-ring svg {{
            position: absolute;
            inset: 0;
            width: 100%;
            height: 100%;
        }}

        [class*="st-key-ask_summary_"] .versal-summary-ring circle {{
            fill: none;
            stroke-width: 3;
        }}

        [class*="st-key-ask_summary_"] .versal-summary-ring-track {{
            stroke: {palette["ring_track"]};
        }}

        [class*="st-key-ask_summary_"] .versal-summary-ring-value {{
            stroke: currentColor;
            stroke-linecap: round;
            transform: rotate(-90deg);
            transform-origin: center;
        }}

        [class*="st-key-ask_summary_"] .versal-summary-ring-dot {{
            fill: currentColor;
            stroke: none;
        }}

        [class*="st-key-ask_summary_"] .versal-summary-ring--up {{ color: {palette["ring_up"]}; }}
        [class*="st-key-ask_summary_"] .versal-summary-ring--down {{ color: {palette["ring_down"]}; }}
        [class*="st-key-ask_summary_"] .versal-summary-ring--neutral {{ color: {palette["ring_neutral"]}; }}

        [class*="st-key-ask_summary_"] .versal-summary-ring span {{
            position: relative;
            color: {palette["summary_card_text"]};
            font-size: 0.62rem;
            font-weight: 700;
        }}

        @media (min-width: 641px) and (max-width: 900px) {{
            [class*="st-key-ask_summary_"] {{
                min-width: calc(50% - 0.5rem);
                flex-basis: calc(50% - 0.5rem);
            }}
        }}

        @media (max-width: 640px) {{
            [class*="st-key-ask_summary_"] {{
                min-width: 100%;
                flex-basis: 100%;
            }}

            [class*="st-key-ask_summary_"] .versal-summary-card {{
                min-height: 160px;
                padding: 1.05rem 1.1rem;
            }}
        }}
        </style>
        """
    )


def apply_overview_theme() -> None:
    """Apply styling scoped exclusively to the Business Overview page."""
    palette = active_overview_theme()
    st.html(
        f"""
        <style>
        [class*="st-key-overview_kpi_"] .versal-overview-kpi-outer {{
            padding: 0.42rem;
            border: 1px solid {palette["card_outer_border"]};
            border-radius: 20px;
            background: {palette["card_outer_bg"]};
            box-shadow: {palette["card_shadow"]};
            transition: transform 180ms ease, box-shadow 180ms ease;
        }}

        [class*="st-key-overview_kpi_"] .versal-overview-kpi-outer:hover {{
            transform: translateY(-2px);
            box-shadow: {palette["card_shadow_hover"]};
        }}

        [class*="st-key-overview_kpi_"] .versal-overview-kpi-inner {{
            min-height: 188px;
            padding: 1.15rem 1.2rem 1rem;
            border-radius: 15px;
            background: {palette["card_bg"]};
            color: {palette["text"]};
        }}

        .versal-overview-kpi-head,
        .versal-overview-kpi-value-row,
        .versal-overview-kpi-footer,
        .versal-overview-chart-head {{
            display: flex;
            align-items: center;
        }}

        .versal-overview-kpi-head,
        .versal-overview-kpi-footer,
        .versal-overview-chart-head {{
            justify-content: space-between;
        }}

        .versal-overview-kpi-label,
        .versal-overview-chart-eyebrow {{
            margin: 0;
            color: {palette["label_muted"]} !important;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            line-height: 1.2;
            text-transform: uppercase;
        }}

        .versal-overview-icon-tile {{
            width: 2rem;
            height: 2rem;
            flex: 0 0 2rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border: 1px solid color-mix(in srgb, {palette["icon_tile_fg"]} 28%, transparent);
            border-radius: 0.58rem;
            background: {palette["icon_tile_bg"]};
            color: {palette["icon_tile_fg"]};
        }}

        .versal-overview-icon-tile .material-symbols-rounded {{
            color: inherit !important;
            direction: ltr;
            display: inline-block;
            font-family: "Material Symbols Rounded" !important;
            font-size: 1.15rem;
            font-style: normal;
            font-variation-settings: "FILL" 0, "wght" 450, "GRAD" 0, "opsz" 20;
            font-weight: normal;
            letter-spacing: normal;
            line-height: 1;
            text-transform: none;
            white-space: nowrap;
            word-wrap: normal;
            -webkit-font-feature-settings: "liga";
            font-feature-settings: "liga";
            -webkit-font-smoothing: antialiased;
        }}

        .versal-overview-kpi-value-row {{
            flex-wrap: wrap;
            gap: 0.55rem;
            margin-top: 0.55rem;
        }}

        .versal-overview-kpi-value {{
            color: {palette["text"]};
            font-size: clamp(1.55rem, 2.5vw, 1.85rem);
            font-weight: 750;
            letter-spacing: -0.025em;
            line-height: 1.15;
        }}

        .versal-overview-change {{
            display: inline-flex;
            align-items: center;
            gap: 0.2rem;
            padding: 0.22rem 0.5rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 700;
            white-space: nowrap;
        }}

        .versal-overview-change--up {{
            background: {palette["badge_up_bg"]};
            color: {palette["badge_up_text"]};
        }}

        .versal-overview-change--down {{
            background: {palette["badge_down_bg"]};
            color: {palette["badge_down_text"]};
        }}

        .versal-overview-change--neutral {{
            background: {palette["badge_neutral_bg"]};
            color: {palette["badge_neutral_text"]};
        }}

        .versal-overview-kpi-question {{
            min-height: 2.5rem;
            margin: 0.75rem 0 0;
            color: {palette["label_muted"]} !important;
            font-size: 0.82rem;
            line-height: 1.45;
        }}

        .versal-overview-kpi-divider {{
            height: 1px;
            margin: 0.75rem 0 0.65rem;
            background: {palette["card_outer_border"]};
        }}

        .versal-overview-kpi-footer {{
            gap: 0.55rem;
            color: {palette["label_muted"]};
            font-size: 0.76rem;
        }}

        .versal-overview-kpi-footer-copy {{
            min-width: 0;
            display: flex;
            flex-wrap: wrap;
            gap: 0.25rem;
        }}

        .versal-overview-kpi-footer strong {{
            color: {palette["text"]};
        }}

        [class*="st-key-overview_chart_outer_"] {{
            margin-top: 1rem;
            padding: 0.42rem;
            border: 1px solid {palette["card_outer_border"]};
            border-radius: 20px !important;
            background: {palette["card_outer_bg"]};
            box-shadow: {palette["card_shadow"]};
        }}

        [class*="st-key-overview_chart_inner_"] {{
            padding: 1rem 1rem 0.35rem;
            border-radius: 15px !important;
            background: {palette["card_bg"]};
        }}

        .versal-overview-chart-copy {{
            min-width: 0;
        }}

        .versal-overview-chart-title {{
            margin: 0.22rem 0 0;
            color: {palette["text"]};
            font-size: 1.15rem;
            font-weight: 700;
            line-height: 1.3;
        }}

        .versal-overview-chart-caption {{
            margin: 0.3rem 0 0;
            color: {palette["label_muted"]} !important;
            font-size: 0.82rem;
            line-height: 1.45;
        }}

        [class*="st-key-overview_chart_inner_"] [data-testid="stPlotlyChart"] {{
            border: 0 !important;
            border-radius: 0 !important;
            overflow: hidden;
        }}

        @media (max-width: 480px) {{
            [class*="st-key-overview_kpi_"] .versal-overview-kpi-inner {{
                min-height: 176px;
                padding: 1rem;
            }}

            [class*="st-key-overview_chart_inner_"] {{
                padding-inline: 0.7rem;
            }}

            .versal-overview-kpi-value {{
                font-size: 1.5rem;
            }}
        }}
        </style>
        """
    )


def apply_login_theme() -> None:
    """Force the login route to the existing light palette only."""
    # Keep the next authenticated render light as well. These are UI preference
    # keys only; authentication state remains owned by ``src.auth.auth``.
    st.session_state["sidebar_dark_mode"] = False
    st.session_state["sidebar_theme_context"] = False
    apply_typography()
    st.html(
        """
        <span id="versal-theme-bootstrap" hidden></span>
        <script>
        (() => {
            const themeKeys = Object.keys(localStorage).filter((key) =>
                key.startsWith("stActiveTheme-")
            );
            for (const key of themeKeys) {
                const oldValue = localStorage.getItem(key);
                const newValue = JSON.stringify("Light");
                if (oldValue === newValue) continue;
                localStorage.setItem(key, newValue);
                window.dispatchEvent(new StorageEvent("storage", {
                    key,
                    oldValue,
                    newValue,
                    storageArea: localStorage,
                    url: window.location.href,
                }));
            }
            document.documentElement.style.colorScheme = "light";
            document.documentElement.dataset.versalLoginTheme = "light";
        })();
        </script>
        """,
        unsafe_allow_javascript=True,
    )
    glass = LOGIN_THEME

    st.html(
        f"""
        <style>
        html:has(body [class*="st-key-login_shell"]) {{
            color-scheme: light !important;
            --background-color: {glass["page_background"]} !important;
            --secondary-background-color: {glass["field_background"]} !important;
            --text-color: {glass["text"]} !important;
        }}

        body:has([class*="st-key-login_shell"]) [data-testid="stSidebar"],
        body:has([class*="st-key-login_shell"]) [data-testid="stSidebarCollapsedControl"],
        body:has([class*="st-key-login_shell"]) [data-testid="stExpandSidebarButton"],
        body:has([class*="st-key-login_shell"]) [data-testid="stHeader"],
        body:has([class*="st-key-login_shell"]) [data-testid="stToolbar"],
        body:has([class*="st-key-login_shell"]) footer {{
            display: none !important;
        }}

        body:has([class*="st-key-login_shell"]) .stApp,
        body:has([class*="st-key-login_shell"]) [data-testid="stAppViewContainer"],
        body:has([class*="st-key-login_shell"]) [data-testid="stMain"] {{
            background-color: {glass["page_background"]} !important;
            background-image: none !important;
            color: {glass["text"]} !important;
            height: 100dvh;
            overflow: hidden !important;
        }}

        body:has([class*="st-key-login_shell"]) [data-testid="stHeader"] {{
            background: {glass["page_background"]} !important;
        }}

        body:has([class*="st-key-login_shell"]),
        body:has([class*="st-key-login_shell"]) [data-testid="stToast"],
        body:has([class*="st-key-login_shell"]) [data-baseweb="toast"],
        body:has([class*="st-key-login_shell"]) [data-testid="stDialog"] [role="dialog"],
        body:has([class*="st-key-login_shell"]) [data-baseweb="modal"] [role="dialog"] {{
            background-color: {glass["field_background"]} !important;
            color: {glass["text"]} !important;
        }}

        body:has([class*="st-key-login_shell"]) [data-testid="stToast"] *,
        body:has([class*="st-key-login_shell"]) [data-baseweb="toast"] *,
        body:has([class*="st-key-login_shell"]) [data-testid="stDialog"] [role="dialog"] *,
        body:has([class*="st-key-login_shell"]) [data-baseweb="modal"] [role="dialog"] * {{
            color: {glass["text"]} !important;
        }}

        html:has(body [class*="st-key-login_shell"]),
        body:has([class*="st-key-login_shell"]),
        body:has([class*="st-key-login_shell"]) [data-testid="stAppViewContainer"] > .main {{
            height: 100dvh;
            overflow: hidden !important;
        }}

        body:has([class*="st-key-login_shell"]) .block-container {{
            width: 100%;
            max-width: 100% !important;
            padding: 1rem !important;
            height: 100dvh;
            overflow: hidden !important;
        }}

        [class*="st-key-login_shell"] {{
            width: 100%;
            height: calc(100dvh - 2rem);
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            isolation: isolate;
        }}

        [class*="st-key-login_shell"] > div {{
            width: 100%;
            position: relative;
            z-index: 1;
        }}

        [class*="st-key-login_shell"]::before,
        [class*="st-key-login_shell"]::after {{
            content: "";
            position: absolute;
            z-index: 0;
            width: min(46vw, 520px);
            aspect-ratio: 1;
            border-radius: 50%;
            filter: blur(42px);
            opacity: 0.9;
            pointer-events: none;
        }}

        [class*="st-key-login_shell"]::before {{
            top: -18%;
            left: 8%;
            background: {glass["shape_one"]};
        }}

        [class*="st-key-login_shell"]::after {{
            right: 7%;
            bottom: -22%;
            background: {glass["shape_two"]};
        }}

        [class*="st-key-login_card"] {{
            width: min(100%, 420px);
            margin-inline: auto;
            padding: 1.5rem 2rem;
            border: 1px solid {glass["card_border"]};
            border-radius: 16px !important;
            background: {glass["card_background"]};
            color: {glass["text"]};
            box-shadow: {glass["card_shadow"]};
            -webkit-backdrop-filter: blur(18px) saturate(140%);
            backdrop-filter: blur(18px) saturate(140%);
        }}

        @supports not ((-webkit-backdrop-filter: blur(1px)) or
                       (backdrop-filter: blur(1px))) {{
            [class*="st-key-login_card"] {{
                background: {glass["fallback_background"]};
            }}
        }}

        [class*="st-key-login_card"] h1 {{
            color: {glass["text"]};
            font-size: clamp(1.45rem, 4vw, 1.9rem);
            line-height: 1.2;
            margin-bottom: 0;
        }}

        [class*="st-key-login_card"] label,
        [class*="st-key-login_card"] p {{
            color: {glass["text"]};
        }}

        [class*="st-key-login_card"] [data-baseweb="input"] {{
            min-height: 3rem;
            border-color: {glass["field_border"]};
            background: {glass["field_background"]};
        }}

        [class*="st-key-login_card"] [data-baseweb="input"] input {{
            color: {glass["text"]};
            -webkit-text-fill-color: {glass["text"]};
        }}

        [class*="st-key-login_card"] [data-baseweb="input"] input::placeholder {{
            color: {glass["muted_text"]};
            opacity: 0.82;
        }}

        :is(
            [class*="st-key-sign_in"] button,
            [class*="st-key-login_card"] [data-testid="stButton"] button[data-testid="stBaseButton-primary"]
        ) {{
            min-height: 3.375rem;
            height: 3.375rem;
            padding: 0.75rem 1.25rem;
            border: 0 !important;
            border-radius: 13px !important;
            background: linear-gradient(
                180deg,
                {glass["login_button_bg_top"]} 0%,
                {glass["login_button_bg_bottom"]} 100%
            ) !important;
            box-shadow:
                {glass["login_button_shadow"]},
                {glass["login_button_highlight"]} !important;
            color: {glass["login_button_text"]} !important;
            font-size: 0.925rem;
            font-weight: 600;
            letter-spacing: 0.12em;
            line-height: 1;
            text-transform: uppercase;
            white-space: nowrap;
            gap: 0;
            transform: translateY(0);
            transition:
                background 160ms ease,
                box-shadow 160ms ease,
                transform 160ms ease,
                opacity 160ms ease;
        }}

        :is(
            [class*="st-key-sign_in"] button,
            [class*="st-key-login_card"] [data-testid="stButton"] button[data-testid="stBaseButton-primary"]
        ) * {{
            color: {glass["login_button_text"]} !important;
            font: inherit;
            letter-spacing: inherit;
            text-transform: inherit;
            white-space: nowrap;
        }}

        :is(
            [class*="st-key-sign_in"] button,
            [class*="st-key-login_card"] [data-testid="stButton"] button[data-testid="stBaseButton-primary"]
        ) [data-testid="stIconMaterial"] {{
            display: none !important;
        }}

        :is(
            [class*="st-key-sign_in"] button,
            [class*="st-key-login_card"] [data-testid="stButton"] button[data-testid="stBaseButton-primary"]
        ):hover:not(:disabled) {{
            background: linear-gradient(
                180deg,
                {glass["login_button_hover"]} 0%,
                {glass["login_button_bg_top"]} 100%
            ) !important;
            box-shadow:
                {glass["login_button_hover_shadow"]},
                {glass["login_button_highlight"]} !important;
            transform: translateY(-2px);
        }}

        :is(
            [class*="st-key-sign_in"] button,
            [class*="st-key-login_card"] [data-testid="stButton"] button[data-testid="stBaseButton-primary"]
        ):active:not(:disabled) {{
            background: linear-gradient(
                180deg,
                {glass["login_button_bg_top"]} 0%,
                {glass["login_button_bg_bottom"]} 100%
            ) !important;
            box-shadow:
                {glass["login_button_pressed_shadow"]},
                {glass["login_button_highlight"]} !important;
            transform: translateY(0);
        }}

        :is(
            [class*="st-key-sign_in"] button,
            [class*="st-key-login_card"] [data-testid="stButton"] button[data-testid="stBaseButton-primary"]
        ):focus-visible {{
            outline: 3px solid {glass["login_button_focus"]} !important;
            outline-offset: 3px;
        }}

        :is(
            [class*="st-key-sign_in"] button,
            [class*="st-key-login_card"] [data-testid="stButton"] button[data-testid="stBaseButton-primary"]
        ):disabled {{
            background: linear-gradient(
                180deg,
                {glass["login_button_disabled_top"]} 0%,
                {glass["login_button_disabled_bottom"]} 100%
            ) !important;
            box-shadow: none !important;
            color: {glass["login_button_disabled_text"]} !important;
            cursor: not-allowed !important;
            opacity: 0.62;
            transform: none;
        }}

        [class*="st-key-forgot_password_row"] button {{
            min-height: auto;
            padding: 0.15rem 0 !important;
            color: {glass["accent"]} !important;
            font-weight: 650;
        }}

        .versal-login-subtitle {{
            margin: -0.15rem 0 0.4rem;
            color: {glass["muted_text"]} !important;
            text-align: center;
            font-size: 0.98rem;
        }}

        @media (max-width: 480px) {{
            body:has([class*="st-key-login_shell"]) .block-container {{
                padding: 0.75rem !important;
            }}

            [class*="st-key-login_shell"] {{
                height: calc(100dvh - 1.5rem);
            }}

            [class*="st-key-login_card"] {{
                padding: 1.1rem;
                border-radius: 14px !important;
            }}

            [class*="st-key-login_shell"]::before,
            [class*="st-key-login_shell"]::after {{
                width: 72vw;
                filter: blur(32px);
            }}
        }}
        </style>
        """
    )


def hide_landing_navigation() -> None:
    """Hide sidebar navigation and its reveal control on the landing route only."""
    st.html(
        """
        <style>
        body:has([class*="st-key-public_landing_shell"]) [data-testid="stSidebar"],
        body:has([class*="st-key-public_landing_shell"]) [data-testid="stSidebarCollapsedControl"],
        body:has([class*="st-key-public_landing_shell"]) [data-testid="stExpandSidebarButton"] {
            display: none !important;
        }
        </style>
        """
    )


def apply_public_landing_theme() -> None:
    """Apply the fixed public landing design without reading runtime theme state."""
    palette = PUBLIC_LANDING_THEME
    hide_landing_navigation()
    apply_typography()
    st.html(
        f"""
        <style id="versal-public-landing-theme">
        html:root {{
            color-scheme: light !important;
        }}

        .stApp:has([class*="st-key-public_landing_shell"]),
        [data-testid="stAppViewContainer"]:has([class*="st-key-public_landing_shell"]),
        [data-testid="stMain"]:has([class*="st-key-public_landing_shell"]) {{
            background: {palette["landing_band_bg"]} !important;
            color: {palette["landing_card_text"]} !important;
            font-family: var(--versal-font-family) !important;
        }}

        [data-testid="stAppViewContainer"]:has([class*="st-key-public_landing_shell"])
        .block-container {{
            width: 100% !important;
            max-width: none !important;
            min-height: 100dvh !important;
            padding: 0 !important;
            overflow-x: hidden !important;
        }}

        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        footer {{
            display: none !important;
        }}

        [class*="st-key-public_landing_shell"] {{
            --versal-anim-duration: {palette["landing_anim_duration"]};
            --versal-anim-stagger: {palette["landing_anim_stagger"]};
            --versal-anim-distance: {palette["landing_anim_distance"]};
            --versal-icon-sweep: {palette["landing_icon_sweep"]};
            --versal-wave-duration: {palette["landing_wave_duration"]};
            --versal-hover-duration: {palette["landing_hover_duration"]};
            --versal-cards-offset: -2.8rem;
            width: 100%;
            min-height: 100dvh;
            margin: 0;
            padding: 0;
            gap: 0 !important;
            overflow: hidden;
            background: {palette["landing_band_bg"]};
        }}

        [class*="st-key-public_landing_hero"] {{
            position: relative;
            min-height: clamp(500px, 68dvh, 690px);
            padding: clamp(1.2rem, 3vw, 2.2rem) clamp(1rem, 5vw, 2.5rem)
                     clamp(5rem, 11vh, 7.2rem) !important;
            box-sizing: border-box;
            overflow: hidden;
            isolation: isolate;
            border: 0 !important;
            border-radius: 0 !important;
            background: linear-gradient(
                118deg,
                {palette["landing_gradient_start"]} 0%,
                {palette["landing_gradient_end"]} 100%
            ) !important;
        }}

        [class*="st-key-public_landing_topbar"],
        [class*="st-key-public_landing_copy"] {{
            position: relative;
            z-index: 2;
            width: min(100%, 1100px);
            margin-inline: auto;
        }}

        [class*="st-key-public_landing_topbar"] {{
            align-items: center;
            gap: 1rem !important;
        }}

        [class*="st-key-public_landing_topbar"]
        > [data-testid="stElementContainer"]:first-child {{
            flex: 0 1 220px;
        }}

        .versal-public-logo {{
            display: block;
            width: clamp(140px, 18vw, 210px);
            max-width: 100%;
            height: auto;
        }}

        [class*="st-key-public_landing_sign_in"] button {{
            min-width: 7.6rem;
            min-height: 2.6rem;
            justify-content: center;
            padding: 0.55rem 1.35rem;
            border: 1px solid {palette["landing_button_border"]} !important;
            border-radius: 999px !important;
            background: transparent !important;
            box-shadow: none !important;
            color: {palette["landing_text"]} !important;
            font-size: 0.95rem;
            font-weight: 650;
            transition: background-color var(--versal-hover-duration) ease,
                        transform var(--versal-hover-duration) ease;
        }}

        [class*="st-key-public_landing_sign_in"] button * {{
            color: {palette["landing_text"]} !important;
        }}

        [class*="st-key-public_landing_sign_in"] button:hover {{
            background: rgba(255, 255, 255, 0.12) !important;
            transform: translateY(-1px);
        }}

        [class*="st-key-public_landing_sign_in"] button:active {{
            background: rgba(255, 255, 255, 0.18) !important;
            transform: translateY(0);
        }}

        [class*="st-key-public_landing_sign_in"] button:focus-visible {{
            outline: 3px solid {palette["landing_focus"]} !important;
            outline-offset: 3px;
        }}

        [class*="st-key-public_landing_copy"] {{
            margin-top: clamp(3.4rem, 8vh, 6.3rem);
        }}

        .versal-public-copy {{
            max-width: 690px;
        }}

        .versal-public-copy h1 {{
            max-width: 660px;
            margin: 0;
            color: {palette["landing_text"]} !important;
            font-size: clamp(3.45rem, 6vw, 4rem);
            font-weight: 800;
            letter-spacing: -0.045em;
            line-height: 0.99;
            text-wrap: balance;
        }}

        .versal-public-copy p {{
            max-width: 590px;
            margin: 1.55rem 0 0;
            color: {palette["landing_text_muted"]} !important;
            font-size: clamp(1rem, 1.8vw, 1.12rem);
            line-height: 1.72;
        }}

        .versal-public-analytics-icons {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-top: 30px;
        }}

        .versal-public-analytics-icon {{
            display: inline-grid;
            flex: 0 0 44px;
            width: 44px;
            height: 44px;
            box-sizing: border-box;
            place-items: center;
            border: 1px solid {palette["landing_icon_tile_border"]};
            border-radius: 12px;
            background: {palette["landing_icon_tile_bg"]};
        }}

        .versal-public-analytics-icon img {{
            display: block;
            width: 22px;
            height: 22px;
        }}

        .versal-public-wave {{
            position: absolute;
            z-index: 0;
            right: -3%;
            bottom: -2%;
            width: min(62vw, 760px);
            aspect-ratio: 1.85 / 1;
            opacity: 0.58;
            pointer-events: none;
            background-image: radial-gradient(
                circle,
                rgba(255, 255, 255, 0.94) 0 1.7px,
                transparent 1.9px
            );
            background-size: 15px 15px;
            clip-path: polygon(
                0 100%, 0 82%, 14% 72%, 26% 50%, 39% 60%, 51% 31%,
                64% 42%, 77% 15%, 88% 27%, 100% 0, 100% 100%
            );
            -webkit-mask-image: linear-gradient(
                120deg,
                transparent 2%,
                rgba(0, 0, 0, 0.28) 35%,
                #000 82%
            );
            mask-image: linear-gradient(
                120deg,
                transparent 2%,
                rgba(0, 0, 0, 0.28) 35%,
                #000 82%
            );
        }}

        [class*="st-key-public_landing_band"] {{
            position: relative;
            z-index: 3;
            min-height: 32dvh;
            padding: 0 clamp(1rem, 5vw, 2.5rem) clamp(2.3rem, 5vw, 4rem) !important;
            box-sizing: border-box;
            border: 0 !important;
            border-radius: 0 !important;
            background: {palette["landing_band_bg"]} !important;
        }}

        .versal-public-cards {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: clamp(1rem, 2.2vw, 1.5rem);
            width: min(100%, 1100px);
            margin: 0 auto;
            transform: translateY(var(--versal-cards-offset));
        }}

        .versal-public-card {{
            display: grid;
            grid-template-columns: 3.1rem minmax(0, 1fr);
            gap: 1rem;
            min-height: 150px;
            padding: clamp(1.25rem, 2.5vw, 1.65rem);
            box-sizing: border-box;
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 16px;
            background: {palette["landing_card_bg"]};
            box-shadow: {palette["landing_card_shadow"]};
        }}

        .versal-public-card-icon {{
            display: inline-grid;
            width: 3rem;
            height: 3rem;
            place-items: center;
            border-radius: 13px;
            background: {palette["landing_icon_bg"]};
            color: {palette["landing_icon"]};
        }}

        .versal-public-card-icon img {{
            width: 1.5rem;
            height: 1.5rem;
            object-fit: contain;
        }}

        .versal-public-card h2 {{
            margin: 0 0 0.5rem;
            color: {palette["landing_card_text"]} !important;
            font-size: 1.05rem;
            font-weight: 750;
            line-height: 1.3;
        }}

        .versal-public-card p {{
            margin: 0;
            color: {palette["landing_card_muted"]} !important;
            font-size: 0.9rem;
            line-height: 1.55;
        }}

        @media (max-width: 800px) {{
            [class*="st-key-public_landing_hero"] {{
                min-height: 620px;
            }}

            .versal-public-copy h1 {{
                max-width: 590px;
                font-size: clamp(2.75rem, 7.2vw, 3.55rem);
            }}

            .versal-public-wave {{
                right: -14%;
                width: min(78vw, 650px);
                opacity: 0.45;
            }}

            .versal-public-cards {{
                grid-template-columns: repeat(3, minmax(0, 1fr));
            }}

            .versal-public-card {{
                grid-template-columns: 1fr;
            }}
        }}

        @media (max-width: 640px) {{
            [class*="st-key-public_landing_hero"] {{
                min-height: 600px;
            }}

            [class*="st-key-public_landing_hero"] {{
                padding: 1.1rem 1rem 5.2rem;
            }}

            [class*="st-key-public_landing_topbar"]
            > [data-testid="stElementContainer"]:first-child {{
                flex-basis: 150px;
                min-width: 0;
            }}

            .versal-public-logo {{
                width: clamp(130px, 38vw, 150px);
            }}

            [class*="st-key-public_landing_sign_in"] button {{
                min-width: 6.8rem;
                min-height: 2.75rem;
                padding-inline: 1rem;
            }}

            [class*="st-key-public_landing_copy"] {{
                margin-top: 4.2rem;
            }}

            .versal-public-copy h1 {{
                max-width: 100%;
                font-size: clamp(2.15rem, 10vw, 2.4rem);
                line-height: 1.04;
            }}

            .versal-public-copy p {{
                font-size: 1rem;
                line-height: 1.62;
            }}

            .versal-public-analytics-icons {{
                gap: 10px;
                margin-top: 28px;
            }}

            .versal-public-analytics-icon {{
                flex-basis: 40px;
                width: 40px;
                height: 40px;
                border-radius: 11px;
            }}

            .versal-public-wave {{
                right: -38%;
                bottom: -1%;
                width: 135vw;
                opacity: 0.34;
            }}

            [class*="st-key-public_landing_band"] {{
                padding-inline: 1rem;
            }}

            .versal-public-cards {{
                grid-template-columns: 1fr;
                gap: 0.9rem;
                --versal-cards-offset: -2rem;
            }}

            .versal-public-card {{
                grid-template-columns: 3rem minmax(0, 1fr);
                min-height: auto;
                padding: 1.15rem;
            }}
        }}

        @media (prefers-reduced-motion: reduce) {{
            [class*="st-key-public_landing_sign_in"] button {{
                transition: none;
            }}
        }}

        @keyframes versal-public-fade-up {{
            from {{
                opacity: 0;
                transform: translate3d(0, var(--versal-anim-distance), 0);
            }}
            to {{
                opacity: 1;
                transform: translate3d(0, 0, 0);
            }}
        }}

        @keyframes versal-public-cards-in {{
            from {{
                opacity: 0;
                transform: translate3d(
                    0,
                    calc(var(--versal-cards-offset) + var(--versal-anim-distance)),
                    0
                );
            }}
            to {{
                opacity: 1;
                transform: translate3d(0, var(--versal-cards-offset), 0);
            }}
        }}

        @keyframes versal-public-wave-drift {{
            from {{ transform: translate3d(0, 0, 0); }}
            to {{ transform: translate3d(16px, 0, 0); }}
        }}

        @media (prefers-reduced-motion: no-preference) {{
            [class*="st-key-public_landing_topbar"],
            .versal-public-copy h1,
            .versal-public-copy p,
            .versal-public-analytics-icon,
            .versal-public-cards {{
                animation-duration: var(--versal-anim-duration);
                animation-timing-function: ease-out;
                animation-fill-mode: both;
                animation-iteration-count: 1;
            }}

            [class*="st-key-public_landing_topbar"] {{
                animation-name: versal-public-fade-up;
                animation-delay: 0ms;
            }}

            .versal-public-copy h1 {{
                animation-name: versal-public-fade-up;
                animation-delay: var(--versal-anim-stagger);
            }}

            .versal-public-copy p {{
                animation-name: versal-public-fade-up;
                animation-delay: calc(var(--versal-anim-stagger) + var(--versal-anim-stagger));
            }}

            .versal-public-analytics-icon {{
                animation-name: versal-public-fade-up;
                animation-delay: calc(
                    var(--versal-anim-stagger) + var(--versal-anim-stagger)
                    + var(--versal-anim-stagger)
                );
            }}

            .versal-public-analytics-icon:nth-child(2) {{
                animation-delay: calc(
                    var(--versal-anim-stagger) + var(--versal-anim-stagger)
                    + var(--versal-anim-stagger) + var(--versal-icon-sweep)
                );
            }}

            .versal-public-analytics-icon:nth-child(3) {{
                animation-delay: calc(
                    var(--versal-anim-stagger) + var(--versal-anim-stagger)
                    + var(--versal-anim-stagger) + var(--versal-icon-sweep)
                    + var(--versal-icon-sweep)
                );
            }}

            .versal-public-analytics-icon:nth-child(4) {{
                animation-delay: calc(
                    var(--versal-anim-stagger) + var(--versal-anim-stagger)
                    + var(--versal-anim-stagger) + var(--versal-icon-sweep)
                    + var(--versal-icon-sweep) + var(--versal-icon-sweep)
                );
            }}

            .versal-public-analytics-icon:nth-child(5) {{
                animation-delay: calc(
                    var(--versal-anim-stagger) + var(--versal-anim-stagger)
                    + var(--versal-anim-stagger) + var(--versal-icon-sweep)
                    + var(--versal-icon-sweep) + var(--versal-icon-sweep)
                    + var(--versal-icon-sweep)
                );
            }}

            .versal-public-cards {{
                animation-name: versal-public-cards-in;
                animation-delay: calc(
                    var(--versal-anim-stagger) + var(--versal-anim-stagger)
                    + var(--versal-anim-stagger) + var(--versal-anim-stagger)
                    + var(--versal-anim-stagger) + var(--versal-anim-stagger)
                    + var(--versal-anim-stagger)
                );
            }}

            .versal-public-wave {{
                animation: versal-public-wave-drift var(--versal-wave-duration)
                           ease-in-out infinite alternate;
            }}

            .versal-public-card {{
                position: relative;
                transition: transform var(--versal-hover-duration) ease;
            }}

            .versal-public-card::after {{
                content: "";
                position: absolute;
                inset: 0;
                border-radius: inherit;
                box-shadow: 0 20px 44px rgba(7, 27, 74, 0.18);
                opacity: 0;
                pointer-events: none;
                transition: opacity var(--versal-hover-duration) ease;
            }}

            .versal-public-card:hover {{
                transform: translate3d(0, -4px, 0);
            }}

            .versal-public-card:hover::after {{
                opacity: 1;
            }}
        }}

        @media (max-width: 767px) and (prefers-reduced-motion: no-preference) {{
            .versal-public-wave {{
                animation: none;
            }}
        }}
        </style>
        """
    )


def apply_theme() -> None:
    """Apply existing visual polish to authenticated business pages."""
    apply_typography()
    st.html(
        """
        <style>
        * {
            transition: background-color 0.2s, color 0.2s, border-color 0.2s;
        }

        .stApp::before {
            content: "";
            position: fixed;
            inset: 0 0 auto 0;
            height: 4px;
            background: linear-gradient(90deg, #4F46E5, #7C3AED);
            z-index: 999999;
            pointer-events: none;
        }

        /* Keep Streamlit's heading permalink icon out of the user interface. */
        [data-testid="stHeadingWithActionElements"] a[href^="#"] {
            display: none !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"],
        div[data-testid="stContainer"] {
            border-radius: 14px !important;
        }

        div[data-testid="stMetric"] {
            border-radius: 14px !important;
            min-width: 100% !important;
            min-height: 140px !important;
            padding: 24px !important;
            overflow: visible !important;
        }

        [class*="st-key-overview_kpi_"] {
            min-height: 200px !important;
            overflow: visible !important;
        }

        [class*="st-key-overview_kpi_"] [data-testid="stVerticalBlockBorderWrapper"] {
            min-height: 200px !important;
            overflow: visible !important;
        }

        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] * {
            font-size: 32px !important;
            font-weight: 700 !important;
            opacity: 1 !important;
            max-width: none !important;
            overflow: visible !important;
            text-overflow: clip !important;
            white-space: nowrap !important;
        }

        div[data-testid="stMetricDelta"],
        div[data-testid="stMetricDelta"] * {
            opacity: 1 !important;
        }

        [data-testid="stDataFrame"],
        [data-testid="stVegaLiteChart"],
        [data-testid="stArrowVegaLiteChart"] {
            border-radius: 12px !important;
            overflow: hidden;
        }

        /* The public landing remains internally routable for browser Back, but
           it is intentionally not an authenticated sidebar destination. */
        [data-testid="stSidebarNav"] [data-testid="stSidebarNavLink"][href$="/landing"] {
            display: none !important;
        }

        [class*="st-key-sidebar_brand"] {
            padding: 0.25rem 0.25rem 0.75rem;
        }

        [class*="st-key-sidebar_brand"] img {
            max-width: 100%;
            height: auto;
        }

        [class*="st-key-landing_account"] {
            position: fixed;
            /* Sit below Streamlit's deployment toolbar instead of behind it. */
            top: 3.5rem;
            right: 1rem;
            z-index: 1000001;
            width: auto;
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            gap: 0.55rem !important;
            padding: 0.25rem 0.45rem 0.25rem 0.75rem;
            border: 1px solid color-mix(in srgb, currentColor 18%, transparent);
            border-radius: 999px;
            background: color-mix(in srgb, var(--background-color, #FFFFFF) 92%, transparent);
            backdrop-filter: blur(10px);
        }

        [class*="st-key-landing_account"] p {
            max-width: 14rem;
            margin: 0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        [class*="st-key-landing_account"] button {
            min-height: 2.25rem;
        }

        [class*="st-key-landing_shell"] {
            max-width: 900px;
            min-height: calc(100vh - 6.5rem);
            margin: 0 auto;
            display: flex;
            align-items: center;
        }

        [class*="st-key-landing_shell"] > div {
            width: 100%;
        }

        [class*="st-key-landing_content"] {
            text-align: center;
        }

        [class*="st-key-landing_content"] img {
            max-width: 100%;
            height: auto;
        }

        [class*="st-key-landing_actions"] {
            width: 100%;
            justify-content: center;
            gap: 0.8rem !important;
        }

        [class*="st-key-landing_actions"] > [data-testid="stElementContainer"] {
            flex: 0 0 auto;
            width: 15rem !important;
            max-width: none;
        }

        [class*="st-key-landing_actions"] [data-testid="stButton"] {
            width: 100% !important;
        }

        [class*="st-key-landing_actions"] [data-testid="stButton"] button {
            width: 100% !important;
            min-height: 3rem;
            justify-content: center;
            align-items: center;
            gap: 0.5rem;
            padding: 0.55rem 1rem;
            border: 0 !important;
            border-radius: 999px;
            color: var(--landing-button-text) !important;
            font-size: 1.1rem;
            font-weight: 700;
            line-height: 1.2;
            text-align: left;
            box-shadow: none;
            transform: translateY(0);
            transition: background-color 180ms ease, box-shadow 180ms ease,
                        transform 180ms ease;
        }

        [class*="st-key-landing_actions"] [data-testid="stButton"] button * {
            color: var(--landing-button-text) !important;
        }

        [class*="st-key-landing_actions"] [data-testid="stButton"] button p {
            margin: 0;
            font-size: 1.1rem;
        }

        [class*="st-key-landing_actions"] [data-testid="stButton"]
        button [data-testid="stIconMaterial"] {
            width: 1.2rem;
            height: 1.2rem;
            font-size: 1.2rem !important;
            line-height: 1;
        }

        [class*="st-key-landing_actions"] > [data-testid="stElementContainer"]:nth-child(1)
        [data-testid="stButton"] button {
            background: var(--landing-button-primary-bg);
            box-shadow: var(--landing-button-primary-shadow);
        }

        [class*="st-key-landing_actions"] > [data-testid="stElementContainer"]:nth-child(2)
        [data-testid="stButton"] button {
            background: var(--landing-button-secondary-bg);
            box-shadow: var(--landing-button-secondary-shadow);
        }

        [class*="st-key-landing_actions"] > [data-testid="stElementContainer"]:nth-child(1)
        [data-testid="stButton"] button:hover {
            background: var(--landing-button-primary-hover);
            box-shadow: 0 13px 28px rgba(15, 15, 61, 0.32);
            transform: translateY(-2px);
        }

        [class*="st-key-landing_actions"] > [data-testid="stElementContainer"]:nth-child(2)
        [data-testid="stButton"] button:hover {
            background: var(--landing-button-secondary-hover);
            box-shadow: 0 13px 28px rgba(180, 35, 24, 0.30);
            transform: translateY(-2px);
        }

        [class*="st-key-landing_actions"] [data-testid="stButton"] button:active {
            transform: translateY(0) scale(0.99);
        }

        [class*="st-key-landing_actions"] [data-testid="stButton"] button:focus-visible {
            outline: 3px solid var(--landing-button-text);
            outline-offset: 3px;
            box-shadow: 0 0 0 6px var(--landing-button-focus-ring);
        }

        .versal-landing-description {
            max-width: 680px;
            margin: 0 auto;
            font-size: 1.05rem;
            line-height: 1.55;
            opacity: 0.78;
        }

        .versal-landing-footer {
            margin-top: 1.75rem;
            text-align: center;
            font-size: 0.85rem;
            opacity: 0.72;
        }

        .versal-landing-footer a {
            color: inherit;
        }

        .versal-logo-fallback {
            display: flex;
            justify-content: center;
            width: 100%;
        }

        @media (max-width: 640px) {
            .block-container {
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }

            [class*="st-key-landing_shell"] {
                min-height: auto;
                padding-top: 1.25rem;
                padding-bottom: 1.5rem;
            }

            [class*="st-key-landing_actions"] > [data-testid="stElementContainer"] {
                flex-basis: 100%;
                max-width: none;
                width: 100%;
            }

            [class*="st-key-landing_actions"] [data-testid="stButton"] {
                width: 100% !important;
            }

            [class*="st-key-landing_actions"] [data-testid="stButton"] button {
                width: 100% !important;
                min-height: 3rem;
            }

            .versal-landing-description {
                font-size: 0.98rem;
            }

            [class*="st-key-landing_account"] {
                top: 3.25rem;
                right: 0.65rem;
                max-width: calc(100vw - 1.3rem);
            }

            [class*="st-key-landing_account"] p {
                max-width: 9rem;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                transition-duration: 0.01ms !important;
            }
        }
        </style>
        """
    )
