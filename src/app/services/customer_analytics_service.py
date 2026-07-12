"""Customer analytics: RFM, CLV, repeat rate, cohort."""

from __future__ import annotations

from datetime import date

import pandas as pd
from sqlalchemy.orm import Session

from app.analytics.cohort import build_cohort_matrix, cohort_pivot
from app.analytics.rfm import compute_rfm_raw, score_rfm, segment_summary
from app.repositories.analytics import AnalyticsRepository
from app.schemas.filters import AnalyticsFilter


class CustomerAnalyticsService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = AnalyticsRepository(session)

    def rfm(
        self,
        filters: AnalyticsFilter | None = None,
        *,
        as_of: date | None = None,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Return (scored customer RFM, segment summary)."""
        lines = self.repo.fetch_order_lines(filters)
        raw = compute_rfm_raw(lines, as_of=as_of)
        scored = score_rfm(raw)
        summary = segment_summary(scored)
        return scored, summary

    def clv(self, filters: AnalyticsFilter | None = None, *, top_n: int = 50) -> pd.DataFrame:
        """Simple historical CLV = lifetime revenue per customer in filter."""
        lines = self.repo.fetch_order_lines(filters)
        if lines.empty:
            return pd.DataFrame(
                columns=[
                    "customer_id",
                    "customer_code",
                    "order_count",
                    "lifetime_revenue",
                    "first_order_at",
                    "last_order_at",
                ]
            )
        g = (
            lines.groupby(["customer_id", "customer_code"], as_index=False)
            .agg(
                order_count=("order_id", "nunique"),
                lifetime_revenue=("line_total", "sum"),
                first_order_at=("order_date", "min"),
                last_order_at=("order_date", "max"),
            )
            .sort_values("lifetime_revenue", ascending=False)
            .head(top_n)
        )
        return g.reset_index(drop=True)

    def repeat_rate(self, filters: AnalyticsFilter | None = None) -> dict[str, float | int]:
        headers = self.repo.fetch_orders_header(filters)
        if headers.empty:
            return {
                "total_buyers": 0,
                "repeat_buyers": 0,
                "repeat_customer_rate_pct": 0.0,
            }
        counts = headers.groupby("customer_id").size()
        total = int(counts.shape[0])
        repeat = int((counts >= 2).sum())
        pct = round(100.0 * repeat / total, 2) if total else 0.0
        return {
            "total_buyers": total,
            "repeat_buyers": repeat,
            "repeat_customer_rate_pct": pct,
        }

    def cohort(self, filters: AnalyticsFilter | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Return (long matrix, pivot retention)."""
        headers = self.repo.fetch_orders_header(filters)
        # need customer_id + order_date only
        if headers.empty:
            empty = pd.DataFrame()
            return empty, empty
        matrix = build_cohort_matrix(
            headers.rename(columns={"order_id": "order_id"}),
            customer_col="customer_id",
            date_col="order_date",
        )
        return matrix, cohort_pivot(matrix)
