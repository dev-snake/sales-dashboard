"""Export small sample files for ETL demos (no DB required for generation)."""

from __future__ import annotations

import csv
import json
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

from openpyxl import Workbook

from app.config.settings import PROJECT_ROOT
from app.seed.distributions import make_faker, money, seed_all


def _default_samples_dir() -> Path:
    return PROJECT_ROOT / "datasets" / "raw" / "samples"


def export_etl_samples(
    target_dir: Path | None = None,
    *,
    seed: int = 42,
) -> Path:
    """Write CSV/Excel/JSON sample files under datasets/raw/samples/."""
    seed_all(seed)
    fake = make_faker("en_US", seed)
    out = target_dir or _default_samples_dir()
    out.mkdir(parents=True, exist_ok=True)

    customers = _sample_customers(fake, 50)
    products = _sample_products(fake, 30)
    orders, items = _sample_orders(fake, 20, product_count=30, customer_count=50)
    payments = _sample_payments(orders)

    _write_csv(out / "customers.csv", customers)
    _write_excel(out / "products.xlsx", "products", products)
    _write_csv(out / "orders.csv", orders)
    _write_csv(out / "order_items.csv", items)
    (out / "payments.json").write_text(
        json.dumps(payments, indent=2, default=str),
        encoding="utf-8",
    )
    return out


def _sample_customers(fake: Any, n: int) -> list[dict[str, Any]]:
    rows = []
    for i in range(n):
        rows.append(
            {
                "code": f"CUS-SAMP-{i + 1:04d}",
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "email": f"sample.customer{i + 1}@example.com",
                "phone": f"090{i + 1:07d}",
                "city": fake.city(),
                "region_code": "REG-R01",
                "registered_at": (datetime.now(UTC) - timedelta(days=30 + i)).isoformat(),
            }
        )
    return rows


def _sample_products(fake: Any, n: int) -> list[dict[str, Any]]:
    rows = []
    for i in range(n):
        price = money(50_000 + i * 10_000)
        rows.append(
            {
                "sku": f"SKU-SAMP-{i + 1:05d}",
                "name": f"Sample Product {i + 1}",
                "category_code": "CAT-R01",
                "brand_code": "BR-0001",
                "supplier_code": "SUP-0001",
                "unit_price": str(price),
                "cost_price": str(money(float(price) * 0.7)),
                "is_active": True,
            }
        )
    return rows


def _sample_orders(
    fake: Any,
    n_orders: int,
    *,
    product_count: int,
    customer_count: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    orders: list[dict[str, Any]] = []
    items: list[dict[str, Any]] = []
    for i in range(n_orders):
        order_number = f"ORD-SAMP-{i + 1:05d}"
        orders.append(
            {
                "order_number": order_number,
                "customer_code": f"CUS-SAMP-{(i % customer_count) + 1:04d}",
                "store_code": "ST-HN-001",
                "employee_code": "EMP-MGR-0001",
                "order_date": (date.today() - timedelta(days=i)).isoformat(),
                "status": "completed" if i % 10 else "paid",
                "subtotal": "0",
                "discount_amount": "0",
                "tax_amount": "0",
                "total_amount": "0",
            }
        )
        for j in range(1 + (i % 3)):
            sku = f"SKU-SAMP-{((i + j) % product_count) + 1:05d}"
            qty = 1 + (j % 3)
            unit_price = Decimal(50_000 + (i + j) * 1000)
            line_total = unit_price * qty
            items.append(
                {
                    "order_number": order_number,
                    "product_sku": sku,
                    "quantity": qty,
                    "unit_price": str(unit_price),
                    "unit_cost": str(money(float(unit_price) * 0.7)),
                    "discount_amount": "0",
                    "line_total": str(line_total),
                }
            )
    return orders, items


def _sample_payments(orders: list[dict[str, Any]]) -> list[dict[str, Any]]:
    methods = ["cash", "card", "transfer", "e_wallet"]
    rows = []
    for i, order in enumerate(orders):
        rows.append(
            {
                "payment_number": f"PAY-SAMP-{i + 1:05d}",
                "order_number": order["order_number"],
                "method": methods[i % len(methods)],
                "amount": "150000.00",
                "status": "completed",
                "paid_at": datetime.now(UTC).isoformat(),
            }
        )
    return rows


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _write_excel(path: Path, sheet_name: str, rows: list[dict[str, Any]]) -> None:
    wb = Workbook()
    ws = wb.active
    assert ws is not None
    ws.title = sheet_name
    if not rows:
        wb.save(path)
        return
    headers = list(rows[0].keys())
    ws.append(headers)
    for row in rows:
        ws.append([row[h] for h in headers])
    wb.save(path)
