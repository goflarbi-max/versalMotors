"""Shared visual styling for the Streamlit shell and landing page."""

import streamlit as st


def apply_login_theme() -> None:
    """Apply login-only chrome hiding and responsive card styling."""
    st.html(
        """
        <span id="versal-theme-bootstrap" hidden></span>
        <script>
        (() => {
            const sessionMarker = "versalMotorsLightThemeInitialized";
            if (sessionStorage.getItem(sessionMarker) !== "true") {
                const themeKeys = Object.keys(localStorage).filter((key) =>
                    key.startsWith("stActiveTheme-")
                );
                let changed = false;

                for (const key of themeKeys) {
                    const stored = localStorage.getItem(key);
                    let selected = stored;
                    try {
                        selected = JSON.parse(stored);
                    } catch (_) {
                        // Older Streamlit versions may store the value without JSON encoding.
                    }
                    if (selected !== "Light") {
                        localStorage.setItem(key, JSON.stringify("Light"));
                        changed = true;
                    }
                }

                sessionStorage.setItem(sessionMarker, "true");
                if (changed) {
                    window.location.reload();
                    return;
                }
            }

        })();
        </script>
        """,
        unsafe_allow_javascript=True,
    )
    try:
        dark_mode = st.context.theme.type == "dark"
    except (AttributeError, RuntimeError):
        dark_mode = False

    login_glass = {
        "light": {
            "card_background": "rgba(255, 255, 255, 0.64)",
            "fallback_background": "rgba(255, 255, 255, 0.96)",
            "card_border": "rgba(255, 255, 255, 0.78)",
            "card_shadow": "0 24px 65px rgba(15, 23, 42, 0.18)",
            "shape_one": "rgba(99, 102, 241, 0.20)",
            "shape_two": "rgba(56, 189, 248, 0.17)",
        },
        "dark": {
            "card_background": "rgba(20, 24, 35, 0.56)",
            "fallback_background": "rgba(15, 23, 42, 0.96)",
            "card_border": "rgba(255, 255, 255, 0.18)",
            "card_shadow": "0 24px 65px rgba(0, 0, 0, 0.38)",
            "shape_one": "rgba(99, 102, 241, 0.16)",
            "shape_two": "rgba(14, 165, 233, 0.12)",
        },
    }
    glass = login_glass["dark" if dark_mode else "light"]
    card_text = "#F8FAFC" if dark_mode else "#0F172A"
    muted_text = "#CBD5E1" if dark_mode else "#64748B"
    field_background = "#111827" if dark_mode else "#F8FAFC"
    field_border = "#334155" if dark_mode else "#CBD5E1"
    page_background = "#020617" if dark_mode else "#F8FAFC"

    st.html(
        f"""
        <style>
        [data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        footer {{
            display: none !important;
        }}

        .stApp,
        [data-testid="stAppViewContainer"] {{
            background: {page_background};
            height: 100dvh;
            overflow: hidden !important;
        }}

        html,
        body,
        [data-testid="stAppViewContainer"] > .main {{
            height: 100dvh;
            overflow: hidden !important;
        }}

        .block-container {{
            width: 100%;
            max-width: 100% !important;
            padding: 1rem !important;
            height: 100dvh;
            overflow: hidden !important;
        }}

        [class*="st-key-login_shell"] {{
            width: 100%;
            height: calc(100dvh - 2rem);
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            isolation: isolate;
        }}

        [class*="st-key-login_shell"] > div {{
            width: 100%;
            position: relative;
            z-index: 1;
        }}

        [class*="st-key-login_shell"]::before,
        [class*="st-key-login_shell"]::after {{
            content: "";
            position: absolute;
            z-index: 0;
            width: min(46vw, 520px);
            aspect-ratio: 1;
            border-radius: 50%;
            filter: blur(42px);
            opacity: 0.9;
            pointer-events: none;
        }}

        [class*="st-key-login_shell"]::before {{
            top: -18%;
            left: 8%;
            background: {glass["shape_one"]};
        }}

        [class*="st-key-login_shell"]::after {{
            right: 7%;
            bottom: -22%;
            background: {glass["shape_two"]};
        }}

        [class*="st-key-login_card"] {{
            width: min(100%, 420px);
            margin-inline: auto;
            padding: 1.5rem 2rem;
            border: 1px solid {glass["card_border"]};
            border-radius: 16px !important;
            background: {glass["card_background"]};
            color: {card_text};
            box-shadow: {glass["card_shadow"]};
            -webkit-backdrop-filter: blur(18px) saturate(140%);
            backdrop-filter: blur(18px) saturate(140%);
        }}

        @supports not ((-webkit-backdrop-filter: blur(1px)) or
                       (backdrop-filter: blur(1px))) {{
            [class*="st-key-login_card"] {{
                background: {glass["fallback_background"]};
            }}
        }}

        [class*="st-key-login_card"] h1 {{
            color: {card_text};
            font-size: clamp(1.45rem, 4vw, 1.9rem);
            line-height: 1.2;
            margin-bottom: 0;
        }}

        [class*="st-key-login_card"] label,
        [class*="st-key-login_card"] p {{
            color: {card_text};
        }}

        [class*="st-key-login_card"] [data-baseweb="input"] {{
            min-height: 3rem;
            border-color: {field_border};
            background: {field_background};
        }}

        [class*="st-key-login_card"] [data-baseweb="input"] input {{
            color: {card_text};
        }}

        [class*="st-key-login_card"] [data-baseweb="input"] input::placeholder {{
            color: {muted_text};
            opacity: 0.82;
        }}

        [class*="st-key-login_card"] [data-testid="stButton"] button[kind="primary"] {{
            min-height: 3.25rem;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 700;
        }}

        [class*="st-key-forgot_password_row"] button {{
            min-height: auto;
            padding: 0.15rem 0 !important;
            color: #6366F1 !important;
            font-weight: 650;
        }}

        .versal-login-subtitle {{
            margin: -0.15rem 0 0.4rem;
            color: {muted_text} !important;
            text-align: center;
            font-size: 0.98rem;
        }}

        @media (max-width: 480px) {{
            .block-container {{
                padding: 0.75rem !important;
            }}

            [class*="st-key-login_shell"] {{
                height: calc(100dvh - 1.5rem);
            }}

            [class*="st-key-login_card"] {{
                padding: 1.1rem;
                border-radius: 14px !important;
            }}

            [class*="st-key-login_shell"]::before,
            [class*="st-key-login_shell"]::after {{
                width: 72vw;
                filter: blur(32px);
            }}
        }}
        </style>
        """
    )


def hide_landing_navigation() -> None:
    """Hide sidebar navigation and its reveal control on the landing route only."""
    st.html(
        """
        <style>
        [data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"] {
            display: none !important;
        }
        </style>
        """
    )


def apply_theme() -> None:
    """Apply existing shell polish plus responsive landing-page styles."""
    try:
        dark_mode = st.context.theme.type == "dark"
    except (AttributeError, RuntimeError):
        dark_mode = False

    landing_button_theme = {
        "button_primary_bg": "#0F0F3D",
        "button_primary_hover": "#1A1A5E",
        "button_secondary_bg": "#D92D20",
        "button_secondary_hover": "#B42318",
        "button_text": "#FFFFFF",
        "button_focus_ring": "#6366F1",
        "button_primary_shadow": (
            "0 10px 24px rgba(15, 15, 61, 0.30), "
            "0 0 0 1px rgba(255, 255, 255, 0.24)"
            if dark_mode
            else "0 10px 24px rgba(15, 15, 61, 0.24)"
        ),
        "button_secondary_shadow": "0 10px 24px rgba(180, 35, 24, 0.24)",
    }
    st.html(
        f"""
        <style>
        :root {{
            --landing-button-primary-bg: {landing_button_theme["button_primary_bg"]};
            --landing-button-primary-hover: {landing_button_theme["button_primary_hover"]};
            --landing-button-secondary-bg: {landing_button_theme["button_secondary_bg"]};
            --landing-button-secondary-hover: {landing_button_theme["button_secondary_hover"]};
            --landing-button-text: {landing_button_theme["button_text"]};
            --landing-button-focus-ring: {landing_button_theme["button_focus_ring"]};
            --landing-button-primary-shadow: {landing_button_theme["button_primary_shadow"]};
            --landing-button-secondary-shadow: {landing_button_theme["button_secondary_shadow"]};
        }}
        </style>
        """
    )
    st.html(
        """
        <style>
        * {
            transition: background-color 0.2s, color 0.2s, border-color 0.2s;
        }

        .stApp::before {
            content: "";
            position: fixed;
            inset: 0 0 auto 0;
            height: 4px;
            background: linear-gradient(90deg, #4F46E5, #7C3AED);
            z-index: 999999;
            pointer-events: none;
        }

        /* Keep Streamlit's heading permalink icon out of the user interface. */
        [data-testid="stHeadingWithActionElements"] a[href^="#"] {
            display: none !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"],
        div[data-testid="stContainer"] {
            border-radius: 14px !important;
        }

        div[data-testid="stMetric"] {
            border-radius: 14px !important;
            min-width: 100% !important;
            min-height: 140px !important;
            padding: 24px !important;
            overflow: visible !important;
        }

        [class*="st-key-overview_kpi_"] {
            min-height: 200px !important;
            overflow: visible !important;
        }

        [class*="st-key-overview_kpi_"] [data-testid="stVerticalBlockBorderWrapper"] {
            min-height: 200px !important;
            overflow: visible !important;
        }

        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] * {
            font-size: 32px !important;
            font-weight: 700 !important;
            opacity: 1 !important;
            max-width: none !important;
            overflow: visible !important;
            text-overflow: clip !important;
            white-space: nowrap !important;
        }

        div[data-testid="stMetricDelta"],
        div[data-testid="stMetricDelta"] * {
            opacity: 1 !important;
        }

        [data-testid="stDataFrame"],
        [data-testid="stVegaLiteChart"],
        [data-testid="stArrowVegaLiteChart"] {
            border-radius: 12px !important;
            overflow: hidden;
        }

        [class*="st-key-sidebar_brand"] {
            padding: 0.25rem 0.25rem 0.75rem;
        }

        [class*="st-key-sidebar_brand"] img {
            max-width: 100%;
            height: auto;
        }

        [class*="st-key-landing_account"] {
            position: fixed;
            /* Sit below Streamlit's deployment toolbar instead of behind it. */
            top: 3.5rem;
            right: 1rem;
            z-index: 1000001;
            width: auto;
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            gap: 0.55rem !important;
            padding: 0.25rem 0.45rem 0.25rem 0.75rem;
            border: 1px solid color-mix(in srgb, currentColor 18%, transparent);
            border-radius: 999px;
            background: color-mix(in srgb, var(--background-color, #FFFFFF) 92%, transparent);
            backdrop-filter: blur(10px);
        }

        [class*="st-key-landing_account"] p {
            max-width: 14rem;
            margin: 0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        [class*="st-key-landing_account"] button {
            min-height: 2.25rem;
        }

        [class*="st-key-landing_shell"] {
            max-width: 900px;
            min-height: calc(100vh - 6.5rem);
            margin: 0 auto;
            display: flex;
            align-items: center;
        }

        [class*="st-key-landing_shell"] > div {
            width: 100%;
        }

        [class*="st-key-landing_content"] {
            text-align: center;
        }

        [class*="st-key-landing_content"] img {
            max-width: 100%;
            height: auto;
        }

        [class*="st-key-landing_actions"] {
            width: 100%;
            justify-content: center;
            gap: 0.8rem !important;
        }

        [class*="st-key-landing_actions"] > [data-testid="stElementContainer"] {
            flex: 0 0 auto;
            width: 15rem !important;
            max-width: none;
        }

        [class*="st-key-landing_actions"] [data-testid="stPageLink"] {
            width: 100% !important;
        }

        [class*="st-key-landing_actions"] [data-testid="stPageLink"] a {
            width: 100% !important;
            min-height: 3rem;
            justify-content: center;
            align-items: center;
            gap: 0.5rem;
            padding: 0.55rem 1rem;
            border: 0 !important;
            border-radius: 999px;
            color: var(--landing-button-text) !important;
            font-size: 1.1rem;
            font-weight: 700;
            line-height: 1.2;
            text-align: left;
            text-decoration: none;
            box-shadow: none;
            transform: translateY(0);
            transition: background-color 180ms ease, box-shadow 180ms ease,
                        transform 180ms ease;
        }

        [class*="st-key-landing_actions"] [data-testid="stPageLink"] a * {
            color: var(--landing-button-text) !important;
        }

        [class*="st-key-landing_actions"] [data-testid="stPageLink"] a p {
            margin: 0;
            font-size: 1.1rem;
        }

        [class*="st-key-landing_actions"] [data-testid="stPageLink"]
        a [data-testid="stIconMaterial"] {
            width: 1.2rem;
            height: 1.2rem;
            font-size: 1.2rem !important;
            line-height: 1;
        }

        [class*="st-key-landing_actions"] [data-testid="stPageLink"] a::after {
            content: none !important;
            display: none !important;
        }

        [class*="st-key-landing_actions"] > [data-testid="stElementContainer"]:nth-child(1)
        [data-testid="stPageLink"] a {
            background: var(--landing-button-primary-bg);
            box-shadow: var(--landing-button-primary-shadow);
        }

        [class*="st-key-landing_actions"] > [data-testid="stElementContainer"]:nth-child(2)
        [data-testid="stPageLink"] a {
            background: var(--landing-button-secondary-bg);
            box-shadow: var(--landing-button-secondary-shadow);
        }

        [class*="st-key-landing_actions"] > [data-testid="stElementContainer"]:nth-child(1)
        [data-testid="stPageLink"] a:hover {
            background: var(--landing-button-primary-hover);
            box-shadow: 0 13px 28px rgba(15, 15, 61, 0.32);
            transform: translateY(-2px);
        }

        [class*="st-key-landing_actions"] > [data-testid="stElementContainer"]:nth-child(2)
        [data-testid="stPageLink"] a:hover {
            background: var(--landing-button-secondary-hover);
            box-shadow: 0 13px 28px rgba(180, 35, 24, 0.30);
            transform: translateY(-2px);
        }

        [class*="st-key-landing_actions"] [data-testid="stPageLink"] a:active {
            transform: translateY(0) scale(0.99);
        }

        [class*="st-key-landing_actions"] [data-testid="stPageLink"] a:focus-visible {
            outline: 3px solid var(--landing-button-text);
            outline-offset: 3px;
            box-shadow: 0 0 0 6px var(--landing-button-focus-ring);
        }

        .versal-landing-description {
            max-width: 680px;
            margin: 0 auto;
            font-size: 1.05rem;
            line-height: 1.55;
            opacity: 0.78;
        }

        .versal-landing-footer {
            margin-top: 1.75rem;
            text-align: center;
            font-size: 0.85rem;
            opacity: 0.72;
        }

        .versal-landing-footer a {
            color: inherit;
        }

        .versal-logo-fallback {
            display: flex;
            justify-content: center;
            width: 100%;
        }

        @media (max-width: 640px) {
            .block-container {
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }

            [class*="st-key-landing_shell"] {
                min-height: auto;
                padding-top: 1.25rem;
                padding-bottom: 1.5rem;
            }

            [class*="st-key-landing_actions"] > [data-testid="stElementContainer"] {
                flex-basis: 100%;
                max-width: none;
                width: 100%;
            }

            [class*="st-key-landing_actions"] [data-testid="stPageLink"] {
                width: 100% !important;
            }

            [class*="st-key-landing_actions"] [data-testid="stPageLink"] a {
                width: 100% !important;
                min-height: 3rem;
            }

            .versal-landing-description {
                font-size: 0.98rem;
            }

            [class*="st-key-landing_account"] {
                top: 3.25rem;
                right: 0.65rem;
                max-width: calc(100vw - 1.3rem);
            }

            [class*="st-key-landing_account"] p {
                max-width: 9rem;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                transition-duration: 0.01ms !important;
            }
        }
        </style>
        """
    )
