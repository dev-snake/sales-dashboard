"""Products page — top N, treemap, ABC, tables."""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[3]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import streamlit as st

from app.dashboard.components.charts import plot_bar, plot_pie, plot_treemap
from app.dashboard.components.filters import render_sidebar_filters
from app.dashboard.data_access import (
    filter_to_dict,
    load_abc,
    load_low_stock,
    load_order_lines,
    load_top_products,
)
from app.utils.logging import setup_logging

st.set_page_config(page_title="Products · Sales Analytics", page_icon="📦", layout="wide")
setup_logging()

st.title("📦 Products")
filters = render_sidebar_filters()
fd = filter_to_dict(filters)

by = st.radio("Rank by", ["revenue", "profit"], horizontal=True)

try:
    lines = load_order_lines(fd)
    top = load_top_products(fd, by=by, top_n=20)
    abc = load_abc(fd)
    low = load_low_stock()
except Exception as exc:
    st.error(f"Failed to load data: {exc}")
    st.stop()

if lines.empty:
    st.info("Không có đơn hàng trong kỳ đã chọn.")
    st.stop()

st.subheader(f"Top products by {by}")
if not top.empty:
    top = top.copy()
    top["label"] = top["sku"].astype(str) + " — " + top["product_name"].astype(str).str[:40]
    plot_bar(top, "label", by, title=f"Top 20 by {by}", key="prod_top", orientation="h")

c1, c2 = st.columns(2)
with c1:
    tree = (
        lines.groupby(["category_name", "product_name"], as_index=False)["line_total"]
        .sum()
        .rename(columns={"line_total": "revenue"})
    )
    # treemap needs non-null path
    tree = tree.dropna(subset=["category_name", "product_name"])
    if not tree.empty:
        plot_treemap(
            tree,
            path=["category_name", "product_name"],
            values="revenue",
            title="Category → product revenue",
            key="prod_tree",
        )
with c2:
    if not abc.empty and "abc_class" in abc.columns:
        share = abc.groupby("abc_class", as_index=False)["revenue"].sum()
        plot_pie(share, "abc_class", "revenue", title="ABC class share", key="prod_abc_pie")
        st.dataframe(
            (
                abc[["sku", "product_name", "revenue", "cum_pct", "abc_class"]].head(30)
                if "sku" in abc.columns
                else abc.head(30)
            ),
            use_container_width=True,
            hide_index=True,
        )

st.subheader("Inventory slow / low stock (snapshot)")
if low.empty:
    st.info("No low-stock rows (or inventory empty).")
else:
    st.dataframe(low.head(50), use_container_width=True, hide_index=True)
