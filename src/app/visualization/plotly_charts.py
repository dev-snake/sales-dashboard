"""Plotly interactive chart factories (DataFrame in → go.Figure out).

No database access — call sites pass tidy frames.
"""

from __future__ import annotations

from typing import Literal

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app.visualization.styles import (
    CATEGORICAL,
    PLOTLY_TEMPLATE,
    PRIMARY,
    SECONDARY,
    color_cycle,
    top_n_with_other,
)


def _base_layout(fig: go.Figure, title: str | None) -> go.Figure:
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title=title or "",
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        colorway=CATEGORICAL,
    )
    return fig


def create_line_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    *,
    color: str | None = None,
    title: str | None = None,
    markers: bool = False,
) -> go.Figure:
    """Line chart for trends over time."""
    if df.empty:
        return _empty_figure(title or "Line chart")
    fig = px.line(
        df,
        x=x,
        y=y,
        color=color,
        markers=markers,
        title=title,
        color_discrete_sequence=CATEGORICAL,
    )
    fig.update_traces(line=dict(width=2))
    return _base_layout(fig, title)


def create_area_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    *,
    color: str | None = None,
    title: str | None = None,
    stacked: bool = True,
) -> go.Figure:
    if df.empty:
        return _empty_figure(title or "Area chart")
    fig = px.area(
        df,
        x=x,
        y=y,
        color=color,
        title=title,
        color_discrete_sequence=CATEGORICAL,
    )
    if not stacked:
        fig.update_traces(stackgroup=None, fill="tozeroy")
    return _base_layout(fig, title)


def create_bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    *,
    orientation: Literal["v", "h"] = "v",
    color: str | None = None,
    title: str | None = None,
    text: str | None = None,
) -> go.Figure:
    if df.empty:
        return _empty_figure(title or "Bar chart")
    fig = px.bar(
        df,
        x=x if orientation == "v" else y,
        y=y if orientation == "v" else x,
        color=color,
        orientation=orientation,
        title=title,
        text=text,
        color_discrete_sequence=CATEGORICAL,
    )
    fig.update_traces(marker_line_width=0)
    return _base_layout(fig, title)


def create_pie_chart(
    df: pd.DataFrame,
    names: str,
    values: str,
    *,
    title: str | None = None,
    max_slices: int = 8,
) -> go.Figure:
    if df.empty:
        return _empty_figure(title or "Pie chart")
    labs, vals = top_n_with_other(
        df[names].astype(str).tolist(),
        pd.to_numeric(df[values], errors="coerce").fillna(0).tolist(),
        n=max_slices,
    )
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labs,
                values=vals,
                hole=0.35,
                textinfo="percent+label",
                marker=dict(colors=color_cycle(len(labs))),
            )
        ]
    )
    return _base_layout(fig, title)


def create_scatter_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    *,
    size: str | None = None,
    color: str | None = None,
    hover_name: str | None = None,
    title: str | None = None,
) -> go.Figure:
    if df.empty:
        return _empty_figure(title or "Scatter chart")
    fig = px.scatter(
        df,
        x=x,
        y=y,
        size=size,
        color=color,
        hover_name=hover_name,
        title=title,
        color_discrete_sequence=CATEGORICAL,
    )
    fig.update_traces(marker=dict(line=dict(width=0.5, color="white")))
    return _base_layout(fig, title)


def create_histogram(
    df: pd.DataFrame,
    x: str,
    *,
    nbins: int = 25,
    title: str | None = None,
    color: str | None = None,
) -> go.Figure:
    if df.empty:
        return _empty_figure(title or "Histogram")
    fig = px.histogram(
        df,
        x=x,
        nbins=nbins,
        color=color,
        title=title,
        color_discrete_sequence=CATEGORICAL,
    )
    fig.update_traces(marker_color=PRIMARY if color is None else None)
    return _base_layout(fig, title)


def create_heatmap(
    data: pd.DataFrame,
    *,
    x: str | None = None,
    y: str | None = None,
    z: str | None = None,
    title: str | None = None,
    colorscale: str = "Blues",
) -> go.Figure:
    """
    Heatmap from:
    - wide matrix (index/columns numeric or labels), or
    - long DataFrame with x, y, z columns.
    """
    if data.empty:
        return _empty_figure(title or "Heatmap")

    if x and y and z and x in data.columns and y in data.columns and z in data.columns:
        pivot = data.pivot_table(index=y, columns=x, values=z, aggfunc="mean")
    else:
        pivot = data

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=[str(c) for c in pivot.columns],
            y=[str(i) for i in pivot.index],
            colorscale=colorscale,
            colorbar=dict(title=z or "value"),
        )
    )
    return _base_layout(fig, title)


def create_treemap(
    df: pd.DataFrame,
    path: list[str],
    values: str,
    *,
    color: str | None = None,
    title: str | None = None,
) -> go.Figure:
    if df.empty:
        return _empty_figure(title or "Treemap")
    fig = px.treemap(
        df,
        path=path,
        values=values,
        color=color or values,
        title=title,
        color_continuous_scale="Tealgrn",
    )
    fig.update_traces(root_color="lightgrey")
    return _base_layout(fig, title)


def _empty_figure(title: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text="No data",
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=14, color="#64748B"),
    )
    fig.update_layout(
        title=title, template=PLOTLY_TEMPLATE, xaxis=dict(visible=False), yaxis=dict(visible=False)
    )
    return fig


# Convenience dual-series line (actual vs comparison)
def create_dual_line_chart(
    df: pd.DataFrame,
    x: str,
    y_a: str,
    y_b: str,
    *,
    name_a: str = "Current",
    name_b: str = "Previous",
    title: str | None = None,
) -> go.Figure:
    if df.empty:
        return _empty_figure(title or "Comparison")
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=df[x], y=df[y_a], mode="lines", name=name_a, line=dict(color=PRIMARY, width=2))
    )
    fig.add_trace(
        go.Scatter(
            x=df[x],
            y=df[y_b],
            mode="lines",
            name=name_b,
            line=dict(color=SECONDARY, width=2, dash="dash"),
        )
    )
    return _base_layout(fig, title)
