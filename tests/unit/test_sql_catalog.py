"""Unit tests for SQL catalog discovery (no database required)."""

from __future__ import annotations

import pytest

from app.sql_catalog import list_entries, load_entry, sql_root


def test_sql_root_exists() -> None:
    root = sql_root()
    assert root.is_dir()
    assert (root / "basic").is_dir()


def test_catalog_has_at_least_100_entries() -> None:
    entries = list_entries()
    assert len(entries) >= 100
    assert len(entries) == 135


def test_level_counts() -> None:
    expected = {
        "basic": 25,
        "intermediate": 30,
        "advanced": 35,
        "reporting": 30,
        "optimization": 15,
    }
    for level, count in expected.items():
        found = list_entries(level=level)
        assert len(found) == count, level


def test_ids_unique() -> None:
    ids = [e.id for e in list_entries()]
    assert len(ids) == len(set(ids))


def test_load_entry_case_insensitive() -> None:
    e = load_entry("r04")
    assert e.id == "R04"
    assert "SELECT" in e.sql.upper()
    assert e.path.exists()


def test_load_unknown_raises() -> None:
    with pytest.raises(KeyError):
        load_entry("ZZ99")


def test_headers_present() -> None:
    for entry in list_entries():
        assert entry.id
        assert entry.title
        assert entry.level
        assert entry.sql.strip()


def test_reporting_uses_paid_completed_where_relevant() -> None:
    """Spot-check core revenue reports mention status filter."""
    for qid in ("R01", "R02", "R04", "R13"):
        sql = load_entry(qid).sql.lower()
        assert "paid" in sql and "completed" in sql
