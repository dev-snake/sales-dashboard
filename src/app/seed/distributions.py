"""Random distributions and weighted choices for realistic seed data."""

from __future__ import annotations

import random
from calendar import monthrange
from collections.abc import Sequence
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import TypeVar
from zoneinfo import ZoneInfo

import numpy as np
from faker import Faker

T = TypeVar("T")

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")

# Month seasonality multipliers (1=Jan … 12=Dec)
MONTH_WEIGHTS: dict[int, float] = {
    1: 1.25,  # Tết season
    2: 1.15,
    3: 0.95,
    4: 0.95,
    5: 1.00,
    6: 1.00,
    7: 1.05,
    8: 1.05,
    9: 1.00,
    10: 1.05,
    11: 1.30,  # year-end
    12: 1.40,
}

ORDER_STATUS_WEIGHTS: list[tuple[str, float]] = [
    ("completed", 0.75),
    ("paid", 0.15),
    ("pending", 0.05),
    ("cancelled", 0.05),
]

PAYMENT_METHOD_WEIGHTS: list[tuple[str, float]] = [
    ("cash", 0.40),
    ("card", 0.35),
    ("transfer", 0.15),
    ("e_wallet", 0.10),
]

RETURN_REASON_WEIGHTS: list[tuple[str, float]] = [
    ("changed_mind", 0.40),
    ("defective", 0.25),
    ("wrong_item", 0.20),
    ("other", 0.10),
    ("expired", 0.05),
]

GENDER_CHOICES = ("male", "female", "other", "unknown")

CATEGORY_NAMES = [
    "Electronics",
    "Home & Living",
    "Fashion",
    "Beauty",
    "Sports",
    "Grocery",
    "Books",
    "Toys",
    "Health",
    "Automotive",
    "Office",
    "Pets",
    "Garden",
    "Baby",
    "Jewelry",
    "Footwear",
    "Accessories",
    "Kitchen",
    "Gaming",
    "Outdoor",
]

CITY_REGION_HINTS = [
    ("Ha Noi", "HN"),
    ("Ho Chi Minh", "HCM"),
    ("Da Nang", "DN"),
    ("Hai Phong", "HP"),
    ("Can Tho", "CT"),
    ("Hue", "HUE"),
    ("Nha Trang", "NT"),
    ("Vung Tau", "VT"),
    ("Bien Hoa", "BH"),
    ("Buon Ma Thuot", "BMT"),
]


def make_faker(locale: str, seed: int) -> Faker:
    """Create a seeded Faker instance with locale fallback."""
    try:
        fake = Faker(locale)
    except AttributeError:
        fake = Faker("en_US")
    Faker.seed(seed)
    fake.seed_instance(seed)
    return fake


def seed_all(seed: int) -> None:
    """Seed Python random, NumPy, and Faker global state."""
    random.seed(seed)
    np.random.seed(seed)
    Faker.seed(seed)


def weighted_choice[T](items: Sequence[tuple[T, float]]) -> T:
    values = [item[0] for item in items]
    weights = [item[1] for item in items]
    return random.choices(values, weights=weights, k=1)[0]


def money(value: float) -> Decimal:
    return Decimal(f"{value:.2f}")


def lognormal_price(
    rng: np.random.Generator, low: float = 20_000, high: float = 5_000_000
) -> Decimal:
    """Log-normal-ish retail price in VND-like range."""
    # sample then scale into band
    raw = float(rng.lognormal(mean=11.5, sigma=0.7))
    clipped = min(max(raw, low), high)
    # round to 1000 VND
    rounded = round(clipped / 1000) * 1000
    return money(max(rounded, low))


def cost_from_price(unit_price: Decimal, rng: np.random.Generator) -> Decimal:
    ratio = float(rng.uniform(0.55, 0.85))
    return money(float(unit_price) * ratio)


def poisson_clipped(rng: np.random.Generator, lam: float, low: int, high: int) -> int:
    val = int(rng.poisson(lam))
    return max(low, min(high, val))


def power_law_weights(n: int, alpha: float = 1.5) -> np.ndarray:
    """Weights favouring lower indices (top customers / products)."""
    ranks = np.arange(1, n + 1, dtype=np.float64)
    w = ranks ** (-alpha)
    w /= w.sum()
    return w


def pick_index(weights: np.ndarray, rng: np.random.Generator) -> int:
    return int(rng.choice(len(weights), p=weights))


def build_weighted_dates(
    start: date, end: date, rng: np.random.Generator | None = None
) -> tuple[list[date], np.ndarray]:
    """Return (dates, normalized weights) with seasonal + weekend uplift."""
    del rng  # reserved for future jitter
    dates: list[date] = []
    weights: list[float] = []
    cur = start
    while cur <= end:
        w = MONTH_WEIGHTS.get(cur.month, 1.0)
        if cur.weekday() >= 5:  # Sat/Sun
            w *= 1.20
        dates.append(cur)
        weights.append(w)
        cur += timedelta(days=1)
    arr = np.array(weights, dtype=np.float64)
    arr /= arr.sum()
    return dates, arr


def sample_order_datetime(
    dates: list[date],
    date_weights: np.ndarray,
    rng: np.random.Generator,
) -> datetime:
    """Sample order_date with seasonality and business-hour time."""
    idx = int(rng.choice(len(dates), p=date_weights))
    d = dates[idx]
    hour = int(rng.integers(8, 22))
    minute = int(rng.integers(0, 60))
    second = int(rng.integers(0, 60))
    return datetime.combine(d, time(hour, minute, second), tzinfo=VN_TZ)


def date_id_from_date(d: date) -> int:
    return d.year * 10_000 + d.month * 100 + d.day


def month_name(month: int) -> str:
    return date(2000, month, 1).strftime("%B")


def day_name(dow_iso: int) -> str:
    # ISO: 1=Mon … 7=Sun
    names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return names[dow_iso - 1]


def iter_calendar_range(start: date, end: date) -> list[date]:
    days: list[date] = []
    cur = start
    while cur <= end:
        days.append(cur)
        cur += timedelta(days=1)
    return days


def last_day_of_month(year: int, month: int) -> int:
    return monthrange(year, month)[1]
