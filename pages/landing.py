"""Fast, presentation-only entry page for VersalMotors."""

import streamlit as st

from src.ui.components import render_logo
from src.ui.theme import hide_landing_navigation


hide_landing_navigation()

with st.container(key="landing_shell"):
    with st.container(horizontal_alignment="center", gap="small", key="landing_content"):
        render_logo(480)
        st.title("Business Intelligence & Decision System", text_alignment="center")
        st.html(
            '<p class="versal-landing-description">Understand performance, investigate what matters, and turn trusted business evidence into better decisions.</p>'
        )
        st.space("small")
        with st.container(horizontal=True, wrap=True, key="landing_actions"):
            st.page_link(
                "pages/overview.py",
                label="Open Business Overview",
                icon=":material/monitoring:",
                width="stretch",
            )
            st.page_link(
                "pages/ask_the_business.py",
                label="Ask the Business",
                icon=":material/forum:",
                width="stretch",
            )
