"""versalMotors Business Intelligence application shell."""

import logging

from dotenv import load_dotenv
import streamlit as st

from src.auth.auth import (
    is_authenticated,
    require_login,
)
from src.database.bootstrap import database_is_ready, ensure_database
from src.ui.components import active_logo_path
from src.ui.auth_ui import render_login
from src.ui.sidebar import render_sidebar
from src.ui.theme import apply_theme, hide_landing_navigation


load_dotenv()

st.set_page_config(
    page_title="versalMotors BI",
    page_icon=str(active_logo_path()),
    layout="wide",
    initial_sidebar_state="auto",
)
apply_theme()

if not is_authenticated():
    login_page = st.Page(
        render_login,
        title="Sign in",
        icon=":material/lock:",
        default=True,
    )
    login_navigation = st.navigation([login_page], position="hidden")
    login_navigation.run()
    st.stop()

require_login()

landing_page = st.Page(
    "pages/landing.py",
    title="Home",
    icon=":material/home:",
    default=True,
)
pages = [
    landing_page,
    st.Page("pages/overview.py", title="Overview", icon=":material/space_dashboard:"),
    st.Page("pages/investigate.py", title="Investigate", icon=":material/search_insights:"),
    st.Page("pages/ask_the_business.py", title="Ask the Business", icon=":material/chat:"),
    st.Page("pages/management_brief.py", title="Management Brief", icon=":material/description:"),
    st.Page("pages/data_quality.py", title="Data Quality", icon=":material/fact_check:"),
]

navigation = st.navigation(pages)

if navigation.title == landing_page.title:
    # Hide the navigation shell before the landing page renders so Home stays
    # sidebar-free without affecting any of the five protected business pages.
    hide_landing_navigation()
else:
    render_sidebar(navigation.title)

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
