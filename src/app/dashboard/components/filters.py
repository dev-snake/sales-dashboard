"""Sidebar filter form → AnalyticsFilter."""

from __future__ import annotations

from datetime import date, timedelta

import streamlit as st

from app.dashboard.data_access import load_dimension_options
from app.dashboard.state import default_filter, get_filters, set_filters
from app.schemas.filters import AnalyticsFilter


def render_sidebar_filters() -> AnalyticsFilter:
    """Render filter form; return currently applied AnalyticsFilter."""
    current = get_filters()
    try:
        dims = load_dimension_options()
    except Exception as exc:
        st.sidebar.error(f"Cannot load filter dimensions: {exc}")
        return current

    st.sidebar.header("Filters")
    with st.sidebar.form("global_filters"):
        today = date.today()
        default_start = current.start_date or (today - timedelta(days=30))
        default_end = (current.end_date - timedelta(days=1)) if current.end_date else today

        date_range = st.date_input(
            "Date range",
            value=(default_start, default_end),
            max_value=today,
        )

        region_opts = {d["label"]: d["id"] for d in dims["regions"]}
        store_opts_all = dims["stores"]
        cat_opts = {d["label"]: d["id"] for d in dims["categories"]}
        emp_opts = {d["label"]: d["id"] for d in dims["employees"]}

        selected_regions = st.multiselect(
            "Region",
            options=list(region_opts.keys()),
            default=[],
        )
        region_ids = [region_opts[label] for label in selected_regions]

        # cascade stores by region
        if region_ids:
            store_pool = [s for s in store_opts_all if s["region_id"] in region_ids]
        else:
            store_pool = store_opts_all
        store_map = {s["label"]: s["id"] for s in store_pool}
        selected_stores = st.multiselect("Store", options=list(store_map.keys()), default=[])
        store_ids = [store_map[label] for label in selected_stores]

        selected_cats = st.multiselect("Category", options=list(cat_opts.keys()), default=[])
        category_ids = [cat_opts[label] for label in selected_cats]

        selected_emps = st.multiselect("Employee", options=list(emp_opts.keys()), default=[])
        employee_ids = [emp_opts[label] for label in selected_emps]

        with st.expander("Advanced"):
            statuses = st.multiselect(
                "Order status",
                options=["paid", "completed", "pending", "cancelled"],
                default=current.order_statuses or ["paid", "completed"],
            )

        col_a, col_b = st.columns(2)
        apply_btn = col_a.form_submit_button("Apply", type="primary", use_container_width=True)
        reset_btn = col_b.form_submit_button("Reset", use_container_width=True)

    if reset_btn:
        set_filters(default_filter())
        st.rerun()

    if apply_btn:
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_d, end_d = date_range
        else:
            start_d, end_d = default_start, default_end
        # end exclusive: +1 day
        new_f = AnalyticsFilter(
            start_date=start_d,
            end_date=end_d + timedelta(days=1),
            region_ids=region_ids,
            store_ids=store_ids,
            category_ids=category_ids,
            employee_ids=employee_ids,
            order_statuses=statuses or ["paid", "completed"],
        )
        set_filters(new_f)
        st.rerun()

    return get_filters()
