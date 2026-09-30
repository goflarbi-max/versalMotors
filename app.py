"""versalMotors Business Intelligence application shell."""

import streamlit as st


st.set_page_config(
    page_title="versalMotors BI",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

pages = [
    st.Page("pages/overview.py", title="Overview", icon="📊", default=True),
    st.Page("pages/investigate.py", title="Investigate", icon="🔎"),
    st.Page("pages/ask_the_business.py", title="Ask the Business", icon="💬"),
    st.Page("pages/management_brief.py", title="Management Brief", icon="📋"),
    st.Page("pages/data_quality.py", title="Data Quality", icon="✅"),
]

navigation = st.navigation(pages)
navigation.run()
