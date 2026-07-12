"""Calendar / date dimension for reporting joins."""

from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, CheckConstraint, Date, Index, Integer, SmallInteger, String, false
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Calendar(Base):
    """Static date dimension (no soft-delete / updated_at)."""

    __tablename__ = "calendar"
    __table_args__ = (
        CheckConstraint("quarter BETWEEN 1 AND 4", name="ck_calendar_quarter"),
        CheckConstraint("month BETWEEN 1 AND 12", name="ck_calendar_month"),
        CheckConstraint("week_of_year BETWEEN 1 AND 53", name="ck_calendar_week"),
        CheckConstraint("day_of_week BETWEEN 1 AND 7", name="ck_calendar_dow"),
        Index("ix_calendar_year_month", "year", "month"),
        Index("ix_calendar_year_quarter", "year", "quarter"),
    )

    # Natural key YYYYMMDD — not a serial sequence
    date_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    full_date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    quarter: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    month: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    month_name: Mapped[str] = mapped_column(String(20), nullable=False)
    week_of_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    day_of_month: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    day_of_week: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    day_name: Mapped[str] = mapped_column(String(20), nullable=False)
    is_weekend: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_holiday: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=false())
    holiday_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    fiscal_year: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    fiscal_quarter: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    def __repr__(self) -> str:
        return f"<Calendar date_id={self.date_id} full_date={self.full_date}>"
