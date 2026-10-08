"""versalMotors Business Intelligence application shell."""

import logging
from pathlib import Path

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

# Global presentation layer. Keeping the visual system in one stylesheet lets
# every page rendered through ``st.navigation`` share the same UI treatment.
st.markdown(
    f"<style>{Path(__file__).with_name('style.css').read_text(encoding='utf-8')}</style>",
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
