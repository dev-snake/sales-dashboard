"""Matplotlib static charts for PDF / export (no DB access)."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Literal

import matplotlib

matplotlib.use("Agg")  # headless-safe
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from app.visualization.styles import (
    MPL_STYLE,
    PRIMARY,
    SECONDARY,
    color_cycle,
    top_n_with_other,
)


def _apply_style() -> None:
    # rcParams keys are typed as Literal[...] — cast for our static style dict
    for key, value in MPL_STYLE.items():
        plt.rcParams[key] = value  # type: ignore[index]


def mpl_line(
    df: pd.DataFrame,
    x: str,
    y: str,
    *,
    title: str | None = None,
    ylabel: str | None = None,
    figsize: tuple[float, float] = (8, 4),
) -> Figure:
    _apply_style()
    fig, ax = plt.subplots(figsize=figsize)
    if df.empty:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
    else:
        ax.plot(df[x], df[y], color=PRIMARY, linewidth=2)
        ax.fill_between(df[x], df[y], alpha=0.12, color=PRIMARY)
    ax.set_title(title or "")
    ax.set_xlabel(x)
    ax.set_ylabel(ylabel or y)
    fig.autofmt_xdate()
    fig.tight_layout()
    return fig


def mpl_barh(
    df: pd.DataFrame,
    y: str,
    x: str,
    *,
    title: str | None = None,
    figsize: tuple[float, float] = (8, 5),
    top_n: int | None = 15,
) -> Figure:
    _apply_style()
    fig, ax = plt.subplots(figsize=figsize)
    if df.empty:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
    else:
        data = df.sort_values(x, ascending=True)
        if top_n is not None:
            data = data.tail(top_n)
        colors = color_cycle(len(data))
        ax.barh(data[y].astype(str), data[x], color=colors)
    ax.set_title(title or "")
    ax.set_xlabel(x)
    fig.tight_layout()
    return fig


def mpl_bar(
    df: pd.DataFrame,
    x: str,
    y: str,
    *,
    title: str | None = None,
    figsize: tuple[float, float] = (8, 4),
) -> Figure:
    _apply_style()
    fig, ax = plt.subplots(figsize=figsize)
    if df.empty:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
    else:
        ax.bar(df[x].astype(str), df[y], color=PRIMARY)
        ax.tick_params(axis="x", rotation=45)
    ax.set_title(title or "")
    ax.set_ylabel(y)
    fig.tight_layout()
    return fig


def mpl_pie(
    df: pd.DataFrame,
    names: str,
    values: str,
    *,
    title: str | None = None,
    max_slices: int = 6,
    figsize: tuple[float, float] = (6, 6),
) -> Figure:
    _apply_style()
    fig, ax = plt.subplots(figsize=figsize)
    if df.empty:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
    else:
        labs, vals = top_n_with_other(
            df[names].astype(str).tolist(),
            pd.to_numeric(df[values], errors="coerce").fillna(0).tolist(),
            n=max_slices,
        )
        ax.pie(
            vals,
            labels=labs,
            autopct="%1.1f%%",
            colors=color_cycle(len(labs)),
            startangle=90,
        )
        ax.axis("equal")
    ax.set_title(title or "")
    fig.tight_layout()
    return fig


def mpl_histogram(
    series: pd.Series | list[float],
    *,
    bins: int = 25,
    title: str | None = None,
    xlabel: str | None = None,
    figsize: tuple[float, float] = (8, 4),
) -> Figure:
    _apply_style()
    fig, ax = plt.subplots(figsize=figsize)
    data = pd.to_numeric(pd.Series(series), errors="coerce").dropna()
    if data.empty:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
    else:
        ax.hist(data, bins=bins, color=SECONDARY, edgecolor="white", alpha=0.9)
    ax.set_title(title or "")
    ax.set_xlabel(xlabel or "value")
    ax.set_ylabel("count")
    fig.tight_layout()
    return fig


def save_fig(
    fig: Figure,
    path: str | Path | None = None,
    *,
    dpi: int = 140,
    format: Literal["png", "svg", "pdf"] = "png",
) -> bytes | Path:
    """Save figure to path or return PNG/SVG bytes if path is None."""
    if path is None:
        buf = BytesIO()
        fig.savefig(buf, format=format, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
        return buf.getvalue()

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format=format, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return out


def fig_to_png_bytes(fig: Figure, *, dpi: int = 140) -> bytes:
    raw = save_fig(fig, path=None, dpi=dpi, format="png")
    assert isinstance(raw, bytes)
    return raw
