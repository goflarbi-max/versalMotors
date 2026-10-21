"""Routing checks for the public landing and protected business pages."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from src.ui.landing import (
    landing_sign_in_target,
    signed_out_default_route,
)


ROOT = Path(__file__).resolve().parents[1]
LANDING = ROOT / "pages" / "landing.py"


def test_public_root_selects_landing_while_signed_out():
    assert signed_out_default_route("http://localhost:8501/") == "landing"


@pytest.mark.parametrize(
    "route",
    [
        "overview",
        "investigate",
        "ask_the_business",
        "management_brief",
        "data_quality",
    ],
)
def test_protected_urls_select_login_while_signed_out(route):
    assert signed_out_default_route(f"http://localhost:8501/{route}") == "login"


def test_landing_renders_without_database_or_ai_dependencies():
    app = AppTest.from_file(LANDING, default_timeout=15).run()

    assert not app.exception
    assert app.button(key="public_landing_sign_in").label == "Sign in"


def test_landing_sign_in_destination_depends_on_authentication():
    assert landing_sign_in_target(False) == "pages/login.py"
    assert landing_sign_in_target(True) == "pages/overview.py"
