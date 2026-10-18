"""Fast, presentation-only entry page for VersalMotors."""

import streamlit as st

from src.ui.components import render_logo
from src.ui.theme import hide_landing_navigation

with st.container(key="landing_shell"):
    with st.container(horizontal_alignment="center", gap="small", key="landing_content"):
        render_logo(480)
        st.title("Business Intelligence & Decision System", text_alignment="center")
        st.html(
            '<p class="versal-landing-description">Understand performance, investigate what matters, and turn trusted business evidence into better decisions.</p>'
        )
        st.space("small")
        with st.container(horizontal=True, wrap=True, key="landing_actions"):
            if st.button(
                "Open Business Overview",
                icon=":material/monitoring:",
                key="landing_open_overview",
                width="content",
            ):
                st.switch_page("pages/overview.py")
            if st.button(
                "Ask the Business",
                icon=":material/forum:",
                key="landing_ask_business",
                width="content",
            ):
                st.switch_page("pages/ask_the_business.py")

# Inject route-specific chrome after the page tree exists so Streamlit navigation
# cannot discard the background or glass styles during the page transition.
hide_landing_navigation()
