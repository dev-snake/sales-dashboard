"""Integration: schema / tables present."""

from __future__ import annotations

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

pytestmark = pytest.mark.integration


def test_tables_exist(db_engine: Engine | None) -> None:
    if db_engine is None:
        pytest.skip("no database")
    names = set(inspect(db_engine).get_table_names())
    expected = {
        "regions",
        "stores",
        "employees",
        "customers",
        "products",
        "orders",
        "order_items",
        "payments",
        "calendar",
        "inventory",
    }
    missing = expected - names
    assert not missing, f"Missing tables: {missing}"


def test_select_one(db_session: Session) -> None:
    assert db_session.execute(text("SELECT 1")).scalar_one() == 1


def test_fk_insert_region_store(db_session: Session) -> None:
    from datetime import date

    from app.models import Region, Store

    region = Region(code="TST-REG-IT", name="Test Region IT", level=1)
    db_session.add(region)
    db_session.flush()
    store = Store(
        code="TST-ST-IT",
        name="Test Store IT",
        region_id=region.id,
        is_active=True,
        opened_at=date(2020, 1, 1),
    )
    db_session.add(store)
    db_session.flush()
    assert store.id is not None
    # cleanup
    db_session.delete(store)
    db_session.delete(region)
