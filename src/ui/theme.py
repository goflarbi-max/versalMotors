"""Shared visual styling for the Streamlit shell and landing page."""

import base64
from pathlib import Path

import streamlit as st


LANDING_SURFACE_THEME = {
    "light": {
        "overlay": "rgba(255, 255, 255, 0.76)",
        "vignette": "rgba(255, 255, 255, 0.18)",
        "panel": "rgba(255, 255, 255, 0.96)",
        "panel_fallback": "#FFFFFF",
        "border": "rgba(255, 255, 255, 0.82)",
        "shadow": "0 24px 70px rgba(15, 23, 42, 0.18)",
        "title": "#111827",
        "description": "#374151",
    },
    "dark": {
        "overlay": "rgba(15, 18, 28, 0.84)",
        "vignette": "rgba(2, 6, 23, 0.20)",
        "panel": "rgba(20, 24, 35, 0.94)",
        "panel_fallback": "#141823",
        "border": "rgba(255, 255, 255, 0.17)",
        "shadow": "0 24px 70px rgba(0, 0, 0, 0.38)",
        "title": "#F8FAFC",
        "description": "#CBD5E1",
    },
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
    },
}


RUNTIME_THEME = {
    "light": {
        "background": "#F8FAFC",
        "secondary_background": "#FFFFFF",
        "text": "#0F172A",
        "muted_text": "#64748B",
        "border": "#E2E8F0",
        "color_scheme": "light",
    },
    "dark": {
        "background": "#020617",
        "secondary_background": "#0F172A",
        "text": "#F1F5F9",
        "muted_text": "#CBD5E1",
        "border": "#1E293B",
        "color_scheme": "dark",
    },
}


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
        "card_outer_bg": "#0B1220",
        "card_bg": "#0F172A",
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
        "chart_palette": ("#16C060", "#3DB2A0", "#94A3B8", "#64748B"),
        "chart_grid": "#334155",
        "chart_grid_subtle": "rgba(51, 65, 85, 0.56)",
        "chart_tooltip_bg": "#111827",
        "chart_tooltip_text": "#F1F5F9",
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
    font-family: var(--st-font, sans-serif);
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
    font-size: 13px;
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
    font-size: 13px;
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
    selected = st.session_state.get("sidebar_dark_mode")
    if isinstance(selected, bool):
        return TABLE_THEME["dark" if selected else "light"]
    try:
        dark_mode = st.context.theme.type == "dark"
    except (AttributeError, RuntimeError):
        dark_mode = False
    return TABLE_THEME["dark" if dark_mode else "light"]


def active_overview_theme() -> dict[str, object]:
    """Return Overview colours matching the app's current runtime selection."""
    selected = st.session_state.get("sidebar_dark_mode")
    if isinstance(selected, bool):
        return OVERVIEW_THEME["dark" if selected else "light"]
    try:
        dark_mode = st.context.theme.type == "dark"
    except (AttributeError, RuntimeError):
        dark_mode = False
    return OVERVIEW_THEME["dark" if dark_mode else "light"]


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


@st.cache_data(show_spinner=False)
def _landing_background_data_uri() -> str:
    """Embed the optimized background so hosted routes need no static-file URL."""
    image_path = Path(__file__).resolve().parents[2] / "assets" / "landing_bg.webp"
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:image/webp;base64,{encoded}"


def apply_login_theme() -> None:
    """Apply login-only chrome hiding and responsive card styling."""
    st.html(
        """
        <span id="versal-theme-bootstrap" hidden></span>
        <script>
        (() => {
            const sessionMarker = "versalMotorsLightThemeInitialized";
            if (sessionStorage.getItem(sessionMarker) !== "true") {
                const themeKeys = Object.keys(localStorage).filter((key) =>
                    key.startsWith("stActiveTheme-")
                );
                let changed = false;

                for (const key of themeKeys) {
                    const stored = localStorage.getItem(key);
                    let selected = stored;
                    try {
                        selected = JSON.parse(stored);
                    } catch (_) {
                        // Older Streamlit versions may store the value without JSON encoding.
                    }
                    if (selected !== "Light") {
                        localStorage.setItem(key, JSON.stringify("Light"));
                        changed = true;
                    }
                }

                sessionStorage.setItem(sessionMarker, "true");
                if (changed) {
                    window.location.reload();
                    return;
                }
            }

        })();
        </script>
        """,
        unsafe_allow_javascript=True,
    )
    try:
        dark_mode = st.context.theme.type == "dark"
    except (AttributeError, RuntimeError):
        dark_mode = False

    login_glass = {
        "light": {
            "card_background": "rgba(255, 255, 255, 0.64)",
            "fallback_background": "rgba(255, 255, 255, 0.96)",
            "card_border": "rgba(255, 255, 255, 0.78)",
            "card_shadow": "0 24px 65px rgba(15, 23, 42, 0.18)",
            "shape_one": "rgba(99, 102, 241, 0.20)",
            "shape_two": "rgba(56, 189, 248, 0.17)",
        },
        "dark": {
            "card_background": "rgba(20, 24, 35, 0.56)",
            "fallback_background": "rgba(15, 23, 42, 0.96)",
            "card_border": "rgba(255, 255, 255, 0.18)",
            "card_shadow": "0 24px 65px rgba(0, 0, 0, 0.38)",
            "shape_one": "rgba(99, 102, 241, 0.16)",
            "shape_two": "rgba(14, 165, 233, 0.12)",
        },
    }
    glass = login_glass["dark" if dark_mode else "light"]
    card_text = "#F8FAFC" if dark_mode else "#0F172A"
    muted_text = "#CBD5E1" if dark_mode else "#64748B"
    field_background = "#111827" if dark_mode else "#F8FAFC"
    field_border = "#334155" if dark_mode else "#CBD5E1"
    page_background = "#020617" if dark_mode else "#F8FAFC"

    st.html(
        f"""
        <style>
        [data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        footer {{
            display: none !important;
        }}

        .stApp,
        [data-testid="stAppViewContainer"] {{
            background: {page_background};
            height: 100dvh;
            overflow: hidden !important;
        }}

        html,
        body,
        [data-testid="stAppViewContainer"] > .main {{
            height: 100dvh;
            overflow: hidden !important;
        }}

        .block-container {{
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
            color: {card_text};
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
            color: {card_text};
            font-size: clamp(1.45rem, 4vw, 1.9rem);
            line-height: 1.2;
            margin-bottom: 0;
        }}

        [class*="st-key-login_card"] label,
        [class*="st-key-login_card"] p {{
            color: {card_text};
        }}

        [class*="st-key-login_card"] [data-baseweb="input"] {{
            min-height: 3rem;
            border-color: {field_border};
            background: {field_background};
        }}

        [class*="st-key-login_card"] [data-baseweb="input"] input {{
            color: {card_text};
        }}

        [class*="st-key-login_card"] [data-baseweb="input"] input::placeholder {{
            color: {muted_text};
            opacity: 0.82;
        }}

        [class*="st-key-login_card"] [data-testid="stButton"] button[kind="primary"] {{
            min-height: 3.25rem;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 700;
        }}

        [class*="st-key-forgot_password_row"] button {{
            min-height: auto;
            padding: 0.15rem 0 !important;
            color: #6366F1 !important;
            font-weight: 650;
        }}

        .versal-login-subtitle {{
            margin: -0.15rem 0 0.4rem;
            color: {muted_text} !important;
            text-align: center;
            font-size: 0.98rem;
        }}

        @media (max-width: 480px) {{
            .block-container {{
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


def _apply_landing_surface_theme() -> None:
    """Register landing-only image and glass styles in the global theme layer."""
    try:
        dark_mode = st.context.theme.type == "dark"
    except (AttributeError, RuntimeError):
        dark_mode = False

    surface = LANDING_SURFACE_THEME["dark" if dark_mode else "light"]
    background_uri = _landing_background_data_uri()
    st.markdown(
        f"""
        <style id="versal-landing-surface">
        .stApp:has([class*="st-key-landing_shell"]),
        [data-testid="stAppViewContainer"]:has([class*="st-key-landing_shell"]) {{
            background-image:
                radial-gradient(ellipse at center, transparent 36%, {surface["vignette"]} 100%),
                linear-gradient({surface["overlay"]}, {surface["overlay"]}),
                url("{background_uri}") !important;
            background-position: center center !important;
            background-size: cover !important;
            background-attachment: scroll !important;
            background-repeat: no-repeat !important;
            overflow: hidden !important;
            transition: none !important;
            animation: none !important;
        }}

        [data-testid="stAppViewContainer"]:has([class*="st-key-landing_shell"])
        .block-container {{
            width: 100% !important;
            max-width: none !important;
            height: 100dvh !important;
            padding: 4px 0 0 !important;
            overflow: hidden !important;
        }}

        [class*="st-key-landing_shell"] {{
            position: relative !important;
            width: 100% !important;
            max-width: none !important;
            height: calc(100dvh - 4px) !important;
            min-height: 0 !important;
            margin: 0 !important;
            padding: clamp(0.75rem, 2vw, 1.5rem) !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            overflow: hidden !important;
            isolation: isolate;
            transition: none !important;
            animation: none !important;
        }}

        [class*="st-key-landing_shell"] > div {{
            width: 100%;
        }}

        [class*="st-key-landing_content"] {{
            width: min(100%, 760px);
            margin-inline: auto;
            padding: clamp(1.35rem, 3.2vw, 2.25rem);
            box-sizing: border-box;
            overflow: hidden !important;
            border: 1px solid {surface["border"]} !important;
            border-radius: 24px !important;
            clip-path: inset(0 round 24px);
            background: {surface["panel"]} !important;
            box-shadow: {surface["shadow"]} !important;
            -webkit-backdrop-filter: none !important;
            backdrop-filter: none !important;
            transition: none !important;
            animation: none !important;
        }}

        [class*="st-key-landing_content"] h1 {{
            color: {surface["title"]} !important;
        }}

        [class*="st-key-landing_content"] .versal-landing-description {{
            color: {surface["description"]} !important;
            opacity: 1;
        }}

        [class*="st-key-landing_content"] > div,
        [class*="st-key-landing_content"] > div >
        [data-testid="stVerticalBlockBorderWrapper"] {{
            border-radius: inherit !important;
            background: transparent !important;
        }}

        @media (max-width: 480px) {{
            [class*="st-key-landing_shell"] {{
                padding: 0.65rem !important;
            }}

            [class*="st-key-landing_content"] {{
                width: calc(100% - 0.5rem);
                padding: 1.1rem 0.9rem;
                border-radius: 18px !important;
                clip-path: inset(0 round 18px);
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hide_landing_navigation() -> None:
    """Hide sidebar navigation and its reveal control on the landing route only."""
    st.html(
        """
        <style>
        [data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"] {
            display: none !important;
        }
        </style>
        """
    )


def apply_theme() -> None:
    """Apply existing shell polish plus responsive landing-page styles."""
    try:
        dark_mode = st.context.theme.type == "dark"
    except (AttributeError, RuntimeError):
        dark_mode = False

    _apply_landing_surface_theme()

    landing_button_theme = {
        "button_primary_bg": "#0F0F3D",
        "button_primary_hover": "#1A1A5E",
        "button_secondary_bg": "#D92D20",
        "button_secondary_hover": "#B42318",
        "button_text": "#FFFFFF",
        "button_focus_ring": "#6366F1",
        "button_primary_shadow": (
            "0 10px 24px rgba(15, 15, 61, 0.30), "
            "0 0 0 1px rgba(255, 255, 255, 0.24)"
            if dark_mode
            else "0 10px 24px rgba(15, 15, 61, 0.24)"
        ),
        "button_secondary_shadow": "0 10px 24px rgba(180, 35, 24, 0.24)",
    }
    st.html(
        f"""
        <style>
        :root {{
            --landing-button-primary-bg: {landing_button_theme["button_primary_bg"]};
            --landing-button-primary-hover: {landing_button_theme["button_primary_hover"]};
            --landing-button-secondary-bg: {landing_button_theme["button_secondary_bg"]};
            --landing-button-secondary-hover: {landing_button_theme["button_secondary_hover"]};
            --landing-button-text: {landing_button_theme["button_text"]};
            --landing-button-focus-ring: {landing_button_theme["button_focus_ring"]};
            --landing-button-primary-shadow: {landing_button_theme["button_primary_shadow"]};
            --landing-button-secondary-shadow: {landing_button_theme["button_secondary_shadow"]};
        }}
        </style>
        """
    )
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
