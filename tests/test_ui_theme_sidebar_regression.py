"""Regression coverage for protected-page theming and native sidebar controls."""

import inspect
from pathlib import Path

import streamlit
from streamlit.testing.v1 import AppTest

from src.ui import sidebar, theme


def test_light_and_dark_palettes_are_distinct_and_state_driven():
    assert theme.active_theme_type({}) == "light"
    assert theme.active_theme_type({theme.THEME_STATE_KEY: False}) == "light"
    assert theme.active_theme_type({theme.THEME_STATE_KEY: True}) == "dark"
    assert theme.RUNTIME_THEME["light"] != theme.RUNTIME_THEME["dark"]
    assert theme.RUNTIME_THEME["dark"]["background"] == "#0F172A"
    assert theme.SIDEBAR_THEME["light"] != theme.SIDEBAR_THEME["dark"]


def test_login_theme_is_always_light():
    assert theme.login_theme_type() == "light"


def test_toggle_updates_theme_once_without_changing_sidebar_state(tmp_path):
    probe = tmp_path / "theme_toggle_probe.py"
    probe.write_text(
        """
import streamlit as st
from src.ui.theme import THEME_STATE_KEY, active_theme_type, initialize_theme_state

st.session_state["run_count"] = st.session_state.get("run_count", 0) + 1
st.session_state.setdefault("sidebar_open_probe", True)
initialize_theme_state()
st.toggle("Dark mode", key=THEME_STATE_KEY)
st.write(active_theme_type())
""".strip(),
        encoding="utf-8",
    )

    app = AppTest.from_file(probe, default_timeout=10).run()
    assert app.session_state[theme.THEME_STATE_KEY] is False
    assert app.session_state["run_count"] == 1
    assert app.session_state["sidebar_open_probe"] is True

    app.toggle[0].set_value(True).run()

    assert not app.exception
    assert app.session_state[theme.THEME_STATE_KEY] is True
    assert app.session_state["run_count"] == 2
    assert app.session_state["sidebar_open_probe"] is True
    assert app.markdown[-1].value == "dark"


def test_sidebar_toggle_selectors_exist_in_installed_streamlit_frontend():
    static_root = Path(streamlit.__file__).resolve().parent / "static"
    javascript = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in static_root.rglob("*.js")
        if path.is_file()
    )

    assert sidebar.EXPAND_TOGGLE_TESTID in javascript
    assert sidebar.COLLAPSE_TOGGLE_TESTID in javascript

    css_source = inspect.getsource(sidebar._apply_sidebar_css)
    assert f'button[data-testid="{sidebar.EXPAND_TOGGLE_TESTID}"]' in css_source
    assert f'[data-testid="{sidebar.COLLAPSE_TOGGLE_TESTID}"] button' in css_source


def test_sidebar_controller_preserves_native_toggle_and_mobile_accessibility():
    controller_source = inspect.getsource(sidebar._apply_sidebar_accessibility)

    assert "versal-nav-toggle-glyph" in controller_source
    assert "stSidebarCollapsedControl" in controller_source
    assert "keyboard_double_arrow_right" in controller_source
    assert "aria-expanded" in controller_source
    assert "Open navigation menu" in controller_source
    assert "Close navigation menu" in controller_source
    assert "stSidebarNavLink" in controller_source
    assert "versal-sidebar-backdrop" in controller_source
    assert "Escape" in controller_source
    assert "closeButton.click()" in controller_source


def test_download_buttons_use_the_active_runtime_palette():
    runtime_source = inspect.getsource(theme.apply_runtime_theme)

    assert 'data-testid="stDownloadButton"' in runtime_source
    assert 'palette["secondary_background"]' in runtime_source
    assert 'palette["text"]' in runtime_source
    assert 'palette["focus"]' in runtime_source
