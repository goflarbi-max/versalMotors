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
            st.page_link(
                "pages/overview.py",
                label="Open Business Overview",
                icon=":material/monitoring:",
                width="content",
            )
            st.page_link(
                "pages/ask_the_business.py",
                label="Ask the Business",
                icon=":material/forum:",
                width="content",
            )

# Keep this page-local override after the links so no earlier cached theme rule can
# recreate the retired right-side pseudo-element.
st.html(
    """
    <style id="versal-remove-landing-button-after">
    [class*="st-key-landing_actions"] [data-testid="stPageLink"] a::after,
    [class*="st-key-landing_actions"] [data-testid="stPageLink"] a:after {
        content: none !important;
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        border: 0 !important;
        margin: 0 !important;
    }
    </style>
    """
)

# Inject route-specific chrome after the page tree exists so Streamlit navigation
# cannot discard the background or glass styles during the page transition.
hide_landing_navigation()
