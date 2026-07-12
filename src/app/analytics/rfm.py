"""RFM scoring and simple segment labels (pure pandas)."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd


def compute_rfm_raw(
    orders_df: pd.DataFrame,
    *,
    as_of: date | None = None,
    customer_col: str = "customer_id",
    date_col: str = "order_date",
    order_col: str = "order_id",
    amount_col: str = "line_total",
) -> pd.DataFrame:
    """
    Build recency (days), frequency, monetary per customer.

    ``orders_df`` should already be filtered to paid/completed lines or headers
    with positive amounts. Prefer line-level with order_id for frequency.
    """
    if orders_df.empty:
        return pd.DataFrame(
            columns=[customer_col, "last_order_date", "recency_days", "frequency", "monetary"]
        )

    df = orders_df.copy()
    df[date_col] = pd.to_datetime(df[date_col], utc=True)
    ref = pd.Timestamp(as_of or date.today(), tz="UTC")

    grouped = df.groupby(customer_col, as_index=False).agg(
        last_order_date=(date_col, "max"),
        frequency=(order_col, "nunique"),
        monetary=(amount_col, "sum"),
    )
    grouped["recency_days"] = (ref - grouped["last_order_date"]).dt.days.clip(lower=0)
    return grouped


def score_rfm(
    raw: pd.DataFrame,
    *,
    n_tiles: int = 5,
) -> pd.DataFrame:
    """
    Assign 1..n_tiles scores.

    - R: lower recency_days → higher score
    - F/M: higher → higher score
    """
    if raw.empty:
        return raw.copy()

    out = raw.copy()
    # NTILE-like via qcut; handle ties / constant series
    out["r_score"] = _ntile_score(out["recency_days"], n_tiles, ascending=False)
    out["f_score"] = _ntile_score(out["frequency"], n_tiles, ascending=True)
    out["m_score"] = _ntile_score(out["monetary"], n_tiles, ascending=True)
    out["rfm_score"] = (
        out["r_score"].astype(str) + out["f_score"].astype(str) + out["m_score"].astype(str)
    )
    out["segment"] = out.apply(_segment_label, axis=1)
    return out


def _ntile_score(series: pd.Series, n: int, *, ascending: bool) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    if s.nunique(dropna=True) <= 1:
        return pd.Series(np.full(len(s), (n + 1) // 2, dtype=int), index=s.index)
    # rank then cut into n buckets
    ranks = s.rank(method="first", ascending=ascending)
    try:
        return pd.qcut(ranks, q=n, labels=False, duplicates="drop") + 1
    except ValueError:
        # fallback fewer bins
        return pd.Series(np.full(len(s), (n + 1) // 2, dtype=int), index=s.index)


def _segment_label(row: pd.Series) -> str:
    r, f, m = int(row["r_score"]), int(row["f_score"]), int(row["m_score"])
    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    if r >= 3 and f >= 3 and m >= 3:
        return "Loyal"
    if r >= 4 and f <= 2:
        return "New / Promising"
    if r <= 2 and f >= 3:
        return "At Risk"
    if r <= 2 and f <= 2 and m <= 2:
        return "Hibernating"
    return "Need Attention"


def segment_summary(scored: pd.DataFrame) -> pd.DataFrame:
    """Counts and monetary by segment."""
    if scored.empty or "segment" not in scored.columns:
        return pd.DataFrame(columns=["segment", "customers", "monetary", "avg_frequency"])
    return (
        scored.groupby("segment", as_index=False)
        .agg(
            customers=("segment", "size"),
            monetary=("monetary", "sum"),
            avg_frequency=("frequency", "mean"),
        )
        .sort_values("monetary", ascending=False)
    )
