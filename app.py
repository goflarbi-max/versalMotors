"""versalMotors Business Intelligence application shell."""

import logging

from dotenv import load_dotenv
import streamlit as st

from src.database.bootstrap import database_is_ready, ensure_database
from src.ui.components import active_logo_path, render_logo
from src.ui.theme import apply_theme


load_dotenv()

st.set_page_config(
    page_title="versalMotors BI",
    page_icon=str(active_logo_path()),
    layout="wide",
    initial_sidebar_state="auto",
)
apply_theme()

landing_page = st.Page(
    "pages/landing.py",
    title="Home",
    icon=":material/home:",
    default=True,
)
pages = [
    landing_page,
    st.Page("pages/overview.py", title="Overview", icon="📊"),
    st.Page("pages/investigate.py", title="Investigate", icon="🔎"),
    st.Page("pages/ask_the_business.py", title="Ask the Business", icon="💬"),
    st.Page("pages/management_brief.py", title="Management Brief", icon="📋"),
    st.Page("pages/data_quality.py", title="Data Quality", icon="✅"),
]

navigation = st.navigation(pages)

if navigation.title != landing_page.title:
    with st.sidebar:
        with st.container(key="sidebar_brand", horizontal_alignment="center"):
            render_logo(220)

    # Keep Home instant and independent of the database. Analytical pages retain
    # the existing deployment bootstrap before their page script executes.
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

navigation.run()
