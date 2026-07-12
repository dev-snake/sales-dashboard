"""Shared design tokens and formatters for charts."""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal

# Brand palette (docs/data-visualization.md)
PRIMARY = "#2563EB"
SECONDARY = "#0D9488"
SUCCESS = "#16A34A"
WARNING = "#D97706"
DANGER = "#DC2626"
NEUTRAL = "#64748B"

# Colorblind-friendly categorical (≈10)
CATEGORICAL: list[str] = [
    "#2563EB",
    "#0D9488",
    "#D97706",
    "#7C3AED",
    "#DC2626",
    "#0891B2",
    "#CA8A04",
    "#DB2777",
    "#4B5563",
    "#65A30D",
]

PLOTLY_TEMPLATE = "plotly_white"
MPL_STYLE: dict[str, bool | float | int | str] = {
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "font.size": 10,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
}


def color_cycle(n: int) -> list[str]:
    """Repeat categorical palette to length n."""
    if n <= 0:
        return []
    return [CATEGORICAL[i % len(CATEGORICAL)] for i in range(n)]


def format_money(value: float | int | Decimal | None, *, currency: str = "VND") -> str:
    """Format money for labels (compact for large VND)."""
    if value is None:
        return "—"
    v = float(value)
    if abs(v) >= 1_000_000_000:
        return f"{v / 1_000_000_000:.2f}B {currency}"
    if abs(v) >= 1_000_000:
        return f"{v / 1_000_000:.2f}M {currency}"
    if abs(v) >= 1_000:
        return f"{v / 1_000:.1f}K {currency}"
    return f"{v:,.0f} {currency}"


def format_percent(value: float | int | Decimal | None, *, digits: int = 1) -> str:
    if value is None:
        return "—"
    return f"{float(value):.{digits}f}%"


def format_number(value: float | int | Decimal | None, *, digits: int = 0) -> str:
    if value is None:
        return "—"
    if digits == 0:
        return f"{float(value):,.0f}"
    return f"{float(value):,.{digits}f}"


def top_n_with_other(
    labels: Sequence[str],
    values: Sequence[float],
    *,
    n: int = 8,
    other_label: str = "Other",
) -> tuple[list[str], list[float]]:
    """Keep top-n by value; bucket remainder as Other (for pie/treemap)."""
    pairs = sorted(zip(labels, values, strict=True), key=lambda x: x[1], reverse=True)
    if len(pairs) <= n:
        return [p[0] for p in pairs], [float(p[1]) for p in pairs]
    head = pairs[:n]
    tail = pairs[n:]
    other_sum = float(sum(v for _, v in tail))
    labs = [p[0] for p in head] + [other_label]
    vals = [float(p[1]) for p in head] + [other_sum]
    return labs, vals
