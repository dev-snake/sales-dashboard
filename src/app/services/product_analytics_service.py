"""Product analytics: ABC, Pareto, top products, margin."""

from __future__ import annotations

import pandas as pd
from sqlalchemy.orm import Session

from app.analytics.abc import abc_classify, pareto_products_for_share
from app.repositories.analytics import AnalyticsRepository
from app.schemas.filters import AnalyticsFilter


class ProductAnalyticsService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = AnalyticsRepository(session)

    def product_revenue(self, filters: AnalyticsFilter | None = None) -> pd.DataFrame:
        lines = self.repo.fetch_order_lines(filters)
        if lines.empty:
            return pd.DataFrame(
                columns=["product_id", "sku", "product_name", "revenue", "cogs", "units", "profit"]
            )
        tmp = lines.copy()
        tmp["cogs_line"] = pd.to_numeric(tmp["quantity"], errors="coerce").fillna(
            0
        ) * pd.to_numeric(tmp["unit_cost"], errors="coerce").fillna(0)
        g = tmp.groupby(["product_id", "sku", "product_name"], as_index=False).agg(
            revenue=("line_total", "sum"),
            units=("quantity", "sum"),
            cogs=("cogs_line", "sum"),
        )
        g["profit"] = g["revenue"] - g["cogs"]
        return g.sort_values("revenue", ascending=False).reset_index(drop=True)

    def abc(self, filters: AnalyticsFilter | None = None) -> pd.DataFrame:
        rev = self.product_revenue(filters)
        if rev.empty:
            return abc_classify(pd.DataFrame(columns=["product_id", "revenue"]))
        base = rev.rename(columns={"product_id": "product_id"})[["product_id", "sku", "revenue"]]
        classified = abc_classify(base, id_col="product_id", value_col="revenue")
        return classified.merge(
            rev[["product_id", "sku", "product_name", "units", "profit"]],
            on="product_id",
            how="left",
        )

    def pareto(self, filters: AnalyticsFilter | None = None) -> dict[str, float | int]:
        abc_df = self.abc(filters)
        return pareto_products_for_share(abc_df)

    def top_products(
        self,
        filters: AnalyticsFilter | None = None,
        *,
        by: str = "revenue",
        top_n: int = 20,
    ) -> pd.DataFrame:
        rev = self.product_revenue(filters)
        if rev.empty:
            return rev
        col = "profit" if by == "profit" else "revenue"
        return rev.sort_values(col, ascending=False).head(top_n).reset_index(drop=True)
