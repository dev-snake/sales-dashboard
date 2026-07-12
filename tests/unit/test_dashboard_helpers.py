"""Unit tests for dashboard helpers (no Streamlit runtime / no DB)."""

from __future__ import annotations

from datetime import date

import pandas as pd

from app.dashboard.data_access import daily_revenue_series, previous_period_filter
from app.schemas.filters import AnalyticsFilter


def test_previous_period_filter() -> None:
    f = AnalyticsFilter(
        start_date=date(2024, 2, 1),
        end_date=date(2024, 3, 1),
        store_ids=[1],
    )
    prev = previous_period_filter(f)
    # length = (Mar 1 - Feb 1) = 29 days (2024 leap year)
    assert prev.end_date == date(2024, 2, 1)
    assert prev.start_date == date(2024, 1, 3)
    assert prev.store_ids == [1]


def test_daily_revenue_series_empty() -> None:
    df = daily_revenue_series(pd.DataFrame())
    assert list(df.columns) == ["day", "revenue"]


def test_daily_revenue_series() -> None:
    lines = pd.DataFrame(
        {
            "order_date": pd.to_datetime(
                ["2024-01-01T10:00:00Z", "2024-01-01T12:00:00Z", "2024-01-02T09:00:00Z"]
            ),
            "line_total": [100, 50, 80],
        }
    )
    daily = daily_revenue_series(lines)
    assert len(daily) == 2
    assert float(daily.loc[daily["day"] == date(2024, 1, 1), "revenue"].iloc[0]) == 150
