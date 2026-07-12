"""Thin Streamlit wrappers around Plotly factories."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.visualization.plotly_charts import (
    create_area_chart,
    create_bar_chart,
    create_heatmap,
    create_histogram,
    create_line_chart,
    create_pie_chart,
    create_scatter_chart,
    create_treemap,
)


def show_plotly(fig: object, *, key: str | None = None) -> None:
    st.plotly_chart(fig, use_container_width=True, key=key)


def plot_line(df: pd.DataFrame, x: str, y: str, *, title: str, key: str) -> None:
    if df.empty:
        st.info("Không có dữ liệu cho biểu đồ này.")
        return
    show_plotly(create_line_chart(df, x, y, title=title), key=key)


def plot_area(
    df: pd.DataFrame, x: str, y: str, *, title: str, key: str, color: str | None = None
) -> None:
    if df.empty:
        st.info("Không có dữ liệu cho biểu đồ này.")
        return
    show_plotly(create_area_chart(df, x, y, color=color, title=title), key=key)


def plot_bar(
    df: pd.DataFrame,
    x: str,
    y: str,
    *,
    title: str,
    key: str,
    orientation: str = "v",
) -> None:
    if df.empty:
        st.info("Không có dữ liệu cho biểu đồ này.")
        return
    show_plotly(
        create_bar_chart(df, x, y, orientation=orientation, title=title),  # type: ignore[arg-type]
        key=key,
    )


def plot_pie(df: pd.DataFrame, names: str, values: str, *, title: str, key: str) -> None:
    if df.empty:
        st.info("Không có dữ liệu cho biểu đồ này.")
        return
    show_plotly(create_pie_chart(df, names, values, title=title), key=key)


def plot_scatter(
    df: pd.DataFrame,
    x: str,
    y: str,
    *,
    title: str,
    key: str,
    hover_name: str | None = None,
    size: str | None = None,
) -> None:
    if df.empty:
        st.info("Không có dữ liệu cho biểu đồ này.")
        return
    show_plotly(
        create_scatter_chart(df, x, y, hover_name=hover_name, size=size, title=title),
        key=key,
    )


def plot_hist(df: pd.DataFrame, x: str, *, title: str, key: str) -> None:
    if df.empty:
        st.info("Không có dữ liệu cho biểu đồ này.")
        return
    show_plotly(create_histogram(df, x, title=title), key=key)


def plot_heatmap(data: pd.DataFrame, *, title: str, key: str) -> None:
    if data.empty:
        st.info("Không có dữ liệu cho biểu đồ này.")
        return
    show_plotly(create_heatmap(data, title=title), key=key)


def plot_treemap(
    df: pd.DataFrame,
    path: list[str],
    values: str,
    *,
    title: str,
    key: str,
) -> None:
    if df.empty:
        st.info("Không có dữ liệu cho biểu đồ này.")
        return
    show_plotly(create_treemap(df, path=path, values=values, title=title), key=key)
