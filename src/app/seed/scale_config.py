"""Scale tier configuration for seed generation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Final


@dataclass(frozen=True, slots=True)
class ScaleConfig:
    """Counts and time window for a seed tier."""

    name: str
    orders: int
    customers: int
    products: int
    stores: int
    employees: int
    regions: int
    categories: int
    brands: int
    suppliers: int
    promotions: int
    months_history: int
    batch_size: int

    @property
    def order_start_date(self) -> date:
        return date.today() - timedelta(days=self.months_history * 30)

    @property
    def order_end_date(self) -> date:
        return date.today()


SCALE_TIERS: Final[dict[str, ScaleConfig]] = {
    "100": ScaleConfig(
        name="100",
        orders=100,
        customers=80,
        products=50,
        stores=3,
        employees=10,
        regions=5,
        categories=8,
        brands=10,
        suppliers=5,
        promotions=5,
        months_history=6,
        batch_size=500,
    ),
    "1k": ScaleConfig(
        name="1k",
        orders=1_000,
        customers=600,
        products=150,
        stores=5,
        employees=25,
        regions=8,
        categories=12,
        brands=20,
        suppliers=10,
        promotions=15,
        months_history=6,
        batch_size=1_000,
    ),
    "10k": ScaleConfig(
        name="10k",
        orders=10_000,
        customers=4_000,
        products=400,
        stores=10,
        employees=60,
        regions=12,
        categories=20,
        brands=40,
        suppliers=20,
        promotions=30,
        months_history=18,
        batch_size=2_000,
    ),
    "100k": ScaleConfig(
        name="100k",
        orders=100_000,
        customers=30_000,
        products=1_000,
        stores=20,
        employees=150,
        regions=16,
        categories=30,
        brands=80,
        suppliers=40,
        promotions=50,
        months_history=36,
        batch_size=5_000,
    ),
    "1m": ScaleConfig(
        name="1m",
        orders=1_000_000,
        customers=200_000,
        products=2_000,
        stores=40,
        employees=400,
        regions=20,
        categories=40,
        brands=120,
        suppliers=60,
        promotions=80,
        months_history=36,
        batch_size=5_000,
    ),
}

# Aliases
SCALE_TIERS["xs"] = SCALE_TIERS["100"]
SCALE_TIERS["s"] = SCALE_TIERS["1k"]
SCALE_TIERS["m"] = SCALE_TIERS["10k"]
SCALE_TIERS["l"] = SCALE_TIERS["100k"]
SCALE_TIERS["xl"] = SCALE_TIERS["1m"]


def get_scale_config(scale: str) -> ScaleConfig:
    """Resolve scale flag to config (case-insensitive)."""
    key = scale.strip().lower()
    if key not in SCALE_TIERS:
        known = ", ".join(sorted({c.name for c in SCALE_TIERS.values()}))
        raise ValueError(f"Unknown scale {scale!r}. Choose one of: {known}")
    return SCALE_TIERS[key]
