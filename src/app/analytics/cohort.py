"""Cohort retention matrix (first-order month × period)."""

from __future__ import annotations

import pandas as pd


def build_cohort_matrix(
    orders_df: pd.DataFrame,
    *,
    customer_col: str = "customer_id",
    date_col: str = "order_date",
) -> pd.DataFrame:
    """
    Return long-form cohort table:

    cohort_month | period_number | active_customers | cohort_size | retention_rate
    """
    if orders_df.empty:
        return pd.DataFrame(
            columns=[
                "cohort_month",
                "period_number",
                "active_customers",
                "cohort_size",
                "retention_rate",
            ]
        )

    df = orders_df[[customer_col, date_col]].copy()
    ts = pd.to_datetime(df[date_col], utc=True)
    df["activity_month"] = pd.to_datetime(
        {"year": ts.dt.year, "month": ts.dt.month, "day": 1},
        utc=True,
    )

    first = df.groupby(customer_col, as_index=False).agg(cohort_month=("activity_month", "min"))
    merged = df.merge(first, on=customer_col, how="inner")
    merged["period_number"] = (
        (merged["activity_month"].dt.year - merged["cohort_month"].dt.year) * 12
        + (merged["activity_month"].dt.month - merged["cohort_month"].dt.month)
    ).astype(int)

    active = merged.groupby(["cohort_month", "period_number"], as_index=False).agg(
        active_customers=(customer_col, "nunique")
    )
    sizes = first.groupby("cohort_month", as_index=False).agg(cohort_size=(customer_col, "nunique"))
    out = active.merge(sizes, on="cohort_month", how="left")
    out["retention_rate"] = out["active_customers"] / out["cohort_size"].replace(0, pd.NA)
    result: pd.DataFrame = out.sort_values(["cohort_month", "period_number"]).reset_index(drop=True)
    return result


def cohort_pivot(matrix: pd.DataFrame) -> pd.DataFrame:
    """Wide retention matrix: rows=cohort_month, cols=period_number."""
    if matrix.empty:
        return pd.DataFrame()
    pivot: pd.DataFrame = matrix.pivot_table(
        index="cohort_month",
        columns="period_number",
        values="retention_rate",
        aggfunc="first",
    )
    return pivot
