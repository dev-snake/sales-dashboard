"""Data quality invariants (DQ01–DQ10) — skip if DB empty / unavailable.

Run after seed for meaningful coverage:

    sales-dashboard seed run --scale 100 --reset --yes
    pytest -m data_quality
"""

from __future__ import annotations

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

pytestmark = pytest.mark.data_quality


def _has_orders(session: Session) -> bool:
    n = session.execute(text("SELECT COUNT(*) FROM orders")).scalar_one()
    return int(n or 0) > 0


def test_dq01_no_orphan_order_items(db_session: Session) -> None:
    if not _has_orders(db_session):
        pytest.skip("no orders — seed first")
    orphans = db_session.execute(text("""
            SELECT COUNT(*) FROM order_items oi
            LEFT JOIN orders o ON o.id = oi.order_id
            WHERE o.id IS NULL
            """)).scalar_one()
    assert orphans == 0


def test_dq03_line_total_formula(db_session: Session) -> None:
    if not _has_orders(db_session):
        pytest.skip("no orders — seed first")
    bad = db_session.execute(text("""
            SELECT COUNT(*) FROM order_items
            WHERE ABS(line_total - (quantity * unit_price - discount_amount)) > 0.01
            """)).scalar_one()
    assert bad == 0


def test_dq05_return_qty_not_exceed_item(db_session: Session) -> None:
    n = db_session.execute(text("SELECT COUNT(*) FROM returns")).scalar_one()
    if int(n or 0) == 0:
        pytest.skip("no returns")
    bad = db_session.execute(text("""
            SELECT COUNT(*)
            FROM returns r
            JOIN order_items oi ON oi.id = r.order_item_id
            WHERE r.quantity > oi.quantity
            """)).scalar_one()
    assert bad == 0


def test_dq06_inventory_nonneg(db_session: Session) -> None:
    n = db_session.execute(text("SELECT COUNT(*) FROM inventory")).scalar_one()
    if int(n or 0) == 0:
        pytest.skip("no inventory")
    bad = db_session.execute(
        text("SELECT COUNT(*) FROM inventory WHERE quantity_on_hand < 0")
    ).scalar_one()
    assert bad == 0


def test_dq07_unique_customer_codes(db_session: Session) -> None:
    dups = db_session.execute(text("""
            SELECT code, COUNT(*) FROM customers
            WHERE deleted_at IS NULL
            GROUP BY code HAVING COUNT(*) > 1
            """)).fetchall()
    assert dups == []


def test_dq07_unique_product_skus(db_session: Session) -> None:
    dups = db_session.execute(text("""
            SELECT sku, COUNT(*) FROM products
            WHERE deleted_at IS NULL
            GROUP BY sku HAVING COUNT(*) > 1
            """)).fetchall()
    assert dups == []


def test_dq08_revenue_status_filter_concept(db_session: Session) -> None:
    """Cancelled orders must not dominate if we only count paid/completed in metrics."""
    if not _has_orders(db_session):
        pytest.skip("no orders")
    # Smoke: query runs and returns a number
    rev = db_session.execute(text("""
            SELECT COALESCE(SUM(oi.line_total), 0)
            FROM order_items oi
            JOIN orders o ON o.id = oi.order_id
            WHERE o.status IN ('paid', 'completed')
            """)).scalar_one()
    assert float(rev) >= 0


def test_dq09_calendar_present(db_session: Session) -> None:
    n = db_session.execute(text("SELECT COUNT(*) FROM calendar")).scalar_one()
    # calendar may be empty if never seeded — skip
    if int(n or 0) == 0:
        pytest.skip("calendar empty — run seed")
    assert int(n) > 365
