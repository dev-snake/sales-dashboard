"""PostgreSQL bulk upsert / insert loaders."""

from __future__ import annotations

from typing import Any

from loguru import logger
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models import Customer, Order, OrderItem, Payment, Product


def _chunked(rows: list[dict[str, Any]], size: int) -> list[list[dict[str, Any]]]:
    return [rows[i : i + size] for i in range(0, len(rows), size)]


def upsert_customers(session: Session, rows: list[dict[str, Any]], batch_size: int) -> int:
    if not rows:
        return 0
    loaded = 0
    for batch in _chunked(rows, batch_size):
        stmt = insert(Customer).values(batch)
        stmt = stmt.on_conflict_do_update(
            index_elements=["code"],
            set_={
                "first_name": stmt.excluded.first_name,
                "last_name": stmt.excluded.last_name,
                "email": stmt.excluded.email,
                "phone": stmt.excluded.phone,
                "gender": stmt.excluded.gender,
                "address": stmt.excluded.address,
                "city": stmt.excluded.city,
                "region_id": stmt.excluded.region_id,
                "registered_at": stmt.excluded.registered_at,
                "is_active": stmt.excluded.is_active,
            },
        )
        session.execute(stmt)
        loaded += len(batch)
    session.flush()
    logger.info("Loaded customers | rows={}", loaded)
    return loaded


def upsert_products(session: Session, rows: list[dict[str, Any]], batch_size: int) -> int:
    if not rows:
        return 0
    loaded = 0
    for batch in _chunked(rows, batch_size):
        stmt = insert(Product).values(batch)
        stmt = stmt.on_conflict_do_update(
            index_elements=["sku"],
            set_={
                "name": stmt.excluded.name,
                "category_id": stmt.excluded.category_id,
                "brand_id": stmt.excluded.brand_id,
                "supplier_id": stmt.excluded.supplier_id,
                "unit_price": stmt.excluded.unit_price,
                "cost_price": stmt.excluded.cost_price,
                "description": stmt.excluded.description,
                "is_active": stmt.excluded.is_active,
            },
        )
        session.execute(stmt)
        loaded += len(batch)
    session.flush()
    logger.info("Loaded products | rows={}", loaded)
    return loaded


def upsert_orders(session: Session, rows: list[dict[str, Any]], batch_size: int) -> int:
    if not rows:
        return 0
    loaded = 0
    for batch in _chunked(rows, batch_size):
        stmt = insert(Order).values(batch)
        stmt = stmt.on_conflict_do_update(
            index_elements=["order_number"],
            set_={
                "customer_id": stmt.excluded.customer_id,
                "store_id": stmt.excluded.store_id,
                "employee_id": stmt.excluded.employee_id,
                "promotion_id": stmt.excluded.promotion_id,
                "order_date": stmt.excluded.order_date,
                "status": stmt.excluded.status,
                "subtotal": stmt.excluded.subtotal,
                "discount_amount": stmt.excluded.discount_amount,
                "tax_amount": stmt.excluded.tax_amount,
                "total_amount": stmt.excluded.total_amount,
                "notes": stmt.excluded.notes,
            },
        )
        session.execute(stmt)
        loaded += len(batch)
    session.flush()
    logger.info("Loaded orders | rows={}", loaded)
    return loaded


def replace_order_items(session: Session, rows: list[dict[str, Any]], batch_size: int) -> int:
    """Delete existing items for affected orders, then insert."""
    if not rows:
        return 0
    order_ids = {int(r["order_id"]) for r in rows}
    session.execute(delete(OrderItem).where(OrderItem.order_id.in_(order_ids)))

    # strip helper keys
    clean_rows = [{k: v for k, v in r.items() if not k.startswith("_")} for r in rows]
    loaded = 0
    for batch in _chunked(clean_rows, batch_size):
        session.execute(insert(OrderItem).values(batch))
        loaded += len(batch)
    session.flush()
    logger.info("Loaded order_items | rows={} orders={}", loaded, len(order_ids))
    return loaded


def upsert_payments(session: Session, rows: list[dict[str, Any]], batch_size: int) -> int:
    if not rows:
        return 0
    loaded = 0
    for batch in _chunked(rows, batch_size):
        stmt = insert(Payment).values(batch)
        stmt = stmt.on_conflict_do_update(
            index_elements=["payment_number"],
            set_={
                "order_id": stmt.excluded.order_id,
                "method": stmt.excluded.method,
                "amount": stmt.excluded.amount,
                "status": stmt.excluded.status,
                "paid_at": stmt.excluded.paid_at,
            },
        )
        session.execute(stmt)
        loaded += len(batch)
    session.flush()
    logger.info("Loaded payments | rows={}", loaded)
    return loaded


def load_entity(session: Session, entity: str, rows: list[dict[str, Any]], batch_size: int) -> int:
    if entity == "customers":
        return upsert_customers(session, rows, batch_size)
    if entity == "products":
        return upsert_products(session, rows, batch_size)
    if entity == "orders":
        return upsert_orders(session, rows, batch_size)
    if entity == "order_items":
        return replace_order_items(session, rows, batch_size)
    if entity == "payments":
        return upsert_payments(session, rows, batch_size)
    raise ValueError(f"No loader for entity {entity}")
