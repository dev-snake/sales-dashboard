"""Unit tests for ORM model metadata (no database required)."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, UniqueConstraint

from app.models import (
    UPDATED_AT_TABLES,
    Base,
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
from app.models.mixins import SoftDeleteMixin, TimestampMixin

EXPECTED_TABLES = {
    "regions",
    "stores",
    "employees",
    "customers",
    "suppliers",
    "brands",
    "categories",
    "products",
    "promotions",
    "orders",
    "order_items",
    "payments",
    "inventory",
    "stock_movements",
    "returns",
    "calendar",
}


def test_all_tables_registered() -> None:
    assert set(Base.metadata.tables.keys()) == EXPECTED_TABLES


def test_table_count() -> None:
    assert len(Base.metadata.tables) == 16


def test_updated_at_tables_exclude_calendar() -> None:
    assert "calendar" not in UPDATED_AT_TABLES
    assert set(UPDATED_AT_TABLES) == EXPECTED_TABLES - {"calendar"}


def test_soft_delete_mixin_on_masters() -> None:
    masters = (
        Region,
        Store,
        Employee,
        Customer,
        Supplier,
        Brand,
        Category,
        Product,
        Promotion,
    )
    for model in masters:
        assert issubclass(model, SoftDeleteMixin)
        assert issubclass(model, TimestampMixin)
        assert "deleted_at" in model.__table__.c


def test_orders_have_no_soft_delete() -> None:
    assert "deleted_at" not in Order.__table__.c
    assert issubclass(Order, TimestampMixin)


def test_calendar_pk_not_serial_identity() -> None:
    col = Calendar.__table__.c.date_id
    assert col.primary_key
    assert col.autoincrement is False or col.autoincrement == "auto"
    # Design: natural key YYYYMMDD, no sequence required
    assert "full_date" in Calendar.__table__.c


def test_order_items_cascade_fk() -> None:
    fks = list(OrderItem.__table__.foreign_key_constraints)
    order_fk = next(fk for fk in fks if any(c.name == "order_id" for c in fk.columns))
    assert order_fk.ondelete == "CASCADE"


def test_inventory_unique_store_product() -> None:
    uniques = [u for u in Inventory.__table__.constraints if isinstance(u, UniqueConstraint)]
    assert any({c.name for c in u.columns} == {"store_id", "product_id"} for u in uniques)


def test_self_fk_regions_and_employees() -> None:
    region_fks = {fk.target_fullname for fk in Region.__table__.foreign_keys}
    assert any(t.startswith("regions") for t in region_fks)

    emp_targets = {fk.target_fullname for fk in Employee.__table__.foreign_keys}
    assert any(t.startswith("employees") for t in emp_targets)
    assert any(t.startswith("stores") for t in emp_targets)


def test_check_constraints_present() -> None:
    order_checks = [
        c.name for c in Order.__table__.constraints if isinstance(c, CheckConstraint) and c.name
    ]
    assert "ck_orders_status" in order_checks

    promo_checks = [
        c.name for c in Promotion.__table__.constraints if isinstance(c, CheckConstraint) and c.name
    ]
    assert "ck_promotions_percent_max" in promo_checks


def test_soft_delete_property() -> None:
    region = Region(code="N", name="North", level=1)
    assert region.is_deleted is False
    region.deleted_at = datetime.now(UTC)
    assert region.is_deleted is True


def test_model_exports() -> None:
    # Ensure public exports stay importable
    assert Brand.__tablename__ == "brands"
    assert Payment.__tablename__ == "payments"
    assert Return.__tablename__ == "returns"
    assert StockMovement.__tablename__ == "stock_movements"
    assert Customer.__tablename__ == "customers"
    assert Product.__tablename__ == "products"
    assert Store.__tablename__ == "stores"
    assert Supplier.__tablename__ == "suppliers"
    assert Category.__tablename__ == "categories"
    assert OrderItem.__tablename__ == "order_items"


def test_foreign_keys_count_reasonable() -> None:
    fk_count = sum(
        1
        for table in Base.metadata.tables.values()
        for _ in table.foreign_key_constraints
        if isinstance(_, ForeignKeyConstraint)
    )
    assert fk_count >= 20
