"""Session-state helpers for dashboard filters."""

from __future__ import annotations

from datetime import UTC, datetime

import streamlit as st

from app.schemas.filters import AnalyticsFilter

FILTERS_KEY = "analytics_filters"
APPLIED_KEY = "filters_applied"


def default_filter() -> AnalyticsFilter:
    return AnalyticsFilter.last_n_days(30)


def get_filters() -> AnalyticsFilter:
    if FILTERS_KEY not in st.session_state:
        st.session_state[FILTERS_KEY] = default_filter()
    return st.session_state[FILTERS_KEY]  # type: ignore[no-any-return]


def set_filters(f: AnalyticsFilter) -> None:
    st.session_state[FILTERS_KEY] = f
    st.session_state[APPLIED_KEY] = datetime.now(UTC)


def last_applied() -> datetime | None:
    value = st.session_state.get(APPLIED_KEY)
    return value if isinstance(value, datetime) else None
