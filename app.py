"""versalMotors Business Intelligence application shell."""

import logging

from dotenv import load_dotenv
import streamlit as st

from src.auth.auth import is_authenticated, require_login
from src.database.bootstrap import database_is_ready, ensure_database
from src.ui.components import active_logo_path
from src.ui.landing import PROTECTED_ROUTES, current_route, signed_out_default_route
from src.ui.sidebar import render_sidebar
from src.ui.theme import apply_theme


load_dotenv()

st.set_page_config(
    page_title="versalMotors BI",
    page_icon=str(active_logo_path()),
    layout="wide",
    initial_sidebar_state="auto",
)

requested_route = current_route(st.context.url)

if not is_authenticated():
    default_route = signed_out_default_route(st.context.url)
    landing_page = st.Page(
        "pages/landing.py",
        title="Welcome",
        icon=":material/home:",
        url_path="landing",
        default=default_route == "landing",
    )
    login_page = st.Page(
        "pages/login.py",
        title="Sign in",
        icon=":material/lock:",
        url_path="login",
        default=default_route == "login",
    )

    def protected_redirect(route: str):
        """Create a distinct signed-out page that forwards to Login."""
        def redirect() -> None:
            st.switch_page(login_page)

        redirect.__name__ = f"redirect_{route}"
        return redirect

    protected_redirect_pages = [
        st.Page(
            protected_redirect(route),
            title="Sign in required",
            url_path=route,
        )
        for route in sorted(PROTECTED_ROUTES)
    ]
    public_navigation = st.navigation(
        [landing_page, login_page, *protected_redirect_pages],
        position="hidden",
    )
    public_navigation.run()
    st.stop()

require_login()
overview_page = st.Page(
    "pages/overview.py",
    title="Overview",
    icon=":material/space_dashboard:",
    default=(st.context.url is None)
    or requested_route not in {"", "landing", "login"},
)

# Keep the public root and /landing directly addressable after sign-in without
# restoring a Home item to the protected sidebar. Post-login navigation still
# goes explicitly to Overview; browser Back can therefore return to the landing
# page, whose Sign in control also returns an authenticated user to Overview.
if requested_route in {"", "landing"} and st.context.url is not None:
    landing_page = st.Page(
        "pages/landing.py",
        title="Welcome",
        icon=":material/home:",
        url_path="landing",
        default=True,
    )
    landing_navigation = st.navigation(
        [landing_page, overview_page],
        position="hidden",
    )
    landing_navigation.run()
    st.stop()

if requested_route == "login":
    def continue_to_overview() -> None:
        st.switch_page(overview_page)

    continue_page = st.Page(
        continue_to_overview,
        title="Continue",
        url_path="continue",
        default=True,
    )
    continue_navigation = st.navigation(
        [continue_page, overview_page],
        position="hidden",
    )
    continue_navigation.run()
    st.stop()

apply_theme()
pages = [
    overview_page,
    st.Page("pages/investigate.py", title="Investigate", icon=":material/search_insights:"),
    st.Page("pages/ask_the_business.py", title="Ask the Business", icon=":material/chat:"),
    st.Page("pages/management_brief.py", title="Management Brief", icon=":material/description:"),
    st.Page("pages/data_quality.py", title="Data Quality", icon=":material/fact_check:"),
    # Registered so browser Back can return to the public experience without
    # losing session state. Its navigation link is hidden by the shared theme.
    st.Page(
        "pages/landing.py",
        title="Welcome",
        icon=":material/home:",
        url_path="landing",
    ),
]

navigation = st.navigation(pages)
render_sidebar(navigation.title)

try:
    if not database_is_ready():
        with st.spinner(
            "Preparing business data for this deployment. "
            "The first startup may take about a minute..."
        ):
            ensure_database()
except Exception:
    logging.exception("Could not prepare the analytical database")
    st.error(
        "Business data could not be prepared automatically. "
        "Please reboot the Streamlit app; if the problem continues, check the deployment logs."
    )
    st.stop()

navigation.run()
