"""Smoke tests for visualization factories (no DB)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from matplotlib.figure import Figure

from app.visualization import (
    create_area_chart,
    create_bar_chart,
    create_heatmap,
    create_histogram,
    create_line_chart,
    create_pie_chart,
    create_scatter_chart,
    create_treemap,
    fig_to_png_bytes,
    format_money,
    format_percent,
    mpl_barh,
    mpl_line,
    mpl_pie,
    save_fig,
)
from app.visualization.styles import top_n_with_other


def _trend_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "month": pd.date_range("2024-01-01", periods=6, freq="MS"),
            "revenue": [100, 120, 90, 140, 160, 150],
            "segment": ["A", "A", "B", "B", "A", "B"],
        }
    )


def _rank_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "store": [f"S{i}" for i in range(5)],
            "revenue": [50, 80, 30, 90, 40],
        }
    )


def test_formatters() -> None:
    assert "M" in format_money(2_500_000)
    assert format_percent(12.34) == "12.3%"


def test_top_n_with_other() -> None:
    labs, vals = top_n_with_other(["a", "b", "c", "d"], [10, 5, 3, 1], n=2)
    assert labs[-1] == "Other"
    assert vals[-1] == 4.0


def test_plotly_all_eight_types() -> None:
    trend = _trend_df()
    rank = _rank_df()
    pie = pd.DataFrame({"name": ["cash", "card", "transfer"], "amount": [40, 35, 25]})
    scatter = pd.DataFrame(
        {"orders": [10, 20, 15], "revenue": [100, 250, 180], "store": ["A", "B", "C"]}
    )
    heat = pd.DataFrame([[1, 2], [3, 4]], index=["Mon", "Tue"], columns=["W1", "W2"])
    tree = pd.DataFrame(
        {
            "category": ["Electronics", "Electronics", "Fashion"],
            "product": ["Phone", "Laptop", "Shirt"],
            "revenue": [100, 80, 40],
        }
    )

    figs: list[go.Figure] = [
        create_line_chart(trend, "month", "revenue", title="Revenue"),
        create_area_chart(trend, "month", "revenue", title="Area"),
        create_bar_chart(rank, "store", "revenue", title="Stores"),
        create_bar_chart(rank, "store", "revenue", orientation="h", title="Stores H"),
        create_pie_chart(pie, "name", "amount", title="Payments"),
        create_scatter_chart(scatter, "orders", "revenue", hover_name="store", title="Scatter"),
        create_histogram(scatter, "revenue", title="Hist"),
        create_heatmap(heat, title="Heat"),
        create_treemap(tree, path=["category", "product"], values="revenue", title="Tree"),
    ]
    for fig in figs:
        assert isinstance(fig, go.Figure)
        # plotly serializable
        assert fig.to_plotly_json()


def test_plotly_empty_no_crash() -> None:
    empty = pd.DataFrame(columns=["x", "y"])
    fig = create_line_chart(empty, "x", "y", title="Empty")
    assert isinstance(fig, go.Figure)


def test_matplotlib_and_png(tmp_path: Path) -> None:
    trend = _trend_df()
    rank = _rank_df()
    pie = pd.DataFrame({"name": ["A", "B"], "amount": [60, 40]})

    fig1 = mpl_line(trend, "month", "revenue", title="Trend")
    fig2 = mpl_barh(rank, "store", "revenue", title="Rank")
    fig3 = mpl_pie(pie, "name", "amount", title="Mix")

    for fig in (fig1, fig2, fig3):
        assert isinstance(fig, Figure)
        png = fig_to_png_bytes(fig)
        assert isinstance(png, bytes)
        assert png[:8] == b"\x89PNG\r\n\x1a\n"

    # reopen line for save_fig (previous closed)
    fig4 = mpl_line(trend, "month", "revenue")
    out = save_fig(fig4, tmp_path / "trend.png", dpi=100)
    assert Path(out).is_file()
    assert Path(out).stat().st_size > 0
