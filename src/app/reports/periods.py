"""Report period resolution (daily → yearly)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal, cast

ReportType = Literal["daily", "weekly", "monthly", "quarterly", "yearly"]


@dataclass(frozen=True, slots=True)
class PeriodWindow:
    """Inclusive start date, exclusive end date (same convention as AnalyticsFilter)."""

    report_type: ReportType
    as_of: date
    start: date
    end: date  # exclusive
    label: str

    @property
    def previous(self) -> PeriodWindow:
        """Comparison window of equal length immediately before this one."""
        length = (self.end - self.start).days
        prev_end = self.start
        prev_start = prev_end - timedelta(days=length)
        return PeriodWindow(
            report_type=self.report_type,
            as_of=self.as_of,
            start=prev_start,
            end=prev_end,
            label=f"prev_{self.label}",
        )


def resolve_period(report_type: ReportType, as_of: date | None = None) -> PeriodWindow:
    """Compute period containing ``as_of`` (default: today)."""
    d = as_of or date.today()
    rt: ReportType = parse_report_type(str(report_type))
    if rt == "daily":
        start, end = d, d + timedelta(days=1)
        label = d.strftime("%Y-%m-%d")
    elif rt == "weekly":
        # ISO week: Monday=0
        start = d - timedelta(days=d.weekday())
        end = start + timedelta(days=7)
        iso = d.isocalendar()
        label = f"{iso.year}-W{iso.week:02d}"
    elif rt == "monthly":
        start = d.replace(day=1)
        if start.month == 12:
            end = date(start.year + 1, 1, 1)
        else:
            end = date(start.year, start.month + 1, 1)
        label = start.strftime("%Y-%m")
    elif rt == "quarterly":
        q = (d.month - 1) // 3 + 1
        start_month = 3 * (q - 1) + 1
        start = date(d.year, start_month, 1)
        end = date(d.year + 1, 1, 1) if q == 4 else date(d.year, start_month + 3, 1)
        label = f"{d.year}-Q{q}"
    elif rt == "yearly":
        start = date(d.year, 1, 1)
        end = date(d.year + 1, 1, 1)
        label = str(d.year)
    else:
        raise ValueError(f"Unknown report type: {report_type}")

    return PeriodWindow(
        report_type=rt,
        as_of=d,
        start=start,
        end=end,
        label=label,
    )


def parse_report_type(value: str) -> ReportType:
    v = value.strip().lower()
    allowed = ("daily", "weekly", "monthly", "quarterly", "yearly")
    if v not in allowed:
        raise ValueError(f"type must be one of {allowed}, got {value!r}")
    return cast(ReportType, v)
