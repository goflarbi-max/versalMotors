"""versalMotors Business Intelligence application shell."""

import logging

from dotenv import load_dotenv
import streamlit as st

from src.auth.auth import (
    current_user_email,
    is_authenticated,
    logout,
    require_login,
)
from src.database.bootstrap import database_is_ready, ensure_database
from src.ui.components import active_logo_path, render_logo
from src.ui.auth_ui import render_login
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
    st.Page("pages/overview.py", title="Overview", icon="📊"),
    st.Page("pages/investigate.py", title="Investigate", icon="🔎"),
    st.Page("pages/ask_the_business.py", title="Ask the Business", icon="💬"),
    st.Page("pages/management_brief.py", title="Management Brief", icon="📋"),
    st.Page("pages/data_quality.py", title="Data Quality", icon="✅"),
]

navigation = st.navigation(pages)
signed_in_email = current_user_email()

if navigation.title == landing_page.title:
    # Hide the navigation shell before the landing page renders so Home stays
    # sidebar-free without affecting any of the five protected business pages.
    hide_landing_navigation()
else:
    with st.sidebar:
        with st.container(key="sidebar_brand", horizontal_alignment="center"):
            render_logo(220)
        st.divider()
        st.caption(f"Signed in as\n\n{signed_in_email}")
        if st.button(
            "Sign out",
            icon=":material/logout:",
            key="sidebar_sign_out",
            width="stretch",
        ):
            logout()
            st.rerun()

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
