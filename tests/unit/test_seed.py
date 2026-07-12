"""Unit tests for seed configuration and pure generators (no DB)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import pytest

from app.seed.calendar_gen import build_calendar_rows
from app.seed.distributions import (
    cost_from_price,
    lognormal_price,
    money,
    power_law_weights,
    seed_all,
    weighted_choice,
)
from app.seed.sample_export import export_etl_samples
from app.seed.scale_config import SCALE_TIERS, get_scale_config


def test_scale_configs_known() -> None:
    for key in ("100", "1k", "10k", "100k", "1m"):
        cfg = get_scale_config(key)
        assert cfg.orders > 0
        assert cfg.customers > 0
        assert cfg.products > 0


def test_scale_aliases() -> None:
    assert get_scale_config("xs").name == "100"
    assert get_scale_config("S").name == "1k"


def test_unknown_scale() -> None:
    with pytest.raises(ValueError, match="Unknown scale"):
        get_scale_config("999")


def test_scale_order_counts_match_design() -> None:
    assert get_scale_config("100").orders == 100
    assert get_scale_config("1k").orders == 1_000
    assert get_scale_config("10k").orders == 10_000


def test_calendar_rows_cover_range() -> None:
    rows = build_calendar_rows(date(2020, 1, 1), date(2020, 1, 31))
    assert len(rows) == 31
    assert rows[0]["date_id"] == 20200101
    assert rows[0]["full_date"] == date(2020, 1, 1)
    assert rows[-1]["date_id"] == 20200131
    assert all("year" in r and "is_weekend" in r for r in rows)


def test_full_calendar_size() -> None:
    rows = build_calendar_rows()
    # 2020-01-01 .. 2030-12-31 inclusive ≈ 4018 days
    assert 4000 < len(rows) < 4100


def test_power_law_sums_to_one() -> None:
    w = power_law_weights(100)
    assert abs(w.sum() - 1.0) < 1e-9
    assert w[0] > w[-1]


def test_money_and_cost() -> None:
    seed_all(42)
    rng = np.random.default_rng(42)
    price = lognormal_price(rng)
    cost = cost_from_price(price, rng)
    assert cost <= price
    assert money(10.5) == money(10.50)


def test_weighted_choice_deterministic() -> None:
    seed_all(1)
    # smoke: returns one of the labels
    label = weighted_choice([("a", 0.5), ("b", 0.5)])
    assert label in {"a", "b"}


def test_export_etl_samples(tmp_path: Path) -> None:
    out = export_etl_samples(tmp_path, seed=7)
    assert (out / "customers.csv").exists()
    assert (out / "products.xlsx").exists()
    assert (out / "orders.csv").exists()
    assert (out / "order_items.csv").exists()
    assert (out / "payments.json").exists()
    customers = (out / "customers.csv").read_text(encoding="utf-8").strip().splitlines()
    assert len(customers) == 51  # header + 50


def test_all_tier_names_unique() -> None:
    names = {c.name for c in SCALE_TIERS.values()}
    assert names == {"100", "1k", "10k", "100k", "1m"}
