"""Sales analysis page — trends, heatmap, scatter, histogram, payments, ranking."""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[3]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import pandas as pd
import streamlit as st

from app.dashboard.components.charts import (
    plot_bar,
    plot_heatmap,
    plot_hist,
    plot_line,
    plot_pie,
    plot_scatter,
)
from app.dashboard.components.filters import render_sidebar_filters
from app.dashboard.data_access import (
    daily_revenue_series,
    filter_to_dict,
    load_order_lines,
    load_orders_header,
)
from app.utils.logging import setup_logging

st.set_page_config(page_title="Sales · Sales Analytics", page_icon="📈", layout="wide")
setup_logging()

st.title("📈 Sales Analysis")
filters = render_sidebar_filters()
fd = filter_to_dict(filters)

try:
    lines = load_order_lines(fd)
    headers = load_orders_header(fd)
except Exception as exc:
    st.error(f"Failed to load data: {exc}")
    st.stop()

if lines.empty:
    st.info("Không có đơn hàng trong kỳ đã chọn.")
    st.stop()

grain = st.radio("Trend grain", ["day", "week", "month"], horizontal=True)
daily = daily_revenue_series(lines)
if grain == "day":
    plot_line(daily, "day", "revenue", title="Daily revenue", key="sales_line")
elif grain == "week":
    tmp = lines.copy()
    tmp["week"] = pd.to_datetime(tmp["order_date"], utc=True).dt.to_period("W").astype(str)
    weekly = (
        tmp.groupby("week", as_index=False)["line_total"]
        .sum()
        .rename(columns={"line_total": "revenue"})
    )
    plot_line(weekly, "week", "revenue", title="Weekly revenue", key="sales_week")
else:
    tmp = lines.copy()
    ts = pd.to_datetime(tmp["order_date"], utc=True)
    tmp["month"] = pd.to_datetime({"year": ts.dt.year, "month": ts.dt.month, "day": 1})
    monthly = (
        tmp.groupby("month", as_index=False)["line_total"]
        .sum()
        .rename(columns={"line_total": "revenue"})
    )
    plot_line(monthly, "month", "revenue", title="Monthly revenue", key="sales_month")

c1, c2 = st.columns(2)
with c1:
    # Heatmap: weekday × month
    tmp = lines.copy()
    ts = pd.to_datetime(tmp["order_date"], utc=True)
    tmp["weekday"] = ts.dt.day_name()
    tmp["month"] = ts.dt.strftime("%Y-%m")
    heat = tmp.pivot_table(
        index="weekday", columns="month", values="line_total", aggfunc="sum", fill_value=0
    )
    # order weekdays
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heat = heat.reindex([d for d in order if d in heat.index])
    plot_heatmap(heat, title="Revenue heatmap (weekday × month)", key="sales_heat")

with c2:
    if not headers.empty:
        # scatter: items per order vs total
        item_counts = lines.groupby("order_id", as_index=False).agg(
            items=("order_item_id", "count"),
            revenue=("line_total", "sum"),
        )
        plot_scatter(
            item_counts,
            "items",
            "revenue",
            title="Order size vs revenue",
            key="sales_scatter",
        )

c3, c4 = st.columns(2)
with c3:
    if not headers.empty:
        plot_hist(headers, "total_amount", title="Order total distribution", key="sales_hist")
with c4:
    # payment mix not in lines — use store ranking instead + note
    by_store = (
        lines.groupby("store_code", as_index=False)["line_total"]
        .sum()
        .rename(columns={"line_total": "revenue"})
        .sort_values("revenue", ascending=False)
    )
    plot_bar(by_store, "store_code", "revenue", title="Store ranking", key="sales_stores")

st.subheader("Category breakdown")
by_cat = (
    lines.groupby("category_name", as_index=False)["line_total"]
    .sum()
    .rename(columns={"line_total": "revenue", "category_name": "name"})
)
plot_pie(by_cat, "name", "revenue", title="Sales by category", key="sales_cat_pie")
