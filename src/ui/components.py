"""Reusable, presentation-only components for the VersalMotors interface."""

from __future__ import annotations

import base64
from html import escape
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[2]
ASSETS_DIR = ROOT / "assets"
LOGO_DARK = ASSETS_DIR / "logo_dark.png"
LOGO_LIGHT = ASSETS_DIR / "logo_light.png"
GITHUB_URL = "https://github.com/goflarbi-max/versalMotors"

_OVERVIEW_ICONS = {
    "payments",
    "account_balance_wallet",
    "directions_car",
    "percent",
    "show_chart",
    "location_on",
}


def _overview_icon(icon: str, *, size: int = 20) -> str:
    """Return a whitelisted Material Symbol using Streamlit's loaded font."""
    icon_name = icon if icon in _OVERVIEW_ICONS else "show_chart"
    return (
        f'<span class="material-symbols-rounded" aria-hidden="true" '
        f'style="font-size:{size}px">{icon_name}</span>'
    )


def current_theme_type() -> str | None:
    """Return Streamlit's active theme when the installed version exposes it."""
    try:
        theme_type = st.context.theme.type
    except (AttributeError, RuntimeError):
        return None
    return theme_type if theme_type in {"light", "dark"} else None


def active_logo_path() -> Path:
    """Return the contrasting logo for the active theme, defaulting safely to light."""
    return LOGO_LIGHT if current_theme_type() == "dark" else LOGO_DARK


def _data_uri(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def render_logo(width: int) -> None:
    """Render the logo using Streamlit's current text colour as its artwork colour.

    The transparent logo supplies the alpha mask. Inheriting ``currentColor``
    makes the artwork dark in light mode and white in dark mode, including the
    first render when Python theme context is not yet available.
    """
    st.html(
        f"""
        <div
          class="versal-theme-logo"
          role="img"
          aria-label="VersalMotors"
          style="
            width: min(100%, {width}px);
            aspect-ratio: 505 / 202;
            margin-inline: auto;
            background-color: currentColor;
            -webkit-mask: url('{_data_uri(LOGO_DARK)}') center / contain no-repeat;
            mask: url('{_data_uri(LOGO_DARK)}') center / contain no-repeat;
          "
        ></div>
        """
    )


def kpi_card(
    label: str,
    value: str,
    change: str | None,
    footer_text: str,
    icon: str,
) -> None:
    """Render an escaped, presentation-only Overview KPI card."""
    safe_label = escape(str(label))
    safe_value = escape(str(value))
    safe_footer = escape(str(footer_text))
    safe_icon = escape(str(icon))

    badge_html = ""
    comparison_html = ""
    if change:
        change_text = str(change).strip()
        badge_value, separator, comparison = change_text.partition(" vs ")
        tone = "down" if badge_value.startswith("-") else "up" if badge_value.startswith("+") else "neutral"
        arrow = "↓" if tone == "down" else "↑" if tone == "up" else "→"
        safe_badge = escape(badge_value)
        comparison_text = f"vs {comparison}" if separator else ""
        badge_html = (
            f'<span class="versal-overview-change versal-overview-change--{tone}">'
            f'<span aria-hidden="true">{arrow}</span>{safe_badge}</span>'
        )
        comparison_html = (
            '<div class="versal-overview-kpi-divider"></div>'
            '<div class="versal-overview-kpi-footer">'
            '<div class="versal-overview-kpi-footer-copy">'
            f'<strong>{safe_badge}</strong><span>{escape(comparison_text)}</span>'
            '</div></div>'
        )

    st.html(
        f"""
        <div class="versal-overview-kpi-outer">
          <div class="versal-overview-kpi-inner">
            <div class="versal-overview-kpi-head">
              <p class="versal-overview-kpi-label">{safe_label}</p>
              <span class="versal-overview-icon-tile" aria-hidden="true">
                {_overview_icon(safe_icon)}
              </span>
            </div>
            <div class="versal-overview-kpi-value-row">
              <span class="versal-overview-kpi-value">{safe_value}</span>
              {badge_html}
            </div>
            <p class="versal-overview-kpi-question">{safe_footer}</p>
            {comparison_html}
          </div>
        </div>
        """
    )


def overview_chart_header(eyebrow: str, title: str, caption: str, icon: str) -> None:
    """Render an escaped header for an Overview chart card."""
    st.html(
        f"""
        <div class="versal-overview-chart-head">
          <div class="versal-overview-chart-copy">
            <p class="versal-overview-chart-eyebrow">{escape(str(eyebrow))}</p>
            <p class="versal-overview-chart-title">{escape(str(title))}</p>
            <p class="versal-overview-chart-caption">{escape(str(caption))}</p>
          </div>
          <span class="versal-overview-icon-tile" aria-hidden="true">
            {_overview_icon(str(icon))}
          </span>
        </div>
        """
    )
