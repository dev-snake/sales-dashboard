"""Inventory & returns snapshot page."""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[3]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import streamlit as st

from app.dashboard.components.charts import plot_bar
from app.dashboard.components.filters import render_sidebar_filters
from app.dashboard.data_access import (
    filter_to_dict,
    load_inventory,
    load_low_stock,
    load_order_lines,
)
from app.utils.logging import setup_logging

st.set_page_config(page_title="Inventory · Sales Analytics", page_icon="📋", layout="wide")
setup_logging()

st.title("📋 Inventory")
filters = render_sidebar_filters()
fd = filter_to_dict(filters)

try:
    inv = load_inventory()
    low = load_low_stock()
    lines = load_order_lines(fd)
except Exception as exc:
    st.error(f"Failed to load data: {exc}")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("Inventory rows", f"{len(inv):,}")
c2.metric("Low stock SKUs", f"{len(low):,}")
if not inv.empty:
    c3.metric("Total units on hand", f"{int(inv['quantity_on_hand'].sum()):,}")

st.subheader("Stock by store (top)")
if inv.empty:
    st.info("No inventory data. Run seed to populate.")
else:
    by_store = (
        inv.groupby("store_code", as_index=False)["quantity_on_hand"]
        .sum()
        .sort_values("quantity_on_hand", ascending=False)
    )
    plot_bar(by_store, "store_code", "quantity_on_hand", title="On-hand by store", key="inv_store")

st.subheader("Low stock (quantity ≤ reorder level)")
if low.empty:
    st.success("No low-stock items (or empty inventory).")
else:
    st.dataframe(low, use_container_width=True, hide_index=True)

st.subheader("Sales units in filter (context)")
if lines.empty:
    st.info("No sales in selected period.")
else:
    sold = (
        lines.groupby(["sku", "product_name"], as_index=False)["quantity"]
        .sum()
        .sort_values("quantity", ascending=False)
        .head(20)
    )
    sold["label"] = sold["sku"].astype(str)
    plot_bar(sold, "label", "quantity", title="Top units sold", key="inv_sold", orientation="h")
