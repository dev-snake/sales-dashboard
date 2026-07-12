"""Integration: MetricsService revenue matches hand calculation on fixture rows."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from app.models import (
    Brand,
    Category,
    Customer,
    Employee,
    Order,
    OrderItem,
    Product,
    Region,
    Store,
    Supplier,
)
from app.schemas.filters import AnalyticsFilter
from app.services.metrics_service import MetricsService

pytestmark = pytest.mark.integration


def test_metrics_match_hand_calc(db_session: Session) -> None:
    # minimal masters
    region = Region(code="MTR-REG", name="Metrics Region", level=1)
    db_session.add(region)
    db_session.flush()
    store = Store(
        code="MTR-ST",
        name="Metrics Store",
        region_id=region.id,
        is_active=True,
        opened_at=date(2020, 1, 1),
    )
    db_session.add(store)
    db_session.flush()
    emp = Employee(
        code="MTR-EMP",
        first_name="Met",
        last_name="Rics",
        store_id=store.id,
        hire_date=date(2020, 1, 1),
        is_active=True,
    )
    db_session.add(emp)
    cat = Category(code="MTR-CAT", name="Metrics Cat")
    brand = Brand(code="MTR-BR", name="Metrics Brand Unique")
    sup = Supplier(code="MTR-SUP", name="Metrics Supplier", is_active=True)
    db_session.add_all([cat, brand, sup])
    db_session.flush()
    product = Product(
        sku="MTR-SKU-1",
        name="Metrics Product",
        category_id=cat.id,
        brand_id=brand.id,
        supplier_id=sup.id,
        unit_price=Decimal("100.00"),
        cost_price=Decimal("40.00"),
        is_active=True,
    )
    db_session.add(product)
    cust = Customer(
        code="MTR-CUS",
        first_name="Buy",
        last_name="Er",
        region_id=region.id,
        is_active=True,
    )
    db_session.add(cust)
    db_session.flush()

    order = Order(
        order_number="MTR-ORD-1",
        customer_id=cust.id,
        store_id=store.id,
        employee_id=emp.id,
        order_date=datetime(2024, 6, 15, 12, 0, tzinfo=UTC),
        status="completed",
        subtotal=Decimal("200.00"),
        total_amount=Decimal("200.00"),
    )
    db_session.add(order)
    db_session.flush()
    item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        quantity=2,
        unit_price=Decimal("100.00"),
        unit_cost=Decimal("40.00"),
        discount_amount=Decimal("0"),
        line_total=Decimal("200.00"),
    )
    db_session.add(item)
    db_session.flush()

    f = AnalyticsFilter(
        start_date=date(2024, 6, 1),
        end_date=date(2024, 7, 1),
        store_ids=[store.id],
    )
    kpi = MetricsService(db_session).summary(f)
    assert kpi.revenue == Decimal("200.00")
    assert kpi.cogs == Decimal("80.00")
    assert kpi.gross_profit == Decimal("120.00")
    assert kpi.order_count == 1
    assert kpi.units_sold == 2
