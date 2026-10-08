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

st.markdown("""
<style>
/* LIGHT MODE ONLY - Professional */
.stApp {
  background-color: #F8FAFC!important;
}

div[data-testid="stMetric"] {
  background: #FFFFFF!important;
  border: 1px solid #E2E8F0!important;
  border-radius: 16px!important;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04)!important;
  padding: 18px!important;
}

/* FORCE VISIBILITY - Light mode */
div[data-testid="stMetricValue"] div {
  color: #0F172A!important;
  -webkit-text-fill-color: #0F172A!important;
  opacity: 1!important;
}

div[data-testid="stMetricLabel"] div {
  color: #64748B!important;
  -webkit-text-fill-color: #64748B!important;
  opacity: 1!important;
}

div[data-testid="stMetricDelta"] div {
  opacity: 1!important;
}

h1, h2, h3 {
  color: #0F172A!important;
  -webkit-text-fill-color: #0F172A!important;
}
</style>
""", unsafe_allow_html=True)

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
