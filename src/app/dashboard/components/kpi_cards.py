"""KPI metric row for Streamlit."""

from __future__ import annotations

from typing import Any

import streamlit as st

from app.visualization.styles import format_money, format_number, format_percent


def _delta_pct(current: float, previous: float) -> float | None:
    if previous == 0:
        return None
    return round(100.0 * (current - previous) / previous, 1)


def render_kpi_row(current: dict[str, Any], previous: dict[str, Any] | None = None) -> None:
    """Render 7 KPI cards with optional period-over-period deltas."""
    prev = previous or {}

    def metric(label: str, value: str, key: str) -> None:
        cur_v = float(current.get(key) or 0)
        prev_v = float(prev.get(key) or 0)
        d = _delta_pct(cur_v, prev_v)
        if d is None:
            st.metric(label, value)
        else:
            st.metric(label, value, delta=f"{d}%")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric("Revenue", format_money(current.get("revenue")), "revenue")
    with c2:
        metric("Gross Profit", format_money(current.get("gross_profit")), "gross_profit")
    with c3:
        metric(
            "Gross Margin",
            format_percent(current.get("gross_margin_pct")),
            "gross_margin_pct",
        )
    with c4:
        metric("Orders", format_number(current.get("order_count")), "order_count")

    c5, c6, c7 = st.columns(3)
    with c5:
        metric("Buyers", format_number(current.get("buyer_count")), "buyer_count")
    with c6:
        metric("AOV", format_money(current.get("aov")), "aov")
    with c7:
        metric("Units sold", format_number(current.get("units_sold")), "units_sold")
