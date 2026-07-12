"""Metric definition consistency: service formulas vs documented SQL semantics."""

from __future__ import annotations

from decimal import Decimal

import pandas as pd

from app.services.metrics_service import MetricsService
from app.sql_catalog import load_entry


def test_metrics_service_matches_documented_arithmetic() -> None:
    lines = pd.DataFrame(
        {
            "order_id": [1, 1, 2],
            "customer_id": [10, 10, 11],
            "quantity": [2, 1, 4],
            "unit_cost": [10, 5, 2.5],
            "line_total": [100, 40, 80],
        }
    )
    # hand: rev=220, cogs=2*10 + 1*5 + 4*2.5 = 20+5+10 = 35, profit=185
    kpi = MetricsService.summary_from_lines(lines, refunds=Decimal("20"))
    assert kpi.revenue == Decimal("220.00")
    assert kpi.cogs == Decimal("35.00")
    assert kpi.gross_profit == Decimal("185.00")
    assert kpi.order_count == 2
    assert kpi.buyer_count == 2
    assert kpi.net_revenue == Decimal("200.00")


def test_sql_r01_r02_mention_status_and_line_total() -> None:
    r01 = load_entry("R01").sql.lower()
    r02 = load_entry("R02").sql.lower()
    for sql in (r01, r02):
        assert "paid" in sql and "completed" in sql
        assert "line_total" in sql


def test_sql_r17_aov_uses_order_count() -> None:
    sql = load_entry("R17").sql.lower()
    assert "aov" in sql or "order_count" in sql
    assert "paid" in sql
