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
THEME_STATE_KEY = theme_module.THEME_STATE_KEY
active_theme_type = theme_module.active_theme_type
initialize_theme_state = theme_module.initialize_theme_state


# Retain these private aliases for compatibility with the existing logout test.
_THEME_KEY = THEME_STATE_KEY
_THEME_CONTEXT_KEY = "sidebar_theme_context"
EXPAND_TOGGLE_TESTID = "stExpandSidebarButton"
COLLAPSE_TOGGLE_TESTID = "stSidebarCollapseButton"


def _logout_to_light() -> None:
    """Sign out through the existing auth function and reset only UI theme state."""
    logout()
    st.session_state[_THEME_KEY] = False
    st.session_state[_THEME_CONTEXT_KEY] = False

def _apply_sidebar_css(dark_mode: bool) -> None:
    palette = SIDEBAR_THEME["dark" if dark_mode else "light"]
    st.html(
        f"""
        <style>
        /* The collapsed sidebar control is rendered in Streamlit's header, not
           inside stSidebar.  Keep its colour tokens at app scope so the
           hamburger remains visible when the sidebar itself is off-canvas. */
        .stApp {{
            --hamburger-line: {palette["hamburger_line"]};
            --hamburger-border: {palette["hamburger_border"]};
            --hamburger-hover-bg: {palette["hamburger_hover_bg"]};
            --hamburger-focus: {palette["sidebar_focus"]};
        }}

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
            font-size: 0.875rem;
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

        /* Keep Streamlit's native open/close controls and enhance only their
           artwork. If the controller cannot run, the native glyph remains. */
        button[data-testid="stExpandSidebarButton"],
        [data-testid="stExpandSidebarButton"] button,
        [data-testid="stSidebarCollapsedControl"] button,
        button[aria-label*="open sidebar" i],
        button[aria-label*="expand sidebar" i],
        [data-testid="stSidebarCollapseButton"] button,
        .versal-nav-toggle {{
            position: relative;
            min-width: 2.75rem !important;
            width: 2.75rem !important;
            min-height: 2.75rem !important;
            height: 2.75rem !important;
            padding: 0 !important;
            border: 1px solid var(--hamburger-border) !important;
            border-radius: 0.75rem !important;
            background: transparent !important;
            color: var(--hamburger-line) !important;
        }}

        /* CSS-only closed-state fallback. This guarantees the native double
           arrow is replaced even before (or without) the JS enhancement. */
        :is(
            button[data-testid="stExpandSidebarButton"],
            [data-testid="stExpandSidebarButton"] button,
            [data-testid="stSidebarCollapsedControl"] button,
            button[aria-label*="open sidebar" i],
            button[aria-label*="expand sidebar" i]
        ):not(.versal-nav-toggle) > * {{
            visibility: hidden !important;
        }}

        :is(
            button[data-testid="stExpandSidebarButton"],
            [data-testid="stExpandSidebarButton"] button,
            [data-testid="stSidebarCollapsedControl"] button,
            button[aria-label*="open sidebar" i],
            button[aria-label*="expand sidebar" i]
        ):not(.versal-nav-toggle)::before {{
            content: "";
            position: absolute;
            left: 50%;
            top: 50%;
            width: 1.375rem;
            height: 2px;
            border-radius: 999px;
            background: var(--hamburger-line);
            box-shadow:
                0 -6px 0 var(--hamburger-line),
                0 6px 0 var(--hamburger-line);
            transform: translate(-50%, -50%);
            visibility: visible !important;
            pointer-events: none;
            z-index: 2;
        }}

        .versal-nav-toggle > :not(.versal-nav-toggle-glyph) {{
            display: none !important;
        }}

        .versal-nav-toggle-glyph {{
            position: absolute;
            left: 50%;
            top: 50%;
            width: 1.375rem;
            height: 2px;
            border-radius: 999px;
            background: var(--hamburger-line);
            transform: translate(-50%, -50%);
            transition: background-color 180ms ease;
            pointer-events: none;
            z-index: 2;
        }}

        .versal-nav-toggle-glyph::before,
        .versal-nav-toggle-glyph::after {{
            content: "";
            position: absolute;
            inset: 0;
            border-radius: inherit;
            background: var(--hamburger-line);
            transition: transform 180ms ease;
        }}

        .versal-nav-toggle-glyph::before {{
            transform: translateY(-6px);
        }}

        .versal-nav-toggle-glyph::after {{
            transform: translateY(6px);
        }}

        .versal-nav-toggle[aria-expanded="true"] .versal-nav-toggle-glyph {{
            background: transparent;
        }}

        .versal-nav-toggle[aria-expanded="true"] .versal-nav-toggle-glyph::before {{
            transform: rotate(45deg);
        }}

        .versal-nav-toggle[aria-expanded="true"] .versal-nav-toggle-glyph::after {{
            transform: rotate(-45deg);
        }}

        button[data-testid="stExpandSidebarButton"]:hover,
        [data-testid="stExpandSidebarButton"] button:hover,
        [data-testid="stSidebarCollapsedControl"] button:hover,
        button[aria-label*="open sidebar" i]:hover,
        button[aria-label*="expand sidebar" i]:hover,
        [data-testid="stSidebarCollapseButton"] button:hover,
        .versal-nav-toggle:hover {{
            background: var(--hamburger-hover-bg) !important;
        }}

        button[data-testid="stExpandSidebarButton"]:focus-visible,
        [data-testid="stExpandSidebarButton"] button:focus-visible,
        [data-testid="stSidebarCollapsedControl"] button:focus-visible,
        button[aria-label*="open sidebar" i]:focus-visible,
        button[aria-label*="expand sidebar" i]:focus-visible,
        [data-testid="stSidebarCollapseButton"] button:focus-visible,
        .versal-nav-toggle:focus-visible {{
            outline: 3px solid var(--hamburger-focus) !important;
            outline-offset: 2px;
        }}

        .versal-sidebar-backdrop {{
            display: none;
        }}

        @media (prefers-reduced-motion: reduce) {{
            .versal-nav-toggle-glyph,
            .versal-nav-toggle-glyph::before,
            .versal-nav-toggle-glyph::after {{
                transition: none;
            }}
        }}

        @media (max-width: 640px) {{
            [data-testid="stSidebar"] {{
                max-width: 100vw;
                padding: 0;
                z-index: 1000000;
            }}

            [data-testid="stSidebar"] > div:first-child {{
                margin: 0;
                border-radius: 0 0.9rem 0.9rem 0;
            }}

            [data-testid="stSidebarUserContent"] {{
                padding-inline: 0.7rem !important;
                overflow-x: hidden;
            }}

            .versal-sidebar-backdrop {{
                position: fixed;
                inset: 0;
                z-index: 999999;
                display: block;
                border: 0;
                background: rgba(15, 23, 42, 0.46);
                animation: versal-sidebar-backdrop-in 180ms ease-out both;
                cursor: default;
            }}

            html.versal-mobile-nav-open,
            html.versal-mobile-nav-open body,
            html.versal-mobile-nav-open [data-testid="stAppViewContainer"] {{
                overflow: hidden !important;
                overscroll-behavior: none;
            }}
        }}

        @keyframes versal-sidebar-backdrop-in {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        </style>
        """
    )


def apply_sidebar_theme() -> bool:
    """Apply the active sidebar palette without rendering sidebar widgets."""
    selected_dark_mode = initialize_theme_state()
    _apply_sidebar_css(selected_dark_mode)
    _apply_sidebar_accessibility()
    return selected_dark_mode


def _apply_sidebar_accessibility() -> None:
    """Enhance Streamlit's native sidebar controls without replacing behavior."""
    st.html(
        """
        <script>
        (() => {
            const MOBILE_QUERY = '(max-width: 640px)';

            const enhanceButton = (button, expanded) => {
                if (!button) return;
                button.classList.add('versal-nav-toggle');
                button.setAttribute(
                    'aria-label',
                    expanded ? 'Close navigation menu' : 'Open navigation menu'
                );
                button.setAttribute('aria-expanded', String(expanded));
                button.setAttribute(
                    'title',
                    expanded ? 'Close navigation menu' : 'Open navigation menu'
                );
                if (!button.querySelector('.versal-nav-toggle-glyph')) {
                    const glyph = document.createElement('span');
                    glyph.className = 'versal-nav-toggle-glyph';
                    glyph.setAttribute('aria-hidden', 'true');
                    button.appendChild(glyph);
                }
            };

            const findOpenButton = () => {
                const knownControl = document.querySelector([
                    'button[data-testid="stExpandSidebarButton"]',
                    '[data-testid="stExpandSidebarButton"] button',
                    '[data-testid="stSidebarCollapsedControl"] button'
                ].join(','));
                if (knownControl) return knownControl;

                const nativeArrow = Array.from(document.querySelectorAll(
                    '[data-testid="stIconMaterial"], .material-symbols-rounded'
                )).find((icon) =>
                    icon.textContent.trim() === 'keyboard_double_arrow_right'
                );
                return nativeArrow ? nativeArrow.closest('button') : null;
            };

            const syncControls = () => {
                const openButton = findOpenButton();
                const closeButton = document.querySelector(
                    '[data-testid="stSidebarCollapseButton"] button'
                );
                enhanceButton(openButton, false);
                enhanceButton(closeButton, true);

                const mobileOpen = window.matchMedia(MOBILE_QUERY).matches && !!closeButton;
                let backdrop = document.querySelector('.versal-sidebar-backdrop');
                document.documentElement.classList.toggle(
                    'versal-mobile-nav-open',
                    mobileOpen
                );

                if (mobileOpen && !backdrop) {
                    backdrop = document.createElement('div');
                    backdrop.className = 'versal-sidebar-backdrop';
                    backdrop.setAttribute('aria-hidden', 'true');
                    document.body.appendChild(backdrop);
                } else if (!mobileOpen && backdrop) {
                    backdrop.remove();
                }
            };

            const closeMobileMenu = () => {
                if (!window.matchMedia(MOBILE_QUERY).matches) return;
                const closeButton = document.querySelector(
                    '[data-testid="stSidebarCollapseButton"] button'
                );
                if (closeButton) closeButton.click();
            };

            syncControls();
            if (!window.__versalSidebarControllerV2) {
                const observer = new MutationObserver(syncControls);
                observer.observe(document.body, {
                    childList: true,
                    subtree: true,
                });

                document.addEventListener('click', (event) => {
                    const target = event.target;
                    if (!(target instanceof Element)) return;
                    if (target.closest('.versal-sidebar-backdrop')) {
                        event.preventDefault();
                        closeMobileMenu();
                        return;
                    }
                    if (target.closest('[data-testid="stSidebarNavLink"]')) {
                        window.setTimeout(closeMobileMenu, 0);
                    }
                });

                document.addEventListener('keydown', (event) => {
                    if (event.key !== 'Escape') return;
                    const closeButton = document.querySelector(
                        '[data-testid="stSidebarCollapseButton"] button'
                    );
                    if (window.matchMedia(MOBILE_QUERY).matches && closeButton) {
                        event.preventDefault();
                        event.stopPropagation();
                        closeButton.click();
                    }
                }, true);

                window.addEventListener('resize', syncControls, { passive: true });
                window.__versalSidebarControllerV2 = { observer, syncControls };
            } else {
                window.__versalSidebarControllerV2.syncControls();
            }
        })();
        </script>
        """,
        unsafe_allow_javascript=True,
    )


def render_sidebar(active_page: str) -> None:
    """Render the shared protected-page navigation without changing page logic."""
    del active_page  # Streamlit's native navigation owns the active-page state.
    selected_dark_mode = apply_sidebar_theme()

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
            st.toggle(
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

            if st.button(
                "Sign out",
                icon=":material/logout:",
                key="sidebar_sign_out",
                width="stretch",
            ):
                _logout_to_light()
                st.rerun()
