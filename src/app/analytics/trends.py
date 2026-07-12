"""Time-series trend helpers (MoM, rolling)."""

from __future__ import annotations

import pandas as pd

from app.analytics.descriptive import safe_div


def add_mom_change(df: pd.DataFrame, *, value_col: str = "revenue") -> pd.DataFrame:
    """Add previous value and MoM % columns. Expects sorted time series."""
    out = df.copy()
    out = out.sort_values(out.columns[0]).reset_index(drop=True)
    out["prev_value"] = out[value_col].shift(1)
    out["mom_change"] = out[value_col] - out["prev_value"]
    prev = pd.to_numeric(out["prev_value"], errors="coerce")
    change = pd.to_numeric(out["mom_change"], errors="coerce")
    mom: list[float | None] = []
    for ch, pr in zip(change.tolist(), prev.tolist(), strict=True):
        if pr is None or pd.isna(pr):
            mom.append(None)
        else:
            mom.append(float(safe_div(ch, pr) * 100))
    out["mom_pct"] = mom
    return out


def rolling_mean(df: pd.DataFrame, *, value_col: str = "revenue", window: int = 7) -> pd.DataFrame:
    """Add rolling mean column."""
    out = df.copy()
    out[f"rolling_mean_{window}"] = (
        pd.to_numeric(out[value_col], errors="coerce").rolling(window=window, min_periods=1).mean()
    )
    return out


def monthly_aggregate(
    line_df: pd.DataFrame,
    *,
    date_col: str = "order_date",
    value_col: str = "line_total",
) -> pd.DataFrame:
    """Aggregate line-level sales to month grain."""
    if line_df.empty:
        return pd.DataFrame(columns=["month_key", "revenue", "order_count", "units"])
    df = line_df.copy()
    ts = pd.to_datetime(df[date_col], utc=True)
    df["month_key"] = pd.to_datetime(
        {"year": ts.dt.year, "month": ts.dt.month, "day": 1},
        utc=True,
    )
    grouped: pd.DataFrame = (
        df.groupby("month_key", as_index=False)
        .agg(
            revenue=(value_col, "sum"),
            order_count=("order_id", "nunique"),
            units=("quantity", "sum"),
        )
        .sort_values("month_key")
    )
    return grouped
