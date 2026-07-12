"""Collect ReportDataPackage from MetricsService + analytics services."""

from __future__ import annotations

import pandas as pd
from sqlalchemy.orm import Session

from app.analytics.trends import monthly_aggregate
from app.reports.package import ReportDataPackage
from app.reports.periods import PeriodWindow
from app.repositories.analytics import AnalyticsRepository
from app.schemas.filters import AnalyticsFilter
from app.services.customer_analytics_service import CustomerAnalyticsService
from app.services.inventory_service import InventoryService
from app.services.metrics_service import MetricsService
from app.services.product_analytics_service import ProductAnalyticsService


def _daily_revenue_series(lines: pd.DataFrame) -> pd.DataFrame:
    if lines.empty:
        return pd.DataFrame(columns=["day", "revenue"])
    df = lines.copy()
    df["day"] = pd.to_datetime(df["order_date"], utc=True).dt.date
    return df.groupby("day", as_index=False).agg(revenue=("line_total", "sum")).sort_values("day")


def _filter_for(period: PeriodWindow, store_ids: list[int] | None = None) -> AnalyticsFilter:
    return AnalyticsFilter(
        start_date=period.start,
        end_date=period.end,
        store_ids=list(store_ids or []),
        order_statuses=["paid", "completed"],
    )


def collect_report(
    session: Session,
    period: PeriodWindow,
    *,
    store_ids: list[int] | None = None,
) -> ReportDataPackage:
    """Build full report package for the given period."""
    f = _filter_for(period, store_ids)
    f_prev = _filter_for(period.previous, store_ids)

    metrics = MetricsService(session)
    products = ProductAnalyticsService(session)
    customers = CustomerAnalyticsService(session)
    inventory = InventoryService(session)
    repo = AnalyticsRepository(session)

    lines = repo.fetch_order_lines(f)
    kpi = metrics.summary(f)
    kpi_prev = metrics.summary(f_prev)

    # Trend grain by report type
    if period.report_type in ("daily", "weekly"):
        trend = _daily_revenue_series(lines)
        if not trend.empty:
            trend = trend.rename(columns={"day": "period_key"})
    else:
        trend = monthly_aggregate(lines)
        if not trend.empty:
            trend = trend.rename(columns={"month_key": "period_key"})

    top_products = products.top_products(f, by="revenue", top_n=20)
    top_stores = metrics.revenue_by_dimension("store", f, top_n=20)
    top_customers = customers.clv(f, top_n=20)
    by_category = metrics.revenue_by_dimension("category", f)

    # employees from lines
    if not lines.empty and "employee_id" in lines.columns:
        top_employees = (
            lines.groupby("employee_id", as_index=False)
            .agg(revenue=("line_total", "sum"), orders=("order_id", "nunique"))
            .sort_values("revenue", ascending=False)
            .head(20)
        )
    else:
        top_employees = pd.DataFrame()

    # region: need region via store — use store dimension if no region name
    by_region = pd.DataFrame()
    if not lines.empty and "region_id" in lines.columns:
        by_region = (
            lines.groupby("region_id", as_index=False)
            .agg(revenue=("line_total", "sum"), orders=("order_id", "nunique"))
            .sort_values("revenue", ascending=False)
        )

    _, rfm_summary = customers.rfm(f)
    abc = products.abc(f)
    repeat = customers.repeat_rate(f)
    low_stock = inventory.low_stock()

    # depth extras for monthly+
    extras: dict = {}
    if period.report_type in ("monthly", "quarterly", "yearly"):
        matrix, pivot = customers.cohort(f)
        extras["cohort_matrix"] = matrix
        extras["cohort_pivot"] = pivot
        extras["pareto"] = products.pareto(f)

    return ReportDataPackage(
        report_type=period.report_type,
        period=period,
        kpi=kpi,
        kpi_previous=kpi_prev,
        trend=trend,
        top_products=top_products,
        top_stores=top_stores,
        top_customers=top_customers,
        top_employees=top_employees,
        by_category=by_category,
        by_region=by_region,
        rfm_summary=rfm_summary,
        abc=abc,
        repeat_rate=repeat,
        low_stock=low_stock,
        extras=extras,
    )
