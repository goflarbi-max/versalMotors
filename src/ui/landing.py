"""Public VersalMotors landing page and route-selection helpers."""

from __future__ import annotations

import base64
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

import streamlit as st

from src.auth.auth import is_authenticated
from src.ui.theme import PUBLIC_LANDING_THEME, apply_public_landing_theme


ROOT = Path(__file__).resolve().parents[2]
LOGO_LIGHT = ROOT / "assets" / "logo_light.png"
PROTECTED_ROUTES = frozenset(
    {
        "overview",
        "investigate",
        "ask_the_business",
        "management_brief",
        "data_quality",
    }
)


def current_route(url: str | None) -> str:
    """Return the final normalized path segment for a Streamlit request URL."""
    if not url:
        return ""
    path = urlsplit(str(url)).path.strip("/")
    return path.rsplit("/", 1)[-1].lower() if path else ""


def signed_out_default_route(url: str | None) -> str:
    """Select Login for protected URLs and Landing for ordinary browser visits.

    ``st.context.url`` is unavailable in Streamlit's in-process AppTest. Keeping
    Login as that environment's default preserves the established authentication
    tests while real browser requests use their concrete URL.
    """
    if url is None:
        return "login"
    return "login" if current_route(url) in PROTECTED_ROUTES else "landing"


def landing_sign_in_target(authenticated: bool) -> str:
    """Return the registered destination for the landing Sign in control."""
    return "pages/overview.py" if authenticated else "pages/login.py"


@st.cache_data(show_spinner=False)
def _light_logo_data_uri() -> str:
    """Read the existing white logo once and return a deploy-safe data URI."""
    encoded = base64.b64encode(LOGO_LIGHT.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _svg_data_uri(svg: str) -> str:
    """Encode a small, repository-owned SVG so Streamlit cannot strip its paths."""
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def _card_markup(icon_uri: str, icon_alt: str, title: str, description: str) -> str:
    safe_title = escape(title)
    safe_description = escape(description)
    safe_alt = escape(icon_alt, quote=True)
    return f"""
        <article class="versal-public-card">
            <span class="versal-public-card-icon">
                <img src="{icon_uri}" alt="{safe_alt}">
            </span>
            <div>
                <h2>{safe_title}</h2>
                <p>{safe_description}</p>
            </div>
        </article>
    """


def _wave_markup() -> str:
    """Return the hook for the lightweight CSS radial-gradient dot wave."""
    return '<div class="versal-public-wave" aria-hidden="true"></div>'


def _analytics_icons() -> str:
    """Return five decorative, sanitizer-safe inline analytics SVGs."""
    stroke = PUBLIC_LANDING_THEME["landing_icon_stroke"]
    drawings = (
        '<path d="M4 19.5h16M6.5 17V11h3v6m2.5 0V6.5h3V17m2.5 0V9h3v8"/>',
        '<path d="M4 19.5h16M5.5 16l4-4 3 2.5 6-7M15.5 7.5h3v3"/>',
        '<path d="M11 3.8a8.2 8.2 0 1 0 8.2 8.2H11V3.8Z"/>'
        '<path d="M14 3.8v5.3h5.3A8.2 8.2 0 0 0 14 3.8Z"/>',
        '<path d="M4.5 17.5a8 8 0 0 1 15 0M7.3 14.5l-1.5-1.2m10.9 1.2 1.5-1.2M12 12V8m0 8.5 3.6-4.4"/>',
        '<path d="M4 18.5V6h12v7.5M7 15l2.5-3 2.2 1.7 2.8-4.2"/>'
        '<circle cx="16.5" cy="16.5" r="3.5"/><path d="m19 19 2 2"/>',
    )
    icons = []
    for drawing in drawings:
        svg = f"""
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
               aria-hidden="true">
            <g fill="none" stroke="{stroke}" stroke-width="1.75"
               stroke-linecap="round" stroke-linejoin="round">
              {drawing}
            </g>
          </svg>"""
        icons.append(
            '<span class="versal-public-analytics-icon" aria-hidden="true">'
            f'<img src="{_svg_data_uri(svg)}" alt="" aria-hidden="true">'
            "</span>"
        )
    return '<div class="versal-public-analytics-icons" aria-hidden="true">' + "".join(icons) + "</div>"


def render_landing() -> None:
    """Render the public, theme-independent landing page without business calls."""
    apply_public_landing_theme()

    headline = escape("Analyze Your Data with Precision")
    description = escape(
        "VersalMotors Business Intelligence brings sales, inventory, servicing, "
        "warranty claims, complaints and customer satisfaction into one clear view. "
        "Spot what is changing, investigate the cause, and make decisions backed by "
        "evidence from your own data."
    )
    logo_uri = _light_logo_data_uri()

    with st.container(key="public_landing_shell"):
        with st.container(key="public_landing_hero"):
            st.html(_wave_markup())
            with st.container(
                horizontal=True,
                horizontal_alignment="distribute",
                vertical_alignment="center",
                wrap=False,
                key="public_landing_topbar",
            ):
                st.html(
                    f'<img class="versal-public-logo" src="{logo_uri}" '
                    'alt="VersalMotors">'
                )
                if st.button(
                    "Sign in",
                    key="public_landing_sign_in",
                    width="content",
                ):
                    st.switch_page(landing_sign_in_target(is_authenticated()))

            with st.container(key="public_landing_copy"):
                st.html(
                    f"""
                    <div class="versal-public-copy">
                        <h1>{headline}</h1>
                        <p>{description}</p>
                        {_analytics_icons()}
                    </div>
                    """
                )

        with st.container(key="public_landing_band"):
            evidence_icon = _svg_data_uri("""
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" role="img" aria-label="Evidence">
                <g fill="none" stroke="#1450B8" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="10.5" cy="10.5" r="6.25"/>
                <path d="m15.2 15.2 4.4 4.4M8 10.5l1.7 1.7 3.5-3.8"/>
                </g>
              </svg>""")
            analytics_icon = _svg_data_uri("""
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" role="img" aria-label="Analytics">
                <g fill="none" stroke="#1450B8" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 8.2a3.8 3.8 0 1 0 0 7.6 3.8 3.8 0 0 0 0-7.6Z"/>
                <path d="m19 13.5 1.6 1.2-2 3.4-1.9-.8a7.8 7.8 0 0 1-2.2 1.3l-.3 2H10l-.3-2a7.8 7.8 0 0 1-2.2-1.3l-1.9.8-2-3.4 1.6-1.2a7.3 7.3 0 0 1 0-2.6L3.6 9.7l2-3.4 1.9.8a7.8 7.8 0 0 1 2.2-1.3l.3-2h4.1l.3 2a7.8 7.8 0 0 1 2.2 1.3l1.9-.8 2 3.4-1.6 1.2a7.3 7.3 0 0 1 .1 2.6Z"/>
                </g>
              </svg>""")
            chat_icon = _svg_data_uri("""
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" role="img" aria-label="Conversation">
                <g fill="none" stroke="#1450B8" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M5 5.2h14a2 2 0 0 1 2 2v8.1a2 2 0 0 1-2 2h-8l-5.2 3v-3H5a2 2 0 0 1-2-2V7.2a2 2 0 0 1 2-2Z"/>
                <path d="M7.5 9.2h9M7.5 13h6.2"/>
                </g>
              </svg>""")
            cards = "".join(
                (
                    _card_markup(
                        evidence_icon,
                        "Evidence",
                        "Evidence you can trace",
                        "Every finding shows the data and the query behind it.",
                    ),
                    _card_markup(
                        analytics_icon,
                        "Analytics",
                        "Advanced Analytics",
                        "Spot unusual patterns across sales, inventory, warranty and complaints.",
                    ),
                    _card_markup(
                        chat_icon,
                        "Conversation",
                        "Ask in plain language",
                        "Get answers grounded in your own business data, with the facts kept separate from opinion.",
                    ),
                )
            )
            st.html(f'<div class="versal-public-cards">{cards}</div>')
