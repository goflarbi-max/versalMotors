"""Presentation-only login screen for the VersalMotors demo access layer."""

import streamlit as st

from src.auth.auth import AuthenticationError, login, verify_credentials
from src.ui.components import render_logo
from src.ui.theme import apply_login_theme


@st.dialog("Forgot Password?", icon=":material/help:")
def _show_password_help() -> None:
    st.info("Please contact the system administrator to reset your password.")


def render_login() -> None:
    """Render the responsive login card and authenticate submitted credentials."""
    apply_login_theme()

    with st.container(key="login_shell"):
        with st.container(key="login_card"):
            with st.container(horizontal_alignment="center", gap="small"):
                render_logo(165)
                st.title(
                    "VersalMotors Business Intelligence",
                    text_alignment="center",
                )
                st.html('<p class="versal-login-subtitle">Sign in to continue</p>')

            email = st.text_input(
                "Email Address",
                type="email",
                placeholder="Enter your email",
                icon=":material/mail:",
                autocomplete="off",
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                icon=":material/lock:",
                autocomplete="new-password",
            )

            with st.container(horizontal_alignment="right", key="forgot_password_row"):
                if st.button(
                    "Forgot Password?",
                    type="tertiary",
                    key="forgot_password",
                ):
                    _show_password_help()

            if st.button(
                "Sign In",
                type="primary",
                icon=":material/arrow_forward:",
                icon_position="right",
                key="sign_in",
                width="stretch",
            ):
                try:
                    user = verify_credentials(email, password)
                except AuthenticationError as error:
                    st.toast(
                        str(error),
                        icon=":material/error:",
                        duration="long",
                    )
                else:
                    login(user)
                    st.rerun()
