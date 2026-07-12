"""Cached data loaders for Streamlit (session-bound DB access)."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import pandas as pd
import streamlit as st
from sqlalchemy import select

from app.analytics.trends import add_mom_change, monthly_aggregate
from app.database.engine import get_engine
from app.database.session import reset_session_factory, session_scope
from app.models import Category, Employee, Region, Store
from app.repositories.analytics import AnalyticsRepository
from app.schemas.filters import AnalyticsFilter
from app.services.customer_analytics_service import CustomerAnalyticsService
from app.services.inventory_service import InventoryService
from app.services.metrics_service import MetricsService
from app.services.product_analytics_service import ProductAnalyticsService


def filter_cache_key(f: AnalyticsFilter) -> str:
    """Stable string key for @st.cache_data."""
    return "|".join(
        [
            str(f.start_date),
            str(f.end_date),
            ",".join(map(str, sorted(f.store_ids))),
            ",".join(map(str, sorted(f.region_ids))),
            ",".join(map(str, sorted(f.category_ids))),
            ",".join(map(str, sorted(f.employee_ids))),
            str(f.customer_id),
            ",".join(sorted(f.order_statuses)),
        ]
    )


def filter_to_dict(f: AnalyticsFilter) -> dict[str, Any]:
    return {
        "start_date": f.start_date.isoformat() if f.start_date else None,
        "end_date": f.end_date.isoformat() if f.end_date else None,
        "store_ids": list(f.store_ids),
        "region_ids": list(f.region_ids),
        "category_ids": list(f.category_ids),
        "employee_ids": list(f.employee_ids),
        "customer_id": f.customer_id,
        "order_statuses": list(f.order_statuses),
    }


def filter_from_dict(d: dict[str, Any]) -> AnalyticsFilter:
    return AnalyticsFilter(
        start_date=date.fromisoformat(d["start_date"]) if d.get("start_date") else None,
        end_date=date.fromisoformat(d["end_date"]) if d.get("end_date") else None,
        store_ids=list(d.get("store_ids") or []),
        region_ids=list(d.get("region_ids") or []),
        category_ids=list(d.get("category_ids") or []),
        employee_ids=list(d.get("employee_ids") or []),
        customer_id=d.get("customer_id"),
        order_statuses=list(d.get("order_statuses") or ["paid", "completed"]),
    )


def previous_period_filter(f: AnalyticsFilter) -> AnalyticsFilter:
    """Shift the date window backward by the same length."""
    if f.start_date is None or f.end_date is None:
        return AnalyticsFilter.last_n_days(30)
    length = (f.end_date - f.start_date).days
    if length <= 0:
        length = 30
    new_end = f.start_date
    new_start = new_end - timedelta(days=length)
    return AnalyticsFilter(
        start_date=new_start,
        end_date=new_end,
        store_ids=list(f.store_ids),
        region_ids=list(f.region_ids),
        category_ids=list(f.category_ids),
        employee_ids=list(f.employee_ids),
        customer_id=f.customer_id,
        order_statuses=list(f.order_statuses),
    )


@st.cache_data(ttl=300, show_spinner=False)
def load_dimension_options() -> dict[str, list[dict[str, Any]]]:
    """Regions, stores, categories, employees for filter widgets."""
    reset_session_factory()
    _ = get_engine()
    with session_scope(commit=False) as session:
        regions = [
            {"id": r.id, "label": f"{r.code} — {r.name}"}
            for r in session.scalars(
                select(Region).where(Region.deleted_at.is_(None)).order_by(Region.code)
            ).all()
        ]
        stores = [
            {
                "id": s.id,
                "label": f"{s.code} — {s.name}",
                "region_id": s.region_id,
            }
            for s in session.scalars(
                select(Store).where(Store.deleted_at.is_(None)).order_by(Store.code)
            ).all()
        ]
        categories = [
            {"id": c.id, "label": f"{c.code} — {c.name}"}
            for c in session.scalars(
                select(Category).where(Category.deleted_at.is_(None)).order_by(Category.code)
            ).all()
        ]
        employees = [
            {
                "id": e.id,
                "label": f"{e.code} — {e.first_name} {e.last_name}",
                "store_id": e.store_id,
            }
            for e in session.scalars(
                select(Employee).where(Employee.deleted_at.is_(None)).order_by(Employee.code)
            ).all()
        ]
    return {
        "regions": regions,
        "stores": stores,
        "categories": categories,
        "employees": employees,
    }


@st.cache_data(ttl=300, show_spinner="Loading KPIs…")
def load_kpi(f_dict: dict[str, Any]) -> dict[str, Any]:
    f = filter_from_dict(f_dict)
    reset_session_factory()
    _ = get_engine()
    with session_scope(commit=False) as session:
        kpi = MetricsService(session).summary(f)
        prev = MetricsService(session).summary(previous_period_filter(f))
    return {"current": kpi.as_dict(), "previous": prev.as_dict()}


@st.cache_data(ttl=300, show_spinner="Loading order lines…")
def load_order_lines(f_dict: dict[str, Any]) -> pd.DataFrame:
    f = filter_from_dict(f_dict)
    reset_session_factory()
    _ = get_engine()
    with session_scope(commit=False) as session:
        return AnalyticsRepository(session).fetch_order_lines(f)


@st.cache_data(ttl=300, show_spinner=False)
def load_orders_header(f_dict: dict[str, Any]) -> pd.DataFrame:
    f = filter_from_dict(f_dict)
    reset_session_factory()
    _ = get_engine()
    with session_scope(commit=False) as session:
        return AnalyticsRepository(session).fetch_orders_header(f)


@st.cache_data(ttl=300, show_spinner="Loading RFM…")
def load_rfm(f_dict: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame]:
    f = filter_from_dict(f_dict)
    reset_session_factory()
    _ = get_engine()
    with session_scope(commit=False) as session:
        return CustomerAnalyticsService(session).rfm(f)


@st.cache_data(ttl=300, show_spinner=False)
def load_clv(f_dict: dict[str, Any], top_n: int = 20) -> pd.DataFrame:
    f = filter_from_dict(f_dict)
    reset_session_factory()
    _ = get_engine()
    with session_scope(commit=False) as session:
        return CustomerAnalyticsService(session).clv(f, top_n=top_n)


@st.cache_data(ttl=300, show_spinner=False)
def load_repeat_rate(f_dict: dict[str, Any]) -> dict[str, float | int]:
    f = filter_from_dict(f_dict)
    reset_session_factory()
    _ = get_engine()
    with session_scope(commit=False) as session:
        return CustomerAnalyticsService(session).repeat_rate(f)


@st.cache_data(ttl=300, show_spinner="Loading cohort…")
def load_cohort(f_dict: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame]:
    f = filter_from_dict(f_dict)
    reset_session_factory()
    _ = get_engine()
    with session_scope(commit=False) as session:
        return CustomerAnalyticsService(session).cohort(f)


@st.cache_data(ttl=300, show_spinner="Loading ABC…")
def load_abc(f_dict: dict[str, Any]) -> pd.DataFrame:
    f = filter_from_dict(f_dict)
    reset_session_factory()
    _ = get_engine()
    with session_scope(commit=False) as session:
        return ProductAnalyticsService(session).abc(f)


@st.cache_data(ttl=300, show_spinner=False)
def load_top_products(f_dict: dict[str, Any], by: str = "revenue", top_n: int = 20) -> pd.DataFrame:
    f = filter_from_dict(f_dict)
    reset_session_factory()
    _ = get_engine()
    with session_scope(commit=False) as session:
        return ProductAnalyticsService(session).top_products(f, by=by, top_n=top_n)


@st.cache_data(ttl=300, show_spinner=False)
def load_inventory() -> pd.DataFrame:
    reset_session_factory()
    _ = get_engine()
    with session_scope(commit=False) as session:
        return InventoryService(session).snapshot()


@st.cache_data(ttl=300, show_spinner=False)
def load_low_stock() -> pd.DataFrame:
    reset_session_factory()
    _ = get_engine()
    with session_scope(commit=False) as session:
        return InventoryService(session).low_stock()


def daily_revenue_series(lines: pd.DataFrame) -> pd.DataFrame:
    if lines.empty:
        return pd.DataFrame(columns=["day", "revenue"])
    df = lines.copy()
    df["day"] = pd.to_datetime(df["order_date"], utc=True).dt.date
    out: pd.DataFrame = (
        df.groupby("day", as_index=False).agg(revenue=("line_total", "sum")).sort_values("day")
    )
    return out


def monthly_trend(lines: pd.DataFrame) -> pd.DataFrame:
    monthly = monthly_aggregate(lines)
    if monthly.empty:
        return monthly
    return add_mom_change(monthly, value_col="revenue")
