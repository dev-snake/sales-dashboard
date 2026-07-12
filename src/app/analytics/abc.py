"""ABC / Pareto classification for products."""

from __future__ import annotations

import pandas as pd


def abc_classify(
    df: pd.DataFrame,
    *,
    id_col: str = "product_id",
    value_col: str = "revenue",
    a_threshold: float = 0.80,
    b_threshold: float = 0.95,
) -> pd.DataFrame:
    """
    Classify SKUs into A/B/C by cumulative revenue share.

    Input: one row per product with revenue (or other value).
    Output: sorted by value desc with cum_pct and abc_class.
    """
    if df.empty:
        return pd.DataFrame(
            columns=[id_col, value_col, "cum_value", "cum_pct", "pct_of_total", "abc_class"]
        )

    out = df[[id_col, value_col]].copy()
    out[value_col] = pd.to_numeric(out[value_col], errors="coerce").fillna(0.0)
    out = out.sort_values(value_col, ascending=False).reset_index(drop=True)
    total = float(out[value_col].sum())
    out["cum_value"] = out[value_col].cumsum()
    out["pct_of_total"] = out[value_col] / total if total else 0.0
    out["cum_pct"] = out["cum_value"] / total if total else 0.0

    def _cls(cum: float) -> str:
        if cum <= a_threshold:
            return "A"
        if cum <= b_threshold:
            return "B"
        return "C"

    out["abc_class"] = out["cum_pct"].map(_cls)
    return out


def pareto_products_for_share(
    abc_df: pd.DataFrame,
    *,
    share: float = 0.80,
) -> dict[str, float | int]:
    """How many products contribute to ``share`` of total value."""
    if abc_df.empty:
        return {
            "products_for_share": 0,
            "total_products": 0,
            "pct_products": 0.0,
            "share": share,
        }
    hit = abc_df[abc_df["cum_pct"] >= share]
    n = int(hit.index[0]) + 1 if not hit.empty else int(len(abc_df))
    total = int(len(abc_df))
    return {
        "products_for_share": n,
        "total_products": total,
        "pct_products": round(100.0 * n / total, 2) if total else 0.0,
        "share": share,
    }
