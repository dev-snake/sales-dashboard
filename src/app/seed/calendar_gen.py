"""Calendar dimension generator (2020-01-01 → 2030-12-31)."""

from __future__ import annotations

from datetime import date
from typing import Any

from app.seed.distributions import date_id_from_date, day_name, iter_calendar_range, month_name

# Vietnam public holidays (approx fixed + observed dates simplified)
FIXED_HOLIDAYS: dict[tuple[int, int], str] = {
    (1, 1): "New Year",
    (4, 30): "Reunification Day",
    (5, 1): "Labour Day",
    (9, 2): "National Day",
}


def build_calendar_rows(
    start: date = date(2020, 1, 1),
    end: date = date(2030, 12, 31),
) -> list[dict[str, Any]]:
    """Generate calendar dimension rows."""
    rows: list[dict[str, Any]] = []
    for d in iter_calendar_range(start, end):
        iso_dow = d.isoweekday()  # 1=Mon … 7=Sun
        holiday_name = FIXED_HOLIDAYS.get((d.month, d.day))
        # Simplified lunar new year placeholder: last week of Jan / first week of Feb
        if holiday_name is None and d.month == 1 and d.day in (28, 29, 30, 31):
            holiday_name = "Tet holiday (approx)"
        if holiday_name is None and d.month == 2 and d.day in (1, 2, 3):
            holiday_name = "Tet holiday (approx)"

        rows.append(
            {
                "date_id": date_id_from_date(d),
                "full_date": d,
                "year": d.year,
                "quarter": (d.month - 1) // 3 + 1,
                "month": d.month,
                "month_name": month_name(d.month),
                "week_of_year": int(d.strftime("%V")),
                "day_of_month": d.day,
                "day_of_week": iso_dow,
                "day_name": day_name(iso_dow),
                "is_weekend": iso_dow >= 6,
                "is_holiday": holiday_name is not None,
                "holiday_name": holiday_name,
                "fiscal_year": d.year if d.month >= 4 else d.year - 1,
                "fiscal_quarter": ((d.month - 4) % 12) // 3 + 1,
            }
        )
    return rows
