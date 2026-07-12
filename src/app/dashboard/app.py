"""Sales Analytics Dashboard — Streamlit entry (Overview / Home).

Run:
    streamlit run src/app/dashboard/app.py
    # or from project root with PYTHONPATH=src
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure `app` package is importable when launched via streamlit
_SRC = Path(__file__).resolve().parents[2]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import streamlit as st

from app.dashboard.components.charts import plot_area, plot_bar, plot_pie
from app.dashboard.components.filters import render_sidebar_filters
from app.dashboard.components.kpi_cards import render_kpi_row
from app.dashboard.data_access import (
    daily_revenue_series,
    filter_to_dict,
    load_kpi,
    load_order_lines,
)
from app.dashboard.state import last_applied
from app.utils.logging import setup_logging
from app.visualization.styles import format_money

st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

setup_logging()

st.title("📊 Sales Analytics Dashboard")
st.caption("Overview · Data source: PostgreSQL · Metrics: paid + completed orders")

filters = render_sidebar_filters()
applied = last_applied()
if applied:
    st.caption(f"Filters applied at {applied.strftime('%Y-%m-%d %H:%M:%S UTC')}")

fd = filter_to_dict(filters)

try:
    kpi_bundle = load_kpi(fd)
    lines = load_order_lines(fd)
except Exception as exc:
    st.error(f"Database connection or query failed: {exc}")
    st.info("Check DATABASE_URL in `.env`, then run `sales-dashboard db migrate` and seed data.")
    st.stop()

render_kpi_row(kpi_bundle["current"], kpi_bundle["previous"])

if lines.empty:
    st.info("Không có đơn hàng trong kỳ đã chọn.")
    st.stop()

# --- Charts row ---
st.subheader("Trends & mix")
daily = daily_revenue_series(lines)
plot_area(daily, "day", "revenue", title="Revenue over time", key="ov_area")

c1, c2 = st.columns(2)
with c1:
    if "region_id" in lines.columns or "store_code" in lines.columns:
        # region via store is not joined name — use store for overview secondary
        by_store = (
            lines.groupby("store_code", as_index=False)["line_total"]
            .sum()
            .rename(columns={"line_total": "revenue"})
            .sort_values("revenue", ascending=False)
            .head(15)
        )
        plot_bar(by_store, "store_code", "revenue", title="Revenue by store", key="ov_store")
with c2:
    if "category_name" in lines.columns:
        by_cat = (
            lines.groupby("category_name", as_index=False)["line_total"]
            .sum()
            .rename(columns={"line_total": "revenue", "category_name": "category"})
        )
        plot_pie(by_cat, "category", "revenue", title="Category mix", key="ov_pie")

st.subheader("Top products & stores")
col_p, col_s = st.columns(2)
with col_p:
    top_prod = (
        lines.groupby(["sku", "product_name"], as_index=False)["line_total"]
        .sum()
        .rename(columns={"line_total": "revenue"})
        .sort_values("revenue", ascending=False)
        .head(10)
    )
    top_prod["label"] = top_prod["sku"] + " — " + top_prod["product_name"].astype(str).str[:30]
    plot_bar(
        top_prod,
        "label",
        "revenue",
        title="Top 10 products",
        key="ov_top_prod",
        orientation="h",
    )
with col_s:
    top_store = (
        lines.groupby("store_code", as_index=False)
        .agg(revenue=("line_total", "sum"), orders=("order_id", "nunique"))
        .sort_values("revenue", ascending=False)
        .head(10)
    )
    st.dataframe(
        top_store.assign({"revenue": lambda s: s.map(lambda v: format_money(v))}),
        use_container_width=True,
        hide_index=True,
    )

st.caption("Navigate pages in the sidebar: Sales · Products · Customers · Inventory")
