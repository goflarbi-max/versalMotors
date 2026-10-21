"""Shared, presentation-only sidebar for protected business pages."""

from __future__ import annotations

from html import escape
from importlib import reload

import streamlit as st

from src.auth.auth import current_user_email, logout
from src.ui import theme as theme_module


# Streamlit can retain an older imported theme module during hot reloads. Refresh
# that UI-only module once when the new sidebar tokens are not yet in memory.
if not all(hasattr(theme_module, name) for name in ("SIDEBAR_THEME", "RUNTIME_THEME")):
    theme_module = reload(theme_module)
SIDEBAR_THEME = theme_module.SIDEBAR_THEME
RUNTIME_THEME = theme_module.RUNTIME_THEME


_THEME_KEY = "sidebar_dark_mode"
_THEME_CONTEXT_KEY = "sidebar_theme_context"


def _logout_to_light() -> None:
    """Sign out through the existing auth function and reset only UI theme state."""
    logout()
    st.session_state[_THEME_KEY] = False
    st.session_state[_THEME_CONTEXT_KEY] = False

def _is_dark_mode() -> bool:
    try:
        return st.context.theme.type == "dark"
    except (AttributeError, RuntimeError):
        return False


def _apply_sidebar_css(dark_mode: bool) -> None:
    palette = SIDEBAR_THEME["dark" if dark_mode else "light"]
    st.html(
        f"""
        <style>
        [data-testid="stSidebar"] {{
            --sidebar-bg: {palette["sidebar_bg"]};
            --sidebar-text: {palette["sidebar_text"]};
            --sidebar-active-bg: {palette["sidebar_active_bg"]};
            --sidebar-active-text: {palette["sidebar_active_text"]};
            --sidebar-hover-bg: {palette["sidebar_hover_bg"]};
            --sidebar-divider: {palette["sidebar_divider"]};
            --sidebar-danger: {palette["sidebar_danger"]};
            --sidebar-focus: {palette["sidebar_focus"]};
            --sidebar-shadow: {palette["sidebar_shadow"]};
            background: var(--sidebar-bg) !important;
            padding: 0;
        }}

        [data-testid="stSidebar"] > div:first-child {{
            background: var(--sidebar-bg) !important;
            border: 0;
            border-right: 1px solid var(--sidebar-divider);
            border-radius: 0 1rem 1rem 0;
            box-shadow: var(--sidebar-shadow);
            color: var(--sidebar-text);
            margin: 0;
        }}

        [data-testid="stSidebarUserContent"] {{
            padding: 1rem 0.85rem 0.85rem !important;
        }}

        [data-testid="stSidebarNav"] {{
            padding: 0 0 0.7rem;
        }}

        /* Remove custom page-link containers left behind by pre-native-nav
           hot reloads. Native Streamlit navigation uses stSidebarNav. */
        [data-testid="stSidebar"] [class*="st-key-sidebar_nav"] {{
            display: none !important;
        }}

        [data-testid="stSidebar"] [class*="st-key-sidebar_footer"] {{
            padding-top: 0.7rem;
            background: var(--sidebar-bg);
            border-top: 1px solid var(--sidebar-divider);
        }}

        [data-testid="stSidebar"] [class*="st-key-sidebar_profile"] {{
            padding: 0.2rem 0.25rem 0.85rem;
        }}

        .versal-sidebar-profile {{
            color: var(--sidebar-text);
        }}

        .versal-sidebar-identity {{
            min-width: 0;
        }}

        .versal-sidebar-label {{
            margin: 0 0 0.12rem;
            font-size: 0.78rem;
            font-weight: 600;
        }}

        .versal-sidebar-email {{
            margin: 0;
            overflow: hidden;
            color: var(--sidebar-text);
            font-size: 0.75rem;
            opacity: 0.72;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        [data-testid="stSidebarNav"] [data-testid="stSidebarNavLink"] {{
            border-radius: 0.8rem;
            margin: 0.15rem 0;
            overflow: hidden;
            width: 100%;
        }}

        [data-testid="stSidebarNav"] a[href*="landing"] {{
            display: none !important;
        }}

        [data-testid="stSidebarNav"] [data-testid="stSidebarNavLink"] {{
            box-sizing: border-box;
            width: 100%;
            min-height: 2.75rem;
            justify-content: flex-start;
            gap: 0.72rem;
            padding: 0.65rem 0.8rem;
            border: 0 !important;
            border-radius: 0.8rem;
            background: transparent !important;
            color: var(--sidebar-text) !important;
            font-weight: 550;
            text-decoration: none !important;
        }}

        [data-testid="stSidebarNav"] [data-testid="stSidebarNavLink"]:not([aria-current="page"]):hover {{
            background: var(--sidebar-hover-bg) !important;
        }}

        [data-testid="stSidebarNav"] [data-testid="stSidebarNavLink"]:not([aria-current="page"]),
        [data-testid="stSidebarNav"] [data-testid="stSidebarNavLink"]:not([aria-current="page"]) * {{
            color: var(--sidebar-text) !important;
            fill: currentColor !important;
        }}

        [data-testid="stSidebarNav"] [data-testid="stSidebarNavLink"]:focus-visible,
        [data-testid="stSidebar"] [class*="st-key-sidebar_theme"] input:focus-visible + div,
        [data-testid="stSidebar"] [class*="st-key-sidebar_sign_out"] button:focus-visible {{
            outline: 3px solid var(--sidebar-focus) !important;
            outline-offset: 2px;
        }}

        [data-testid="stSidebarNav"] [data-testid="stSidebarNavLink"][aria-current="page"] {{
            background: var(--sidebar-active-bg) !important;
            color: var(--sidebar-active-text) !important;
            font-weight: 650;
        }}

        [data-testid="stSidebarNav"] [data-testid="stSidebarNavLink"][aria-current="page"] * {{
            color: var(--sidebar-active-text) !important;
            fill: currentColor !important;
        }}

        [data-testid="stSidebarNav"] [data-testid="stSidebarNavLink"]
        [data-testid="stIconMaterial"] {{
            color: currentColor !important;
            font-size: 1.3rem !important;
        }}

        [data-testid="stSidebar"] hr {{
            border-color: var(--sidebar-divider) !important;
            margin: 0.8rem 0 !important;
        }}

        [data-testid="stSidebar"] h2 {{
            border-top: 1px solid var(--sidebar-divider);
            margin-top: 0.85rem;
            padding-top: 1rem;
        }}

        [data-testid="stSidebar"] [class*="st-key-sidebar_theme"] {{
            color: var(--sidebar-text);
            min-height: 2.75rem;
        }}

        [data-testid="stSidebar"] [class*="st-key-sidebar_theme"] label {{
            min-height: 2.75rem;
            align-items: center;
        }}

        [data-testid="stSidebar"] [class*="st-key-sidebar_sign_out"] button {{
            min-height: 2.75rem;
            justify-content: flex-start;
            border: 0 !important;
            background: transparent !important;
            color: var(--sidebar-danger) !important;
            font-weight: 650;
        }}

        [data-testid="stSidebar"] [class*="st-key-sidebar_sign_out"] button:hover {{
            background: color-mix(in srgb, var(--sidebar-danger) 12%, transparent) !important;
        }}

        [data-testid="stSidebarCollapsedControl"] button {{
            min-width: 2.75rem;
            min-height: 2.75rem;
        }}

        @media (max-width: 640px) {{
            [data-testid="stSidebar"] {{
                max-width: 100vw;
                padding: 0;
            }}

            [data-testid="stSidebar"] > div:first-child {{
                margin: 0;
                border-radius: 0 0.9rem 0.9rem 0;
            }}

            [data-testid="stSidebarUserContent"] {{
                padding-inline: 0.7rem !important;
                overflow-x: hidden;
            }}
        }}
        </style>
        """
    )


def _apply_runtime_theme(dark_mode: bool) -> None:
    """Apply the existing app palette without replacing the browser session."""
    palette = RUNTIME_THEME["dark" if dark_mode else "light"]
    st.html(
        f"""
        <style>
        :root {{
            color-scheme: {palette["color_scheme"]};
            --background-color: {palette["background"]} !important;
            --secondary-background-color: {palette["secondary_background"]} !important;
            --text-color: {palette["text"]} !important;
            --muted-text-color: {palette["muted_text"]} !important;
            --border-color: {palette["border"]} !important;
        }}

        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {{
            background-color: {palette["background"]} !important;
            color: {palette["text"]} !important;
        }}

        [data-testid="stHeader"] {{
            background-color: transparent !important;
        }}

        [data-testid="stVerticalBlockBorderWrapper"],
        div[data-testid="stMetric"] {{
            border-color: {palette["border"]} !important;
        }}

        /* The sidebar toggle changes the runtime palette without replacing the
           current page. Explicitly recolour native elements whose generated
           styles otherwise retain the previous theme until a full reload. */
        [data-testid="stMain"] h1,
        [data-testid="stMain"] h2,
        [data-testid="stMain"] h3,
        [data-testid="stMain"] h4,
        [data-testid="stMain"] h5,
        [data-testid="stMain"] h6,
        [data-testid="stMain"] [data-testid="stMarkdownContainer"],
        [data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stMain"] [data-testid="stMarkdownContainer"] li,
        [data-testid="stMain"] [data-testid="stMetricLabel"],
        [data-testid="stMain"] [data-testid="stMetricLabel"] *,
        [data-testid="stMain"] [data-testid="stMetricValue"],
        [data-testid="stMain"] [data-testid="stMetricValue"] *,
        [data-testid="stMain"] label,
        [data-testid="stMain"] legend {{
            color: {palette["text"]} !important;
        }}

        [data-testid="stMain"] [data-testid="stCaptionContainer"],
        [data-testid="stMain"] [data-testid="stCaptionContainer"] *,
        [data-testid="stMain"] small {{
            color: {palette["muted_text"]} !important;
        }}

        [data-testid="stMain"] div[data-testid="stMetric"] {{
            background-color: {palette["secondary_background"]} !important;
        }}

        [data-testid="stMain"] input,
        [data-testid="stMain"] textarea,
        [data-testid="stMain"] [data-baseweb="select"] > div,
        [data-testid="stMain"] [data-baseweb="base-input"] {{
            background-color: {palette["secondary_background"]} !important;
            border-color: {palette["border"]} !important;
            color: {palette["text"]} !important;
        }}

        [data-testid="stMain"] input,
        [data-testid="stMain"] textarea,
        [data-testid="stMain"] [data-baseweb="select"] *,
        [data-testid="stMain"] [data-baseweb="base-input"] * {{
            color: {palette["text"]} !important;
        }}

        [data-testid="stMain"] [data-testid="stDataFrame"],
        [data-testid="stMain"] [data-testid="stTable"] {{
            color: {palette["text"]} !important;
            border-color: {palette["border"]} !important;
        }}
        </style>
        """
    )


def _request_streamlit_theme(dark_mode: bool) -> None:
    target = "Dark" if dark_mode else "Light"
    st.html(
        f"""
        <script>
        (() => {{
            const target = {target!r};
            const keys = Object.keys(localStorage).filter((key) =>
                key.startsWith("stActiveTheme-")
            );
            for (const key of keys) {{
                const oldValue = localStorage.getItem(key);
                const newValue = JSON.stringify(target);
                localStorage.setItem(key, newValue);
                window.dispatchEvent(new StorageEvent("storage", {{
                    key,
                    oldValue,
                    newValue,
                    storageArea: localStorage,
                    url: window.location.href,
                }}));
            }}
            document.documentElement.style.colorScheme = target.toLowerCase();
        }})();
        </script>
        """,
        unsafe_allow_javascript=True,
    )


def render_sidebar(active_page: str) -> None:
    """Render the shared protected-page navigation without changing page logic."""
    del active_page  # Streamlit's native navigation owns the active-page state.
    context_dark_mode = _is_dark_mode()
    if _THEME_KEY not in st.session_state:
        st.session_state[_THEME_KEY] = context_dark_mode
    selected_dark_mode = bool(st.session_state[_THEME_KEY])
    _apply_runtime_theme(selected_dark_mode)
    _apply_sidebar_css(selected_dark_mode)

    email = escape(current_user_email() or "Signed-in user")

    with st.sidebar:
        with st.container(key="sidebar_shell"):
            with st.container(key="sidebar_profile"):
                st.html(
                    f"""
                    <div class="versal-sidebar-profile">
                        <div class="versal-sidebar-identity">
                            <p class="versal-sidebar-label">Signed in</p>
                            <p class="versal-sidebar-email" title="{email}">{email}</p>
                        </div>
                    </div>
                    """
                )

            st.divider()

        with st.container(key="sidebar_footer"):
            selected_dark = st.toggle(
                (
                    ":material/light_mode: Light mode"
                    if selected_dark_mode
                    else ":material/dark_mode: Dark mode"
                ),
                key=_THEME_KEY,
                help="Switch between the existing light and dark themes.",
                persist_state="session",
                width="stretch",
            )
            if selected_dark != context_dark_mode:
                st.session_state[_THEME_CONTEXT_KEY] = selected_dark
                _request_streamlit_theme(selected_dark)

            if st.button(
                "Sign out",
                icon=":material/logout:",
                key="sidebar_sign_out",
                width="stretch",
            ):
                _logout_to_light()
                st.rerun()
