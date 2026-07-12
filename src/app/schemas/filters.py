"""Analytics filter and KPI result DTOs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal


@dataclass(slots=True)
class AnalyticsFilter:
    """Shared filter for metrics / analytics / dashboard."""

    start_date: date | None = None
    end_date: date | None = None  # exclusive upper bound preferred
    store_ids: list[int] = field(default_factory=list)
    region_ids: list[int] = field(default_factory=list)
    category_ids: list[int] = field(default_factory=list)
    employee_ids: list[int] = field(default_factory=list)
    customer_id: int | None = None
    order_statuses: list[str] = field(default_factory=lambda: ["paid", "completed"])

    @classmethod
    def last_n_days(cls, days: int = 30) -> AnalyticsFilter:
        today = datetime.now(UTC).date()
        return cls(start_date=today - timedelta(days=days), end_date=today + timedelta(days=1))

    def resolve_bounds(self) -> tuple[datetime | None, datetime | None]:
        """Return timezone-aware datetime bounds (end exclusive if date given)."""
        start: datetime | None = None
        end: datetime | None = None
        if self.start_date is not None:
            start = datetime.combine(self.start_date, datetime.min.time(), tzinfo=UTC)
        if self.end_date is not None:
            end = datetime.combine(self.end_date, datetime.min.time(), tzinfo=UTC)
        return start, end


@dataclass(slots=True)
class KPIResult:
    """Canonical KPI bundle — single source of truth for dashboard/report."""

    revenue: Decimal = Decimal("0")
    cogs: Decimal = Decimal("0")
    gross_profit: Decimal = Decimal("0")
    gross_margin_pct: Decimal = Decimal("0")
    order_count: int = 0
    buyer_count: int = 0
    units_sold: int = 0
    aov: Decimal = Decimal("0")
    net_revenue: Decimal | None = None
    refunds: Decimal = Decimal("0")

    def as_dict(self) -> dict[str, object]:
        return {
            "revenue": self.revenue,
            "cogs": self.cogs,
            "gross_profit": self.gross_profit,
            "gross_margin_pct": self.gross_margin_pct,
            "order_count": self.order_count,
            "buyer_count": self.buyer_count,
            "units_sold": self.units_sold,
            "aov": self.aov,
            "net_revenue": self.net_revenue,
            "refunds": self.refunds,
        }
