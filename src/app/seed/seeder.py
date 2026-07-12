"""Core seed orchestrator: generate + load synthetic retail data."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import Any

import numpy as np
from loguru import logger
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import (
    Brand,
    Calendar,
    Category,
    Customer,
    Employee,
    Inventory,
    Order,
    OrderItem,
    Payment,
    Product,
    Promotion,
    Region,
    Return,
    StockMovement,
    Store,
    Supplier,
)
from app.seed.bulk import bulk_insert
from app.seed.calendar_gen import build_calendar_rows
from app.seed.distributions import (
    CATEGORY_NAMES,
    CITY_REGION_HINTS,
    GENDER_CHOICES,
    ORDER_STATUS_WEIGHTS,
    PAYMENT_METHOD_WEIGHTS,
    RETURN_REASON_WEIGHTS,
    build_weighted_dates,
    cost_from_price,
    lognormal_price,
    make_faker,
    money,
    pick_index,
    poisson_clipped,
    power_law_weights,
    sample_order_datetime,
    seed_all,
    weighted_choice,
)
from app.seed.scale_config import ScaleConfig

# Truncate order: children first is handled by CASCADE
TRUNCATE_TABLES = (
    "returns",
    "payments",
    "order_items",
    "orders",
    "stock_movements",
    "inventory",
    "products",
    "promotions",
    "customers",
    "employees",
    "stores",
    "categories",
    "brands",
    "suppliers",
    "regions",
    "calendar",
)


@dataclass
class SeedResult:
    scale: str
    counts: dict[str, int] = field(default_factory=dict)
    duration_seconds: float = 0.0


@dataclass
class _IdMaps:
    region_ids: list[int] = field(default_factory=list)
    store_ids: list[int] = field(default_factory=list)
    employee_ids: list[int] = field(default_factory=list)
    # employee_id -> store_id
    employee_store: dict[int, int] = field(default_factory=dict)
    # store_id -> list[employee_id]
    store_employees: dict[int, list[int]] = field(default_factory=dict)
    customer_ids: list[int] = field(default_factory=list)
    supplier_ids: list[int] = field(default_factory=list)
    brand_ids: list[int] = field(default_factory=list)
    category_ids: list[int] = field(default_factory=list)
    product_ids: list[int] = field(default_factory=list)
    product_prices: dict[int, tuple[Decimal, Decimal]] = field(default_factory=dict)
    promotion_ids: list[int] = field(default_factory=list)


class DatabaseSeeder:
    """Generate and insert seed data for a given scale."""

    def __init__(
        self,
        session: Session,
        config: ScaleConfig,
        *,
        seed: int = 42,
        locale: str = "vi_VN",
        tax_rate: float | None = None,
    ) -> None:
        self.session = session
        self.config = config
        self.seed = seed
        self.locale = locale
        settings = get_settings()
        self.tax_rate = tax_rate if tax_rate is not None else settings.tax_rate
        self.rng = np.random.default_rng(seed)
        self.fake = make_faker(locale, seed)
        self.ids = _IdMaps()
        self.batch_size = config.batch_size

    def reset(self) -> None:
        """TRUNCATE all business tables (destructive)."""
        logger.warning("Truncating all seed tables (CASCADE, RESTART IDENTITY)")
        table_list = ", ".join(TRUNCATE_TABLES)
        self.session.execute(text(f"TRUNCATE TABLE {table_list} RESTART IDENTITY CASCADE"))
        self.session.commit()

    def run(self, *, reset: bool = False) -> SeedResult:
        import time

        seed_all(self.seed)
        self.rng = np.random.default_rng(self.seed)
        self.fake = make_faker(self.locale, self.seed)
        self.ids = _IdMaps()

        started = time.perf_counter()
        if reset:
            self.reset()

        counts: dict[str, int] = {}
        counts["calendar"] = self._seed_calendar()
        counts["regions"] = self._seed_regions()
        counts["stores"] = self._seed_stores()
        counts["employees"] = self._seed_employees()
        counts["suppliers"] = self._seed_suppliers()
        counts["brands"] = self._seed_brands()
        counts["categories"] = self._seed_categories()
        counts["products"] = self._seed_products()
        counts["customers"] = self._seed_customers()
        counts["promotions"] = self._seed_promotions()
        order_counts = self._seed_orders_and_related()
        counts.update(order_counts)
        counts["inventory"] = self._seed_inventory()

        self.session.commit()
        duration = time.perf_counter() - started
        logger.info(
            "Seed complete | scale={} duration={:.1f}s counts={}",
            self.config.name,
            duration,
            counts,
        )
        return SeedResult(scale=self.config.name, counts=counts, duration_seconds=duration)

    # ------------------------------------------------------------------
    # Masters
    # ------------------------------------------------------------------

    def _seed_calendar(self) -> int:
        # Skip if already populated (no reset)
        existing = self.session.execute(text("SELECT COUNT(*) FROM calendar")).scalar_one()
        if existing and existing > 0:
            logger.info("Calendar already has {} rows — skip", existing)
            return int(existing)

        rows = build_calendar_rows()
        bulk_insert(self.session, Calendar, rows, batch_size=self.batch_size)
        self.session.commit()
        return len(rows)

    def _seed_regions(self) -> int:
        n = self.config.regions
        rows: list[dict[str, Any]] = []
        # Root regions first
        roots = min(3, n)
        for i in range(roots):
            code = f"REG-R{i + 1:02d}"
            name = ("North", "Central", "South")[i] if i < 3 else f"Region Root {i + 1}"
            rows.append(
                {
                    "code": code,
                    "name": name,
                    "parent_id": None,
                    "level": 1,
                }
            )
        root_ids = bulk_insert(
            self.session, Region, rows, batch_size=self.batch_size, returning_id=True
        )
        self.session.flush()

        child_rows: list[dict[str, Any]] = []
        for i in range(roots, n):
            parent = root_ids[i % len(root_ids)]
            hint = CITY_REGION_HINTS[i % len(CITY_REGION_HINTS)]
            child_rows.append(
                {
                    "code": f"REG-{hint[1]}-{i + 1:02d}",
                    "name": f"{hint[0]} Area {i + 1}",
                    "parent_id": parent,
                    "level": 2,
                }
            )
        child_ids = bulk_insert(
            self.session, Region, child_rows, batch_size=self.batch_size, returning_id=True
        )
        self.ids.region_ids = root_ids + child_ids
        self.session.commit()
        return len(self.ids.region_ids)

    def _seed_stores(self) -> int:
        n = self.config.stores
        rows: list[dict[str, Any]] = []
        for i in range(n):
            region_id = self.ids.region_ids[i % len(self.ids.region_ids)]
            city, code = CITY_REGION_HINTS[i % len(CITY_REGION_HINTS)]
            rows.append(
                {
                    "code": f"ST-{code}-{i + 1:03d}",
                    "name": f"RetailCo {city} #{i + 1}",
                    "region_id": region_id,
                    "address": self.fake.street_address(),
                    "city": city,
                    "phone": self._phone(),
                    "opened_at": date.today() - timedelta(days=int(self.rng.integers(365, 3650))),
                    "is_active": True,
                }
            )
        self.ids.store_ids = bulk_insert(
            self.session, Store, rows, batch_size=self.batch_size, returning_id=True
        )
        self.session.commit()
        return len(self.ids.store_ids)

    def _seed_employees(self) -> int:
        n = self.config.employees
        stores = self.ids.store_ids
        # At least 1 manager per store
        managers: list[dict[str, Any]] = []
        for i, store_id in enumerate(stores):
            managers.append(
                {
                    "code": f"EMP-MGR-{i + 1:04d}",
                    "first_name": self.fake.first_name(),
                    "last_name": self.fake.last_name(),
                    "email": f"manager{i + 1}@retailco.example",
                    "phone": self._phone(),
                    "store_id": store_id,
                    "manager_id": None,
                    "job_title": "Store Manager",
                    "hire_date": date.today() - timedelta(days=int(self.rng.integers(800, 4000))),
                    "is_active": True,
                }
            )
        manager_ids = bulk_insert(
            self.session, Employee, managers, batch_size=self.batch_size, returning_id=True
        )
        store_manager = dict(zip(stores, manager_ids, strict=True))

        remaining = max(0, n - len(managers))
        associates: list[dict[str, Any]] = []
        for i in range(remaining):
            store_id = stores[i % len(stores)]
            associates.append(
                {
                    "code": f"EMP-AS-{i + 1:05d}",
                    "first_name": self.fake.first_name(),
                    "last_name": self.fake.last_name(),
                    "email": f"assoc{i + 1}@retailco.example" if self.rng.random() < 0.9 else None,
                    "phone": self._phone() if self.rng.random() < 0.85 else None,
                    "store_id": store_id,
                    "manager_id": store_manager[store_id],
                    "job_title": "Sales Associate",
                    "hire_date": date.today() - timedelta(days=int(self.rng.integers(30, 2500))),
                    "is_active": bool(self.rng.random() > 0.05),
                }
            )
        assoc_ids = bulk_insert(
            self.session, Employee, associates, batch_size=self.batch_size, returning_id=True
        )

        all_ids = manager_ids + assoc_ids
        self.ids.employee_ids = all_ids
        self.ids.employee_store.clear()
        self.ids.store_employees = {sid: [] for sid in stores}
        for row, eid in zip(managers, manager_ids, strict=True):
            self.ids.employee_store[eid] = row["store_id"]
            self.ids.store_employees[row["store_id"]].append(eid)
        for row, eid in zip(associates, assoc_ids, strict=True):
            self.ids.employee_store[eid] = row["store_id"]
            self.ids.store_employees[row["store_id"]].append(eid)

        self.session.commit()
        return len(all_ids)

    def _seed_suppliers(self) -> int:
        rows = []
        for i in range(self.config.suppliers):
            rows.append(
                {
                    "code": f"SUP-{i + 1:04d}",
                    "name": f"{self.fake.company()} Supply",
                    "contact_name": self.fake.name(),
                    "email": f"supplier{i + 1}@example.com",
                    "phone": self._phone(),
                    "address": self.fake.address().replace("\n", ", "),
                    "rating": money(float(self.rng.uniform(2.5, 5.0))),
                    "is_active": True,
                }
            )
        self.ids.supplier_ids = bulk_insert(
            self.session, Supplier, rows, batch_size=self.batch_size, returning_id=True
        )
        self.session.commit()
        return len(self.ids.supplier_ids)

    def _seed_brands(self) -> int:
        rows = []
        for i in range(self.config.brands):
            name = f"{self.fake.company()} Brand {i + 1}"
            rows.append(
                {
                    "code": f"BR-{i + 1:04d}",
                    "name": name[:150],
                    "country": self.fake.country()[:100],
                }
            )
        self.ids.brand_ids = bulk_insert(
            self.session, Brand, rows, batch_size=self.batch_size, returning_id=True
        )
        self.session.commit()
        return len(self.ids.brand_ids)

    def _seed_categories(self) -> int:
        n = self.config.categories
        roots_n = min(6, n)
        root_rows = []
        for i in range(roots_n):
            name = CATEGORY_NAMES[i % len(CATEGORY_NAMES)]
            root_rows.append(
                {
                    "code": f"CAT-R{i + 1:02d}",
                    "name": name,
                    "parent_id": None,
                    "description": f"Root category {name}",
                }
            )
        root_ids = bulk_insert(
            self.session, Category, root_rows, batch_size=self.batch_size, returning_id=True
        )
        child_rows = []
        for i in range(roots_n, n):
            parent = root_ids[i % len(root_ids)]
            name = CATEGORY_NAMES[i % len(CATEGORY_NAMES)]
            child_rows.append(
                {
                    "code": f"CAT-C{i + 1:03d}",
                    "name": f"{name} Sub {i + 1}",
                    "parent_id": parent,
                    "description": f"Subcategory of {name}",
                }
            )
        child_ids = bulk_insert(
            self.session, Category, child_rows, batch_size=self.batch_size, returning_id=True
        )
        self.ids.category_ids = root_ids + child_ids
        self.session.commit()
        return len(self.ids.category_ids)

    def _seed_products(self) -> int:
        n = self.config.products
        rows = []
        for i in range(n):
            cat_id = self.ids.category_ids[i % len(self.ids.category_ids)]
            brand_id = self.ids.brand_ids[i % len(self.ids.brand_ids)]
            supplier_id = self.ids.supplier_ids[i % len(self.ids.supplier_ids)]
            unit_price = lognormal_price(self.rng)
            cost_price = cost_from_price(unit_price, self.rng)
            sku = f"SKU-{cat_id:03d}-{brand_id:03d}-{i + 1:06d}"
            rows.append(
                {
                    "sku": sku,
                    "name": f"{self.fake.word().title()} {self.fake.color_name()} {i + 1}",
                    "category_id": cat_id,
                    "brand_id": brand_id,
                    "supplier_id": supplier_id,
                    "unit_price": unit_price,
                    "cost_price": cost_price,
                    "description": self.fake.sentence(),
                    "is_active": bool(self.rng.random() > 0.10),
                }
            )
        self.ids.product_ids = bulk_insert(
            self.session, Product, rows, batch_size=self.batch_size, returning_id=True
        )
        for row, pid in zip(rows, self.ids.product_ids, strict=True):
            unit_price = Decimal(str(row["unit_price"]))
            cost_price = Decimal(str(row["cost_price"]))
            self.ids.product_prices[pid] = (unit_price, cost_price)
        self.session.commit()
        return len(self.ids.product_ids)

    def _seed_customers(self) -> int:
        n = self.config.customers
        rows = []
        for i in range(n):
            has_email = self.rng.random() < 0.60
            has_phone = self.rng.random() < 0.80
            region_id = self.ids.region_ids[i % len(self.ids.region_ids)]
            registered = datetime.now(UTC) - timedelta(
                days=int(self.rng.integers(30, self.config.months_history * 30 + 60))
            )
            rows.append(
                {
                    "code": f"CUS-{i + 1:07d}",
                    "first_name": self.fake.first_name(),
                    "last_name": self.fake.last_name(),
                    "email": f"customer{i + 1}@example.com" if has_email else None,
                    "phone": self._phone() if has_phone else None,
                    "gender": str(self.rng.choice(GENDER_CHOICES)),
                    "birth_date": date.today()
                    - timedelta(days=int(self.rng.integers(18 * 365, 70 * 365))),
                    "address": self.fake.street_address(),
                    "city": CITY_REGION_HINTS[i % len(CITY_REGION_HINTS)][0],
                    "region_id": region_id,
                    "registered_at": registered,
                    "is_active": True,
                }
            )
        self.ids.customer_ids = bulk_insert(
            self.session, Customer, rows, batch_size=self.batch_size, returning_id=True
        )
        self.session.commit()
        return len(self.ids.customer_ids)

    def _seed_promotions(self) -> int:
        rows = []
        start_base = self.config.order_start_date
        for i in range(self.config.promotions):
            is_percent = self.rng.random() < 0.7
            discount_type = "percent" if is_percent else "fixed"
            if is_percent:
                discount_value = money(float(self.rng.choice([5, 10, 15, 20, 25, 30])))
            else:
                discount_value = money(float(self.rng.choice([10_000, 20_000, 50_000, 100_000])))
            start = start_base + timedelta(days=int(self.rng.integers(0, 90)))
            end = start + timedelta(days=int(self.rng.integers(14, 120)))
            rows.append(
                {
                    "code": f"PROMO-{i + 1:04d}",
                    "name": f"Promo Campaign {i + 1}",
                    "discount_type": discount_type,
                    "discount_value": discount_value,
                    "min_order_amount": money(100_000) if self.rng.random() < 0.5 else None,
                    "start_date": start,
                    "end_date": end,
                    "is_active": True,
                }
            )
        self.ids.promotion_ids = bulk_insert(
            self.session, Promotion, rows, batch_size=self.batch_size, returning_id=True
        )
        self.session.commit()
        return len(self.ids.promotion_ids)

    # ------------------------------------------------------------------
    # Facts
    # ------------------------------------------------------------------

    def _seed_orders_and_related(self) -> dict[str, int]:
        cfg = self.config
        n_orders = cfg.orders
        dates, date_weights = build_weighted_dates(
            cfg.order_start_date, cfg.order_end_date, self.rng
        )

        customer_weights = power_law_weights(len(self.ids.customer_ids), alpha=1.4)
        product_weights = power_law_weights(len(self.ids.product_ids), alpha=1.3)

        total_orders = 0
        total_items = 0
        total_payments = 0
        total_returns = 0
        total_movements = 0

        chunk = min(cfg.batch_size, 5_000)
        order_seq = 0
        pay_seq = 0
        ret_seq = 0

        for start in range(0, n_orders, chunk):
            end = min(start + chunk, n_orders)
            batch_n = end - start

            order_rows: list[dict[str, Any]] = []
            pending_items: list[list[dict[str, Any]]] = []
            pending_meta: list[dict[str, Any]] = []

            for _ in range(batch_n):
                order_seq += 1
                store_id = int(self.rng.choice(self.ids.store_ids))
                emp_list = self.ids.store_employees[store_id]
                employee_id = int(self.rng.choice(emp_list))
                customer_id = self.ids.customer_ids[pick_index(customer_weights, self.rng)]
                status = weighted_choice(ORDER_STATUS_WEIGHTS)
                order_dt = sample_order_datetime(dates, date_weights, self.rng)
                promotion_id = None
                if self.rng.random() < 0.10 and self.ids.promotion_ids:
                    promotion_id = int(self.rng.choice(self.ids.promotion_ids))

                n_lines = poisson_clipped(self.rng, 2.5, 1, 12)
                line_defs: list[dict[str, Any]] = []
                subtotal = Decimal("0.00")
                for _ln in range(n_lines):
                    pid = self.ids.product_ids[pick_index(product_weights, self.rng)]
                    unit_price, unit_cost = self.ids.product_prices[pid]
                    noise = Decimal(str(round(1 + float(self.rng.uniform(-0.02, 0.02)), 4)))
                    snap_price = money(float(unit_price * noise))
                    qty = int(self.rng.integers(1, 5))
                    line_discount = Decimal("0.00")
                    if self.rng.random() < 0.30:
                        line_discount = money(
                            float(snap_price) * qty * float(self.rng.uniform(0.02, 0.10))
                        )
                    line_total = money(float(snap_price) * qty - float(line_discount))
                    if line_total < 0:
                        line_total = Decimal("0.00")
                    subtotal += line_total
                    line_defs.append(
                        {
                            "product_id": pid,
                            "quantity": qty,
                            "unit_price": snap_price,
                            "unit_cost": unit_cost,
                            "discount_amount": line_discount,
                            "line_total": line_total,
                        }
                    )

                header_discount = Decimal("0.00")
                if promotion_id is not None and self.rng.random() < 0.5:
                    header_discount = money(float(subtotal) * 0.05)
                taxable = subtotal - header_discount
                tax_amount = money(float(taxable) * self.tax_rate)
                total_amount = money(float(taxable + tax_amount))

                order_rows.append(
                    {
                        "order_number": f"ORD-{order_seq:09d}",
                        "customer_id": customer_id,
                        "store_id": store_id,
                        "employee_id": employee_id,
                        "promotion_id": promotion_id,
                        "order_date": order_dt,
                        "status": status,
                        "subtotal": subtotal,
                        "discount_amount": header_discount,
                        "tax_amount": tax_amount,
                        "total_amount": total_amount,
                        "notes": None,
                    }
                )
                pending_items.append(line_defs)
                pending_meta.append(
                    {
                        "status": status,
                        "store_id": store_id,
                        "total_amount": total_amount,
                        "order_date": order_dt,
                    }
                )

            order_ids = bulk_insert(
                self.session,
                Order,
                order_rows,
                batch_size=self.batch_size,
                returning_id=True,
            )
            total_orders += len(order_ids)

            item_rows: list[dict[str, Any]] = []
            for oid, lines, _meta in zip(order_ids, pending_items, pending_meta, strict=True):
                for line in lines:
                    item_rows.append({"order_id": oid, **line})

            item_ids = bulk_insert(
                self.session,
                OrderItem,
                item_rows,
                batch_size=self.batch_size,
                returning_id=True,
            )
            total_items += len(item_ids)

            return_candidates: list[dict[str, Any]] = []
            idx = 0
            for oid, lines, meta in zip(order_ids, pending_items, pending_meta, strict=True):
                for line in lines:
                    iid = item_ids[idx]
                    idx += 1
                    if meta["status"] in ("paid", "completed"):
                        return_candidates.append(
                            {
                                "order_item_id": iid,
                                "order_id": oid,
                                "store_id": meta["store_id"],
                                "quantity": line["quantity"],
                                "line_total": line["line_total"],
                                "product_id": line["product_id"],
                                "order_date": meta["order_date"],
                            }
                        )

            # Payments
            payment_rows: list[dict[str, Any]] = []
            for oid, meta in zip(order_ids, pending_meta, strict=True):
                if meta["status"] not in ("paid", "completed"):
                    continue
                multi = self.rng.random() < 0.05
                total = meta["total_amount"]
                if multi and float(total) > 0:
                    share = money(float(total) * float(self.rng.uniform(0.3, 0.7)))
                    rest = money(float(total) - float(share))
                    amounts = [share, rest]
                else:
                    amounts = [total]
                for amt in amounts:
                    if float(amt) <= 0:
                        continue
                    pay_seq += 1
                    payment_rows.append(
                        {
                            "payment_number": f"PAY-{pay_seq:09d}",
                            "order_id": oid,
                            "method": weighted_choice(PAYMENT_METHOD_WEIGHTS),
                            "amount": amt,
                            "status": "completed",
                            "paid_at": meta["order_date"]
                            + timedelta(minutes=int(self.rng.integers(1, 120))),
                        }
                    )
            bulk_insert(self.session, Payment, payment_rows, batch_size=self.batch_size)
            total_payments += len(payment_rows)

            # Stock movements sale_out for completed/paid
            movement_rows: list[dict[str, Any]] = []
            for oid, lines, meta in zip(order_ids, pending_items, pending_meta, strict=True):
                if meta["status"] not in ("paid", "completed"):
                    continue
                for line in lines:
                    movement_rows.append(
                        {
                            "store_id": meta["store_id"],
                            "product_id": line["product_id"],
                            "movement_type": "sale_out",
                            "quantity": -int(line["quantity"]),
                            "reference_type": "order",
                            "reference_id": oid,
                            "note": "seed sale",
                            "moved_at": meta["order_date"],
                        }
                    )
            # purchase_in baseline movements
            for mr in list(movement_rows):
                if self.rng.random() < 0.35:
                    movement_rows.append(
                        {
                            "store_id": mr["store_id"],
                            "product_id": mr["product_id"],
                            "movement_type": "purchase_in",
                            "quantity": int(self.rng.integers(5, 40)),
                            "reference_type": "purchase",
                            "reference_id": None,
                            "note": "seed purchase",
                            "moved_at": mr["moved_at"]
                            - timedelta(days=int(self.rng.integers(1, 30))),
                        }
                    )
            bulk_insert(self.session, StockMovement, movement_rows, batch_size=self.batch_size)
            total_movements += len(movement_rows)

            # Returns ~3% of return candidates
            return_rows: list[dict[str, Any]] = []
            for cand in return_candidates:
                if self.rng.random() > 0.03:
                    continue
                max_qty = int(cand["quantity"])
                qty = int(self.rng.integers(1, max_qty + 1))
                refund = money(float(cand["line_total"]) * (qty / max_qty))
                ret_seq += 1
                return_rows.append(
                    {
                        "return_number": f"RET-{ret_seq:09d}",
                        "order_id": cand["order_id"],
                        "order_item_id": cand["order_item_id"],
                        "store_id": cand["store_id"],
                        "quantity": qty,
                        "reason": weighted_choice(RETURN_REASON_WEIGHTS),
                        "refund_amount": refund,
                        "status": str(
                            self.rng.choice(
                                ["requested", "approved", "completed"], p=[0.2, 0.3, 0.5]
                            )
                        ),
                        "returned_at": cand["order_date"]
                        + timedelta(days=int(self.rng.integers(1, 21))),
                    }
                )
            bulk_insert(self.session, Return, return_rows, batch_size=self.batch_size)
            total_returns += len(return_rows)

            self.session.commit()
            logger.info(
                "Orders progress {}/{} | items+={} payments+={} returns+={}",
                end,
                n_orders,
                len(item_rows),
                len(payment_rows),
                len(return_rows),
            )

        return {
            "orders": total_orders,
            "order_items": total_items,
            "payments": total_payments,
            "returns": total_returns,
            "stock_movements": total_movements,
        }

    def _seed_inventory(self) -> int:
        rows: list[dict[str, Any]] = []
        for store_id in self.ids.store_ids:
            for pid in self.ids.product_ids:
                if self.rng.random() > 0.70:
                    continue  # sparse 70% filled
                reorder = int(self.rng.integers(5, 25))
                # 5% low stock
                if self.rng.random() < 0.05:
                    qty = int(self.rng.integers(0, reorder + 1))
                else:
                    # heavy-tailed
                    qty = int(min(5000, self.rng.pareto(1.5) * 20 + reorder + 5))
                max_level = reorder * int(self.rng.integers(4, 12))
                rows.append(
                    {
                        "store_id": store_id,
                        "product_id": pid,
                        "quantity_on_hand": qty,
                        "reorder_level": reorder,
                        "max_level": max_level,
                    }
                )
        bulk_insert(self.session, Inventory, rows, batch_size=self.batch_size)
        self.session.commit()
        return len(rows)

    def _phone(self) -> str:
        return f"09{self.rng.integers(10000000, 99999999)}"
