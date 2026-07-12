"""Transform validated models → load-ready dicts with FK ids."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from app.etl.transformers.lookups import LookupCache
from app.schemas.customer import CustomerIn
from app.schemas.order import OrderIn, OrderItemIn
from app.schemas.payment import PaymentIn
from app.schemas.product import ProductIn
from app.utils.errors import ETLError


def transform_customers(
    rows: list[CustomerIn],
    lookups: LookupCache,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    ready: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for row in rows:
        region_id = None
        if row.region_code:
            region_id = lookups.regions.get(row.region_code)
            if region_id is None:
                rejected.append(
                    {
                        **row.model_dump(mode="json"),
                        "_errors": f"unknown region_code={row.region_code}",
                    }
                )
                continue
        ready.append(
            {
                "code": row.code,
                "first_name": row.first_name,
                "last_name": row.last_name,
                "email": row.email,
                "phone": row.phone,
                "gender": row.gender,
                "address": row.address,
                "city": row.city,
                "region_id": region_id,
                "registered_at": row.registered_at or datetime.now(UTC),
                "is_active": row.is_active,
            }
        )
    return ready, rejected


def transform_products(
    rows: list[ProductIn],
    lookups: LookupCache,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    ready: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for row in rows:
        cat_id = lookups.categories.get(row.category_code)
        if cat_id is None:
            rejected.append(
                {
                    **row.model_dump(mode="json"),
                    "_errors": f"unknown category_code={row.category_code}",
                }
            )
            continue
        brand_id = None
        if row.brand_code:
            brand_id = lookups.brands.get(row.brand_code)
            if brand_id is None:
                rejected.append(
                    {
                        **row.model_dump(mode="json"),
                        "_errors": f"unknown brand_code={row.brand_code}",
                    }
                )
                continue
        supplier_id = None
        if row.supplier_code:
            supplier_id = lookups.suppliers.get(row.supplier_code)
            if supplier_id is None:
                rejected.append(
                    {
                        **row.model_dump(mode="json"),
                        "_errors": f"unknown supplier_code={row.supplier_code}",
                    }
                )
                continue
        ready.append(
            {
                "sku": row.sku,
                "name": row.name,
                "category_id": cat_id,
                "brand_id": brand_id,
                "supplier_id": supplier_id,
                "unit_price": row.unit_price,
                "cost_price": row.cost_price,
                "description": row.description,
                "is_active": row.is_active,
            }
        )
    return ready, rejected


def transform_orders(
    rows: list[OrderIn],
    lookups: LookupCache,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    ready: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for row in rows:
        customer_id = lookups.customers.get(row.customer_code)
        store_id = lookups.stores.get(row.store_code)
        employee_id = lookups.employees.get(row.employee_code)
        errors: list[str] = []
        if customer_id is None:
            errors.append(f"unknown customer_code={row.customer_code}")
        if store_id is None:
            errors.append(f"unknown store_code={row.store_code}")
        if employee_id is None:
            errors.append(f"unknown employee_code={row.employee_code}")
        if errors:
            rejected.append({**row.model_dump(mode="json"), "_errors": "; ".join(errors)})
            continue
        ready.append(
            {
                "order_number": row.order_number,
                "customer_id": customer_id,
                "store_id": store_id,
                "employee_id": employee_id,
                "promotion_id": None,
                "order_date": row.order_date,
                "status": row.status,
                "subtotal": row.subtotal,
                "discount_amount": row.discount_amount,
                "tax_amount": row.tax_amount,
                "total_amount": row.total_amount,
                "notes": row.notes,
            }
        )
    return ready, rejected


def transform_order_items(
    rows: list[OrderItemIn],
    lookups: LookupCache,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    ready: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for row in rows:
        order_id = lookups.orders.get(row.order_number)
        product_id = lookups.products.get(row.product_sku)
        errors: list[str] = []
        if order_id is None:
            errors.append(f"unknown order_number={row.order_number}")
        if product_id is None:
            errors.append(f"unknown product_sku={row.product_sku}")
        if errors:
            rejected.append({**row.model_dump(mode="json"), "_errors": "; ".join(errors)})
            continue
        line_total = row.line_total
        if line_total is None:
            line_total = Decimal(row.quantity) * row.unit_price - row.discount_amount
        if line_total < 0:
            rejected.append(
                {**row.model_dump(mode="json"), "_errors": "line_total would be negative"}
            )
            continue
        ready.append(
            {
                "order_id": order_id,
                "product_id": product_id,
                "quantity": row.quantity,
                "unit_price": row.unit_price,
                "unit_cost": row.unit_cost,
                "discount_amount": row.discount_amount or Decimal("0"),
                "line_total": line_total,
                "_order_number": row.order_number,  # helper for reload strategy
            }
        )
    return ready, rejected


def transform_payments(
    rows: list[PaymentIn],
    lookups: LookupCache,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    ready: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for row in rows:
        order_id = lookups.orders.get(row.order_number)
        if order_id is None:
            rejected.append(
                {
                    **row.model_dump(mode="json"),
                    "_errors": f"unknown order_number={row.order_number}",
                }
            )
            continue
        ready.append(
            {
                "payment_number": row.payment_number,
                "order_id": order_id,
                "method": row.method,
                "amount": row.amount,
                "status": row.status,
                "paid_at": row.paid_at,
            }
        )
    return ready, rejected


ENTITY_NATURAL_KEY = {
    "customers": "code",
    "products": "sku",
    "orders": "order_number",
    "payments": "payment_number",
}


def require_supported_entity(entity: str) -> str:
    supported = {
        "customers",
        "products",
        "orders",
        "order_items",
        "payments",
    }
    e = entity.strip().lower()
    if e not in supported:
        raise ETLError(
            f"Unsupported entity {entity!r}",
            details={"supported": sorted(supported)},
        )
    return e
