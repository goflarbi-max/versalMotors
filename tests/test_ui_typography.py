"""Checks for the shared VersalMotors typography contract."""

import pandas as pd

from src.ui.charts import overview_chart
from src.ui.typography import FONT_FAMILY, TYPOGRAPHY, typography_css


def test_theme_exposes_inter_with_sans_serif_fallbacks():
    family = TYPOGRAPHY["font_family"]

    assert family.startswith("Inter, system-ui")
    assert '"Segoe UI"' in family
    assert "Roboto" in family
    assert "Arial" in family
    assert family.endswith("sans-serif")
    assert "serif" not in family.replace("sans-serif", "")
    assert family == FONT_FAMILY


def test_typography_css_uses_swap_and_contains_only_font_properties():
    css = typography_css()

    assert "font-display: swap" in css
    assert "background:" not in css
    assert "color:" not in css
    assert "overflow:" not in css


def test_overview_chart_uses_shared_font_family():
    frame = pd.DataFrame(
        {"period": pd.to_datetime(["2026-01-01", "2026-02-01"]), "value": [10, 20]}
    )

    figure = overview_chart(
        frame,
        chart_type="line",
        x="period",
        y="value",
        x_label="Period",
        y_label="Value",
        series_name="Revenue",
    )

    family = FONT_FAMILY
    assert figure.layout.font.family == family
    assert figure.layout.xaxis.tickfont.family == family
    assert figure.layout.yaxis.tickfont.family == family
    assert figure.layout.legend.font.family == family
    assert figure.layout.hoverlabel.font.family == family
