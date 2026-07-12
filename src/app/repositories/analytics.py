"""Analytics data access — load line-level frames for Python analytics."""

from __future__ import annotations

import pandas as pd
from sqlalchemy import Select, and_, func, select
from sqlalchemy.orm import Session

from app.models import (
    Category,
    Customer,
    Inventory,
    Order,
    OrderItem,
    Product,
    Return,
    Store,
)
from app.schemas.filters import AnalyticsFilter


class AnalyticsRepository:
    """Fetch denormalized slices for metrics & analytics services."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def fetch_order_lines(self, filters: AnalyticsFilter | None = None) -> pd.DataFrame:
        """Line items joined to orders (+ optional dims) for revenue analytics."""
        f = filters or AnalyticsFilter()
        stmt: Select[tuple] = (
            select(
                OrderItem.id.label("order_item_id"),
                OrderItem.order_id,
                OrderItem.product_id,
                OrderItem.quantity,
                OrderItem.unit_price,
                OrderItem.unit_cost,
                OrderItem.discount_amount,
                OrderItem.line_total,
                Order.order_number,
                Order.order_date,
                Order.status,
                Order.customer_id,
                Order.store_id,
                Order.employee_id,
                Order.promotion_id,
                Product.sku,
                Product.name.label("product_name"),
                Product.category_id,
                Category.name.label("category_name"),
                Store.code.label("store_code"),
                Store.name.label("store_name"),
                Store.region_id,
                Customer.code.label("customer_code"),
            )
            .select_from(OrderItem)
            .join(Order, Order.id == OrderItem.order_id)
            .join(Product, Product.id == OrderItem.product_id)
            .outerjoin(Category, Category.id == Product.category_id)
            .outerjoin(Store, Store.id == Order.store_id)
            .outerjoin(Customer, Customer.id == Order.customer_id)
            .where(Order.status.in_(f.order_statuses or ["paid", "completed"]))
        )
        stmt = self._apply_filters(stmt, f)
        return self._to_frame(stmt)

    def fetch_orders_header(self, filters: AnalyticsFilter | None = None) -> pd.DataFrame:
        f = filters or AnalyticsFilter()
        stmt = select(
            Order.id.label("order_id"),
            Order.order_number,
            Order.order_date,
            Order.status,
            Order.customer_id,
            Order.store_id,
            Order.employee_id,
            Order.total_amount,
            Order.subtotal,
            Order.discount_amount,
            Order.tax_amount,
        ).where(Order.status.in_(f.order_statuses or ["paid", "completed"]))
        # reuse filter helpers on Order only
        start, end = f.resolve_bounds()
        if start is not None:
            stmt = stmt.where(Order.order_date >= start)
        if end is not None:
            stmt = stmt.where(Order.order_date < end)
        if f.store_ids:
            stmt = stmt.where(Order.store_id.in_(f.store_ids))
        if f.employee_ids:
            stmt = stmt.where(Order.employee_id.in_(f.employee_ids))
        if f.customer_id is not None:
            stmt = stmt.where(Order.customer_id == f.customer_id)
        return self._to_frame(stmt)

    def fetch_refunds_total(self, filters: AnalyticsFilter | None = None) -> float:
        f = filters or AnalyticsFilter()
        stmt = select(func.coalesce(func.sum(Return.refund_amount), 0)).where(
            Return.status.in_(["approved", "completed"])
        )
        start, end = f.resolve_bounds()
        if start is not None:
            stmt = stmt.where(Return.returned_at >= start)
        if end is not None:
            stmt = stmt.where(Return.returned_at < end)
        if f.store_ids:
            stmt = stmt.where(Return.store_id.in_(f.store_ids))
        val = self.session.scalar(stmt)
        return float(val or 0)

    def fetch_inventory(self) -> pd.DataFrame:
        stmt = (
            select(
                Inventory.store_id,
                Inventory.product_id,
                Inventory.quantity_on_hand,
                Inventory.reorder_level,
                Inventory.max_level,
                Product.sku,
                Product.name.label("product_name"),
                Store.code.label("store_code"),
            )
            .join(Product, Product.id == Inventory.product_id)
            .join(Store, Store.id == Inventory.store_id)
        )
        return self._to_frame(stmt)

    def _apply_filters(self, stmt: Select[tuple], f: AnalyticsFilter) -> Select[tuple]:
        start, end = f.resolve_bounds()
        conds = []
        if start is not None:
            conds.append(Order.order_date >= start)
        if end is not None:
            conds.append(Order.order_date < end)
        if f.store_ids:
            conds.append(Order.store_id.in_(f.store_ids))
        if f.employee_ids:
            conds.append(Order.employee_id.in_(f.employee_ids))
        if f.customer_id is not None:
            conds.append(Order.customer_id == f.customer_id)
        if f.category_ids:
            conds.append(Product.category_id.in_(f.category_ids))
        if f.region_ids:
            conds.append(Store.region_id.in_(f.region_ids))
        if conds:
            stmt = stmt.where(and_(*conds))
        return stmt

    def _to_frame(self, stmt: Select[tuple]) -> pd.DataFrame:
        result = self.session.execute(stmt)
        rows = result.mappings().all()
        if not rows:
            # preserve column names when empty
            cols = list(result.keys())
            return pd.DataFrame(columns=cols)
        return pd.DataFrame([dict(r) for r in rows])
