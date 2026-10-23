"""Single source of truth for VersalMotors typography."""

from __future__ import annotations

import streamlit as st


FONT_FAMILY = 'Inter, system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif'

TYPOGRAPHY = {
    "font_family": FONT_FAMILY,
    "font_weight_body": 400,
    "font_weight_label": 500,
    "font_weight_strong": 600,
    "font_weight_heading": 700,
    "font_size_body": "16px",
    "font_size_readable_min": "14px",
    "font_size_caption": "12px",
}


def typography_css() -> str:
    """Return font-only CSS for native Streamlit and custom HTML content."""
    typography = TYPOGRAPHY
    return f"""
    <style id="versal-typography">
    @font-face {{
        font-family: "Inter";
        src: url("/app/static/fonts/Inter-400.woff2") format("woff2");
        font-style: normal;
        font-weight: 400;
        font-display: swap;
    }}
    @font-face {{
        font-family: "Inter";
        src: url("/app/static/fonts/Inter-500.woff2") format("woff2");
        font-style: normal;
        font-weight: 500;
        font-display: swap;
    }}
    @font-face {{
        font-family: "Inter";
        src: url("/app/static/fonts/Inter-600.woff2") format("woff2");
        font-style: normal;
        font-weight: 600;
        font-display: swap;
    }}
    @font-face {{
        font-family: "Inter";
        src: url("/app/static/fonts/Inter-700.woff2") format("woff2");
        font-style: normal;
        font-weight: 700;
        font-display: swap;
    }}

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
    [data-baseweb],
    [role="tooltip"],
    button,
    input,
    textarea,
    select,
    .versal-table-root {{
        font-family: var(--versal-font-family) !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }}

    body,
    .stApp,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li {{
        font-size: var(--versal-font-size-body);
        font-weight: var(--versal-font-weight-body);
        line-height: 1.5;
    }}

    h1,
    h2,
    .versal-public-headline,
    [data-testid="stHeadingWithActionElements"] h1,
    [data-testid="stHeadingWithActionElements"] h2 {{
        font-family: var(--versal-font-family) !important;
        font-weight: var(--versal-font-weight-heading);
        letter-spacing: -0.02em;
        line-height: 1.2;
    }}

    h3, h4, h5, h6,
    [data-testid="stHeadingWithActionElements"] h3,
    [data-testid="stHeadingWithActionElements"] h4,
    [data-testid="stHeadingWithActionElements"] h5,
    [data-testid="stHeadingWithActionElements"] h6,
    .versal-overview-chart-title,
    .versal-table th {{
        font-family: var(--versal-font-family) !important;
        font-weight: var(--versal-font-weight-strong);
        letter-spacing: -0.01em;
        line-height: 1.25;
    }}

    label,
    nav,
    [role="tab"],
    [data-testid="stWidgetLabel"] {{
        font-weight: var(--versal-font-weight-label);
    }}

    .versal-overview-kpi-label,
    .versal-overview-chart-label {{
        font-weight: var(--versal-font-weight-strong);
        letter-spacing: 0.04em;
    }}

    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] *,
    .versal-summary-ring span {{
        font-size: var(--versal-font-size-caption) !important;
        line-height: 1.4;
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


def apply_typography() -> None:
    """Apply the shared font system without changing colour or layout styles."""
    st.html(typography_css())
