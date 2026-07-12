"""Descriptive helpers on numeric series / DataFrames."""

from __future__ import annotations

from decimal import Decimal

import pandas as pd


def safe_div(numerator: Decimal | float | int, denominator: Decimal | float | int) -> Decimal:
    """Divide with zero guard; returns Decimal."""
    n = Decimal(str(numerator))
    d = Decimal(str(denominator))
    if d == 0:
        return Decimal("0")
    return n / d


def margin_pct(revenue: Decimal | float, cogs: Decimal | float) -> Decimal:
    rev = Decimal(str(revenue))
    cost = Decimal(str(cogs))
    profit = rev - cost
    if rev == 0:
        return Decimal("0")
    return (profit / rev * Decimal("100")).quantize(Decimal("0.01"))


def describe_numeric(series: pd.Series) -> dict[str, float]:
    """Basic descriptive stats for a numeric series."""
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return {
            "count": 0.0,
            "mean": 0.0,
            "std": 0.0,
            "min": 0.0,
            "p25": 0.0,
            "p50": 0.0,
            "p75": 0.0,
            "max": 0.0,
        }
    return {
        "count": float(s.count()),
        "mean": float(s.mean()),
        "std": float(s.std(ddof=0) if len(s) else 0.0),
        "min": float(s.min()),
        "p25": float(s.quantile(0.25)),
        "p50": float(s.quantile(0.50)),
        "p75": float(s.quantile(0.75)),
        "max": float(s.max()),
    }
