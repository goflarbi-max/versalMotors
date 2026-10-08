"""versalMotors Business Intelligence application shell."""

import logging

from dotenv import load_dotenv
load_dotenv()

import streamlit as st

from src.database.bootstrap import database_is_ready, ensure_database


st.set_page_config(
    page_title="versalMotors BI",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

if st.context.theme.type == "dark":
    theme_tokens = """
        color-scheme: dark;
        --vm-page: #020617;
        --vm-page-depth: #060B19;
        --vm-card: #0F172A;
        --vm-text: #F1F5F9;
        --vm-text-secondary: #94A3B8;
        --vm-border: #1E293B;
        --vm-accent: #6366F1;
        --vm-accent-soft: rgba(99, 102, 241, 0.12);
        --vm-success: #10B981;
        --vm-warning: #F59E0B;
        --vm-danger: #EF4444;
        --vm-shadow: 0 1px 3px rgba(0, 0, 0, 0.28);
    """
else:
    theme_tokens = """
        color-scheme: light;
        --vm-page: #F8FAFC;
        --vm-page-depth: #F1F5F9;
        --vm-card: #FFFFFF;
        --vm-text: #0F172A;
        --vm-text-secondary: #64748B;
        --vm-border: #E2E8F0;
        --vm-accent: #4F46E5;
        --vm-accent-soft: rgba(79, 70, 229, 0.08);
        --vm-success: #10B981;
        --vm-warning: #F59E0B;
        --vm-danger: #EF4444;
        --vm-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    """

st.markdown(
    """
    <style>
    /* Streamlit's active menu theme supplies these semantic tokens. */
    :root {
        __VM_THEME_TOKENS__
    }

    * {
        transition: background-color 0.2s, color 0.2s, border-color 0.2s;
    }

    .stApp {
        background:
            radial-gradient(circle at 88% -10%, var(--vm-accent-soft), transparent 28rem),
            linear-gradient(180deg, var(--vm-page), var(--vm-page-depth)) !important;
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

    section[data-testid="stSidebar"] {
        background-color: var(--vm-card) !important;
        border-right: 1px solid var(--vm-border) !important;
    }

    /* Bordered Streamlit containers become restrained enterprise cards. */
    [data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stContainer"] {
        background-color: var(--vm-card) !important;
        border-color: var(--vm-border) !important;
        border-radius: 14px !important;
        box-shadow: var(--vm-shadow) !important;
    }

    div[data-testid="stMetric"] {
        background-color: var(--vm-card) !important;
        border: 1px solid var(--vm-border) !important;
        border-radius: 14px !important;
        box-shadow: var(--vm-shadow) !important;
        min-width: 100% !important;
        min-height: 140px !important;
        padding: 24px !important;
        overflow: visible !important;
    }

    /* Explicit metric contrast prevents invisible values in light mode. */
    div[data-testid="stMetricValue"],
    div[data-testid="stMetricValue"] * {
        color: var(--vm-text) !important;
        -webkit-text-fill-color: var(--vm-text) !important;
        font-size: 32px !important;
        font-weight: 700 !important;
        opacity: 1 !important;
        max-width: none !important;
        overflow: visible !important;
        text-overflow: clip !important;
        white-space: nowrap !important;
    }

    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] * {
        color: var(--vm-text-secondary) !important;
        -webkit-text-fill-color: var(--vm-text-secondary) !important;
        opacity: 1 !important;
    }

    div[data-testid="stMetricDelta"],
    div[data-testid="stMetricDelta"] * {
        opacity: 1 !important;
    }

    h1, h2, h3 {
        color: var(--vm-text) !important;
        -webkit-text-fill-color: var(--vm-text) !important;
    }

    [data-testid="stCaptionContainer"] {
        color: var(--vm-text-secondary) !important;
    }

    [data-testid="stDataFrame"] {
        background-color: var(--vm-card) !important;
        border: 1px solid var(--vm-border) !important;
        border-radius: 12px !important;
        box-shadow: var(--vm-shadow) !important;
        overflow: hidden;
    }

    [data-testid="stDataFrame"] *,
    [data-testid="stTable"] * {
        border-color: var(--vm-border) !important;
    }

    [data-testid="stVegaLiteChart"],
    [data-testid="stArrowVegaLiteChart"] {
        background-color: transparent !important;
        border-radius: 12px;
        overflow: hidden;
    }

    [data-testid="stVegaLiteChart"] canvas,
    [data-testid="stArrowVegaLiteChart"] canvas,
    [data-testid="stVegaLiteChart"] svg,
    [data-testid="stArrowVegaLiteChart"] svg {
        background-color: transparent !important;
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            transition-duration: 0.01ms !important;
        }
    }
    </style>
    """.replace("__VM_THEME_TOKENS__", theme_tokens),
    unsafe_allow_html=True,
)

try:
    if not database_is_ready():
        with st.spinner("Preparing business data for this deployment. The first startup may take about a minute…"):
            ensure_database()
except Exception:
    logging.exception("Could not prepare the analytical database")
    st.error(
        "Business data could not be prepared automatically. "
        "Please reboot the Streamlit app; if the problem continues, check the deployment logs."
    )
    st.stop()

pages = [
    st.Page("pages/overview.py", title="Overview", icon="📊", default=True),
    st.Page("pages/investigate.py", title="Investigate", icon="🔎"),
    st.Page("pages/ask_the_business.py", title="Ask the Business", icon="💬"),
    st.Page("pages/management_brief.py", title="Management Brief", icon="📋"),
    st.Page("pages/data_quality.py", title="Data Quality", icon="✅"),
]

navigation = st.navigation(pages)
navigation.run()
