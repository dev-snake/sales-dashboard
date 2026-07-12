"""Canonical KPI / metrics computation — single source of truth."""

from __future__ import annotations

from decimal import Decimal

import pandas as pd
from sqlalchemy.orm import Session

from app.analytics.descriptive import margin_pct, safe_div
from app.repositories.analytics import AnalyticsRepository
from app.schemas.filters import AnalyticsFilter, KPIResult


class MetricsService:
    """Compute revenue, profit, AOV and related KPIs."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = AnalyticsRepository(session)

    def summary(self, filters: AnalyticsFilter | None = None) -> KPIResult:
        """KPI bundle for a filter window."""
        f = filters or AnalyticsFilter.last_n_days(30)
        lines = self.repo.fetch_order_lines(f)
        refunds = Decimal(str(self.repo.fetch_refunds_total(f)))
        return self.summary_from_lines(lines, refunds=refunds)

    @staticmethod
    def summary_from_lines(
        lines: pd.DataFrame,
        *,
        refunds: Decimal = Decimal("0"),
    ) -> KPIResult:
        """Pure KPI calc from order-line frame (unit-testable without DB)."""
        if lines.empty:
            return KPIResult(refunds=refunds, net_revenue=Decimal("0") - refunds)

        revenue = Decimal(str(pd.to_numeric(lines["line_total"], errors="coerce").fillna(0).sum()))
        cogs = Decimal(
            str(
                (
                    pd.to_numeric(lines["quantity"], errors="coerce").fillna(0)
                    * pd.to_numeric(lines["unit_cost"], errors="coerce").fillna(0)
                ).sum()
            )
        )
        units = int(pd.to_numeric(lines["quantity"], errors="coerce").fillna(0).sum())
        order_count = int(lines["order_id"].nunique()) if "order_id" in lines.columns else 0
        buyer_count = int(lines["customer_id"].nunique()) if "customer_id" in lines.columns else 0
        profit = revenue - cogs
        aov = safe_div(revenue, order_count)
        net = revenue - refunds
        return KPIResult(
            revenue=revenue.quantize(Decimal("0.01")),
            cogs=cogs.quantize(Decimal("0.01")),
            gross_profit=profit.quantize(Decimal("0.01")),
            gross_margin_pct=margin_pct(revenue, cogs),
            order_count=order_count,
            buyer_count=buyer_count,
            units_sold=units,
            aov=aov.quantize(Decimal("0.01")),
            net_revenue=net.quantize(Decimal("0.01")),
            refunds=refunds.quantize(Decimal("0.01")),
        )

    def revenue_by_dimension(
        self,
        dim: str,
        filters: AnalyticsFilter | None = None,
        *,
        top_n: int | None = None,
    ) -> pd.DataFrame:
        """Aggregate revenue by store_code | category_name | product_name | customer_code."""
        col_map = {
            "store": "store_code",
            "category": "category_name",
            "product": "product_name",
            "customer": "customer_code",
            "sku": "sku",
        }
        if dim not in col_map:
            raise ValueError(f"Unknown dimension {dim!r}; choose {sorted(col_map)}")
        col = col_map[dim]
        lines = self.repo.fetch_order_lines(filters)
        if lines.empty:
            return pd.DataFrame(columns=[col, "revenue", "units", "orders"])
        g = (
            lines.groupby(col, dropna=False, as_index=False)
            .agg(
                revenue=("line_total", "sum"),
                units=("quantity", "sum"),
                orders=("order_id", "nunique"),
            )
            .sort_values("revenue", ascending=False)
        )
        if top_n is not None:
            g = g.head(top_n)
        return g.reset_index(drop=True)
