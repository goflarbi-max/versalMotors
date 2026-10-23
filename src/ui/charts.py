"""Plotly rendering helpers used only by the Business Overview page."""

from __future__ import annotations

from typing import Literal

import pandas as pd
import plotly.graph_objects as go

from src.ui.theme import TYPOGRAPHY_THEME, active_overview_theme


OVERVIEW_CHART_HEIGHT = 400


def overview_chart(
    data: pd.DataFrame,
    *,
    chart_type: Literal["line", "horizontal_bar"],
    x: str,
    y: str,
    x_label: str,
    y_label: str,
    series_name: str,
) -> go.Figure:
    """Build the existing Overview chart type from the unchanged source frame."""
    palette = active_overview_theme()
    primary = palette["chart_palette"][0]

    if chart_type == "line":
        figure = go.Figure(
            go.Scatter(
                x=data[x],
                y=data[y],
                name=series_name,
                mode="lines",
                line={"color": primary, "width": 2.4, "shape": "spline"},
                fill="tozeroy",
                fillcolor="rgba(22, 192, 96, 0.10)",
                fillgradient={
                    "type": "vertical",
                    "colorscale": [
                        [0, "rgba(22, 192, 96, 0.02)"],
                        [1, "rgba(22, 192, 96, 0.22)"],
                    ],
                },
                hovertemplate=(
                    "<b>%{x|%b %Y}</b><br>"
                    f"{series_name}: %{{y:,.0f}}<extra></extra>"
                ),
            )
        )
    else:
        figure = go.Figure(
            go.Bar(
                x=data[y],
                y=data[x],
                name=series_name,
                orientation="h",
                marker={"color": primary, "cornerradius": 6},
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    f"{series_name}: %{{x:,.0f}}<extra></extra>"
                ),
            )
        )

    figure.update_layout(
        height=OVERVIEW_CHART_HEIGHT,
        margin={"l": 12, "r": 12, "t": 28, "b": 12},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={
            "color": palette["text"],
            "family": TYPOGRAPHY_THEME["font_family"],
            "size": 12,
        },
        hovermode="closest",
        hoverlabel={
            "bgcolor": palette["chart_tooltip_bg"],
            "bordercolor": palette["card_outer_border"],
            "font": {
                "color": palette["chart_tooltip_text"],
                "family": TYPOGRAPHY_THEME["font_family"],
                "size": 12,
            },
        },
        legend={
            "orientation": "h",
            "x": 1,
            "xanchor": "right",
            "y": 1.08,
            "yanchor": "bottom",
            "font": {
                "color": palette["label_muted"],
                "family": TYPOGRAPHY_THEME["font_family"],
                "size": 12,
            },
            "itemsizing": "constant",
        },
        bargap=0.28,
    )
    horizontal = chart_type == "horizontal_bar"
    figure.update_xaxes(
        title_text=y_label if horizontal else x_label,
        showline=False,
        zeroline=False,
        showgrid=True,
        gridcolor=palette["chart_grid"],
        griddash="dash",
        tickfont={"color": palette["label_muted"], "family": TYPOGRAPHY_THEME["font_family"], "size": 12},
        title_font={"color": palette["label_muted"], "family": TYPOGRAPHY_THEME["font_family"], "size": 12},
        automargin=True,
    )
    figure.update_yaxes(
        title_text=x_label if horizontal else y_label,
        showline=False,
        zeroline=False,
        showgrid=chart_type == "line",
        gridcolor=palette["chart_grid_subtle"],
        tickfont={"color": palette["label_muted"], "family": TYPOGRAPHY_THEME["font_family"], "size": 12},
        title_font={"color": palette["label_muted"], "family": TYPOGRAPHY_THEME["font_family"], "size": 12},
        automargin=True,
    )
    return figure
