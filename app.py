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
    /* Scoped, Streamlit-safe card styling. No global text color overrides. */
    .stApp {
        background-color: #F8FAFC;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF;
        border-color: #E2E8F0 !important;
        border-radius: 16px !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
    }

    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
        padding: 18px;
    }

    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] * {
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        opacity: 1 !important;
    }

    @media (prefers-color-scheme: dark) {
        .stApp {
            background-color: #020617;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #0F172A;
            border-color: #1E293B !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.28);
        }

        [data-testid="stMetric"] {
            background-color: #0F172A;
            border-color: #1E293B;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.28);
        }

        [data-testid="stMetricValue"],
        [data-testid="stMetricValue"] * {
            color: #F1F5F9 !important;
            -webkit-text-fill-color: #F1F5F9 !important;
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
