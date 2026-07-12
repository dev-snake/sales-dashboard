"""ReportDataPackage — structured payload for Excel/PDF builders."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import pandas as pd

from app.reports.periods import PeriodWindow
from app.schemas.filters import KPIResult


@dataclass
class ReportDataPackage:
    """Collected analytics for one reporting period."""

    report_type: str
    period: PeriodWindow
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    kpi: KPIResult = field(default_factory=KPIResult)
    kpi_previous: KPIResult = field(default_factory=KPIResult)
    trend: pd.DataFrame = field(default_factory=pd.DataFrame)
    top_products: pd.DataFrame = field(default_factory=pd.DataFrame)
    top_stores: pd.DataFrame = field(default_factory=pd.DataFrame)
    top_customers: pd.DataFrame = field(default_factory=pd.DataFrame)
    top_employees: pd.DataFrame = field(default_factory=pd.DataFrame)
    by_category: pd.DataFrame = field(default_factory=pd.DataFrame)
    by_region: pd.DataFrame = field(default_factory=pd.DataFrame)
    rfm_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    abc: pd.DataFrame = field(default_factory=pd.DataFrame)
    repeat_rate: dict[str, float | int] = field(default_factory=dict)
    low_stock: pd.DataFrame = field(default_factory=pd.DataFrame)
    extras: dict[str, Any] = field(default_factory=dict)

    @property
    def title(self) -> str:
        return f"Sales {self.report_type.capitalize()} Report — {self.period.label}"

    def kpi_delta_pct(self, key: str) -> float | None:
        cur = float(getattr(self.kpi, key, 0) or 0)
        prev = float(getattr(self.kpi_previous, key, 0) or 0)
        if prev == 0:
            return None
        return round(100.0 * (cur - prev) / prev, 2)
