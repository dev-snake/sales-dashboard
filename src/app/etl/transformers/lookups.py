"""FK code → id lookups and sample master ensure."""

from __future__ import annotations

from datetime import date

from loguru import logger
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models import Brand, Category, Customer, Employee, Order, Product, Region, Store, Supplier


class LookupCache:
    """Session-scoped natural key → id maps."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.regions: dict[str, int] = {}
        self.stores: dict[str, int] = {}
        self.employees: dict[str, int] = {}
        self.customers: dict[str, int] = {}
        self.categories: dict[str, int] = {}
        self.brands: dict[str, int] = {}
        self.suppliers: dict[str, int] = {}
        self.products: dict[str, int] = {}
        self.orders: dict[str, int] = {}
        self.refresh()

    def refresh(self) -> None:
        self.regions = {
            r.code: r.id for r in self.session.scalars(select(Region)).all() if r.deleted_at is None
        }
        self.stores = {
            s.code: s.id for s in self.session.scalars(select(Store)).all() if s.deleted_at is None
        }
        self.employees = {
            e.code: e.id
            for e in self.session.scalars(select(Employee)).all()
            if e.deleted_at is None
        }
        self.customers = {
            c.code: c.id
            for c in self.session.scalars(select(Customer)).all()
            if c.deleted_at is None
        }
        self.categories = {
            c.code: c.id
            for c in self.session.scalars(select(Category)).all()
            if c.deleted_at is None
        }
        self.brands = {
            b.code: b.id for b in self.session.scalars(select(Brand)).all() if b.deleted_at is None
        }
        self.suppliers = {
            s.code: s.id
            for s in self.session.scalars(select(Supplier)).all()
            if s.deleted_at is None
        }
        self.products = {
            p.sku: p.id for p in self.session.scalars(select(Product)).all() if p.deleted_at is None
        }
        self.orders = {o.order_number: o.id for o in self.session.scalars(select(Order)).all()}


def ensure_sample_masters(session: Session) -> None:
    """Upsert minimal masters required by datasets/raw/samples files."""
    # Region
    session.execute(
        insert(Region)
        .values(code="REG-R01", name="North", parent_id=None, level=1)
        .on_conflict_do_update(index_elements=["code"], set_={"name": "North", "level": 1})
    )
    session.flush()
    region_id = session.scalars(select(Region.id).where(Region.code == "REG-R01")).one()

    session.execute(
        insert(Store)
        .values(
            code="ST-HN-001",
            name="RetailCo Ha Noi #1",
            region_id=region_id,
            city="Ha Noi",
            is_active=True,
            opened_at=date(2020, 1, 1),
        )
        .on_conflict_do_update(
            index_elements=["code"],
            set_={"name": "RetailCo Ha Noi #1", "region_id": region_id, "city": "Ha Noi"},
        )
    )
    session.flush()
    store_id = session.scalars(select(Store.id).where(Store.code == "ST-HN-001")).one()

    session.execute(
        insert(Employee)
        .values(
            code="EMP-MGR-0001",
            first_name="Sample",
            last_name="Manager",
            email="manager.sample@retailco.example",
            store_id=store_id,
            manager_id=None,
            job_title="Store Manager",
            hire_date=date(2020, 1, 1),
            is_active=True,
        )
        .on_conflict_do_update(
            index_elements=["code"],
            set_={"store_id": store_id, "job_title": "Store Manager", "is_active": True},
        )
    )

    session.execute(
        insert(Category)
        .values(code="CAT-R01", name="Electronics", parent_id=None, description="Sample root")
        .on_conflict_do_update(index_elements=["code"], set_={"name": "Electronics"})
    )
    session.execute(
        insert(Brand)
        .values(code="BR-0001", name="Sample Brand 1", country="Vietnam")
        .on_conflict_do_update(index_elements=["code"], set_={"name": "Sample Brand 1"})
    )
    session.execute(
        insert(Supplier)
        .values(
            code="SUP-0001",
            name="Sample Supplier 1",
            is_active=True,
        )
        .on_conflict_do_update(index_elements=["code"], set_={"name": "Sample Supplier 1"})
    )
    session.commit()
    logger.info("Ensured sample master data (region/store/employee/category/brand/supplier)")
