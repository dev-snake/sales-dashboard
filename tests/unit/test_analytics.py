"""Unit tests for pure analytics (no database)."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

import pandas as pd

from app.analytics.abc import abc_classify, pareto_products_for_share
from app.analytics.cohort import build_cohort_matrix, cohort_pivot
from app.analytics.descriptive import margin_pct, safe_div
from app.analytics.rfm import compute_rfm_raw, score_rfm, segment_summary
from app.analytics.trends import add_mom_change, monthly_aggregate
from app.services.metrics_service import MetricsService


def _lines() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "order_id": 1,
                "customer_id": 10,
                "product_id": 100,
                "quantity": 2,
                "unit_cost": 50,
                "line_total": 200,
                "order_date": datetime(2024, 1, 5, tzinfo=UTC),
            },
            {
                "order_id": 1,
                "customer_id": 10,
                "product_id": 101,
                "quantity": 1,
                "unit_cost": 30,
                "line_total": 80,
                "order_date": datetime(2024, 1, 5, tzinfo=UTC),
            },
            {
                "order_id": 2,
                "customer_id": 11,
                "product_id": 100,
                "quantity": 3,
                "unit_cost": 50,
                "line_total": 300,
                "order_date": datetime(2024, 2, 10, tzinfo=UTC),
            },
            {
                "order_id": 3,
                "customer_id": 10,
                "product_id": 102,
                "quantity": 1,
                "unit_cost": 10,
                "line_total": 40,
                "order_date": datetime(2024, 3, 1, tzinfo=UTC),
            },
        ]
    )


def test_safe_div_and_margin() -> None:
    assert safe_div(10, 0) == Decimal("0")
    assert safe_div(10, 4) == Decimal("2.5")
    assert margin_pct(200, 50) == Decimal("75.00")
    assert margin_pct(0, 0) == Decimal("0")


def test_metrics_summary_from_lines() -> None:
    kpi = MetricsService.summary_from_lines(_lines(), refunds=Decimal("20"))
    assert kpi.revenue == Decimal("620.00")
    assert kpi.order_count == 3
    assert kpi.buyer_count == 2
    assert kpi.units_sold == 7
    assert kpi.cogs == Decimal("290.00")  # 2*50 + 1*30 + 3*50 + 1*10
    assert kpi.gross_profit == Decimal("330.00")
    assert kpi.net_revenue == Decimal("600.00")
    assert kpi.aov == (Decimal("620") / 3).quantize(Decimal("0.01"))


def test_abc_and_pareto() -> None:
    df = pd.DataFrame(
        {
            "product_id": [1, 2, 3, 4, 5],
            "revenue": [50, 30, 10, 5, 5],
        }
    )
    abc = abc_classify(df)
    assert set(abc["abc_class"]) <= {"A", "B", "C"}
    assert abc.iloc[0]["abc_class"] == "A"
    p = pareto_products_for_share(abc, share=0.80)
    assert p["products_for_share"] >= 1
    assert p["total_products"] == 5


def test_rfm_scores() -> None:
    raw = compute_rfm_raw(_lines(), as_of=date(2024, 3, 15))
    assert set(raw.columns) >= {
        "customer_id",
        "recency_days",
        "frequency",
        "monetary",
    }
    assert raw.loc[raw["customer_id"] == 10, "frequency"].iloc[0] == 2
    scored = score_rfm(raw)
    assert "segment" in scored.columns
    summary = segment_summary(scored)
    assert "customers" in summary.columns


def test_cohort_matrix() -> None:
    orders = pd.DataFrame(
        {
            "customer_id": [1, 1, 2, 2, 3],
            "order_date": pd.to_datetime(
                [
                    "2024-01-10",
                    "2024-02-15",
                    "2024-01-20",
                    "2024-03-01",
                    "2024-02-05",
                ],
                utc=True,
            ),
        }
    )
    matrix = build_cohort_matrix(orders)
    assert not matrix.empty
    assert "retention_rate" in matrix.columns
    pivot = cohort_pivot(matrix)
    assert pivot.shape[0] >= 1


def test_monthly_trend_mom() -> None:
    monthly = monthly_aggregate(_lines())
    assert len(monthly) == 3
    trend = add_mom_change(monthly, value_col="revenue")
    assert "mom_pct" in trend.columns
    assert pd.isna(trend.iloc[0]["mom_pct"])


def test_metrics_empty() -> None:
    kpi = MetricsService.summary_from_lines(pd.DataFrame())
    assert kpi.order_count == 0
    assert kpi.revenue == Decimal("0")
