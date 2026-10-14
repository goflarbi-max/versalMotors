"""Reusable, presentation-only components for the VersalMotors interface."""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[2]
ASSETS_DIR = ROOT / "assets"
LOGO_DARK = ASSETS_DIR / "logo_dark.png"
LOGO_LIGHT = ASSETS_DIR / "logo_light.png"
GITHUB_URL = "https://github.com/goflarbi-max/versalMotors"


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
