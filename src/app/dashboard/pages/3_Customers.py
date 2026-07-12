"""Customers page — RFM, CLV, repeat rate, cohort heatmap."""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[3]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import streamlit as st

from app.dashboard.components.charts import plot_bar, plot_heatmap
from app.dashboard.components.filters import render_sidebar_filters
from app.dashboard.data_access import (
    filter_to_dict,
    load_clv,
    load_cohort,
    load_repeat_rate,
    load_rfm,
)
from app.utils.logging import setup_logging
from app.visualization.styles import format_percent

st.set_page_config(page_title="Customers · Sales Analytics", page_icon="👥", layout="wide")
setup_logging()

st.title("👥 Customers")
filters = render_sidebar_filters()
fd = filter_to_dict(filters)

try:
    scored, segment_summary = load_rfm(fd)
    clv = load_clv(fd, top_n=20)
    repeat = load_repeat_rate(fd)
    matrix, pivot = load_cohort(fd)
except Exception as exc:
    st.error(f"Failed to load data: {exc}")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("Total buyers", f"{repeat.get('total_buyers', 0):,}")
c2.metric("Repeat buyers", f"{repeat.get('repeat_buyers', 0):,}")
c3.metric("Repeat rate", format_percent(repeat.get("repeat_customer_rate_pct", 0)))

st.subheader("RFM segments")
if segment_summary.empty:
    st.info("No RFM data in range.")
else:
    plot_bar(
        segment_summary,
        "segment",
        "customers",
        title="Customers by RFM segment",
        key="cust_rfm_bar",
    )
    st.dataframe(segment_summary, use_container_width=True, hide_index=True)

st.subheader("Top customers (CLV / lifetime revenue in filter)")
if clv.empty:
    st.info("No customer revenue.")
else:
    show = clv.copy()
    show["label"] = show["customer_code"].astype(str)
    plot_bar(
        show,
        "label",
        "lifetime_revenue",
        title="Top CLV",
        key="cust_clv",
        orientation="h",
    )
    st.dataframe(show, use_container_width=True, hide_index=True)

st.subheader("Cohort retention")
if pivot.empty:
    st.info("Not enough history for cohort.")
else:
    plot_heatmap(pivot, title="Cohort retention rate", key="cust_cohort")
    with st.expander("Cohort long table"):
        st.dataframe(matrix.head(100), use_container_width=True, hide_index=True)

if not scored.empty:
    with st.expander("RFM scored customers (sample)"):
        cols = [
            c
            for c in (
                "customer_id",
                "recency_days",
                "frequency",
                "monetary",
                "r_score",
                "f_score",
                "m_score",
                "segment",
            )
            if c in scored.columns
        ]
        st.dataframe(
            scored.sort_values("monetary", ascending=False).head(50)[cols],
            use_container_width=True,
            hide_index=True,
        )
