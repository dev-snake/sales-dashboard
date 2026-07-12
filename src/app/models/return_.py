"""Product returns / refunds.

Module named ``return_`` because ``return`` is a Python keyword.
Table name remains ``returns``.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.order_item import OrderItem
    from app.models.store import Store


class Return(TimestampMixin, Base):
    __tablename__ = "returns"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_returns_quantity_pos"),
        CheckConstraint(
            "reason IN ('defective', 'wrong_item', 'changed_mind', 'expired', 'other')",
            name="ck_returns_reason",
        ),
        CheckConstraint("refund_amount >= 0", name="ck_returns_refund_nonneg"),
        CheckConstraint(
            "status IN ('requested', 'approved', 'rejected', 'completed')",
            name="ck_returns_status",
        ),
        Index("ix_returns_order_id", "order_id"),
        Index("ix_returns_order_item_id", "order_item_id"),
        Index("ix_returns_store_id", "store_id"),
        Index("ix_returns_returned_at", "returned_at"),
        Index("ix_returns_status", "status"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    return_number: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    order_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("orders.id", ondelete="RESTRICT"),
        nullable=False,
    )
    order_item_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("order_items.id", ondelete="RESTRICT"),
        nullable=False,
    )
    store_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("stores.id", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(50), nullable=False)
    refund_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        server_default="0",
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    returned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    order: Mapped[Order] = relationship("Order", back_populates="returns")
    order_item: Mapped[OrderItem] = relationship("OrderItem", back_populates="returns")
    store: Mapped[Store] = relationship("Store", back_populates="returns")

    def __repr__(self) -> str:
        return f"<Return id={self.id} number={self.return_number!r}>"
