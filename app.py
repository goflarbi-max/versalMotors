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

st.markdown(
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

    /* Structure only: native Streamlit theming owns all colors. */
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

    /* Auto-height overview cards stay large without Streamlit scroll regions. */
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

    [data-testid="stDataFrame"] {
        border-radius: 12px !important;
        overflow: hidden;
    }

    [data-testid="stVegaLiteChart"],
    [data-testid="stArrowVegaLiteChart"] {
        border-radius: 12px;
        overflow: hidden;
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            transition-duration: 0.01ms !important;
        }
    }
    </style>
    """,
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
