"""Promotion / discount campaigns."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    Index,
    Numeric,
    String,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.order import Order


class Promotion(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "promotions"
    __table_args__ = (
        CheckConstraint(
            "discount_type IN ('percent', 'fixed')",
            name="ck_promotions_discount_type",
        ),
        CheckConstraint("discount_value > 0", name="ck_promotions_discount_value_pos"),
        CheckConstraint(
            "min_order_amount IS NULL OR min_order_amount >= 0",
            name="ck_promotions_min_order_nonneg",
        ),
        CheckConstraint("end_date >= start_date", name="ck_promotions_date_range"),
        CheckConstraint(
            "(discount_type <> 'percent') OR (discount_value <= 100)",
            name="ck_promotions_percent_max",
        ),
        Index("ix_promotions_date_range", "start_date", "end_date"),
        Index("ix_promotions_is_active", "is_active"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    discount_type: Mapped[str] = mapped_column(String(20), nullable=False)
    discount_value: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    min_order_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=true())

    orders: Mapped[list[Order]] = relationship("Order", back_populates="promotion")

    def __repr__(self) -> str:
        return f"<Promotion id={self.id} code={self.code!r}>"
