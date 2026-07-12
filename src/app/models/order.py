"""Sales order header."""

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
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.employee import Employee
    from app.models.order_item import OrderItem
    from app.models.payment import Payment
    from app.models.promotion import Promotion
    from app.models.return_ import Return
    from app.models.store import Store


class Order(TimestampMixin, Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'paid', 'completed', 'cancelled')",
            name="ck_orders_status",
        ),
        CheckConstraint("subtotal >= 0", name="ck_orders_subtotal_nonneg"),
        CheckConstraint("discount_amount >= 0", name="ck_orders_discount_nonneg"),
        CheckConstraint("tax_amount >= 0", name="ck_orders_tax_nonneg"),
        CheckConstraint("total_amount >= 0", name="ck_orders_total_nonneg"),
        Index("ix_orders_customer_id", "customer_id"),
        Index("ix_orders_store_id", "store_id"),
        Index("ix_orders_employee_id", "employee_id"),
        Index("ix_orders_order_date", "order_date"),
        Index("ix_orders_status", "status"),
        Index("ix_orders_store_date", "store_id", "order_date"),
        Index("ix_orders_status_date", "status", "order_date"),
        Index("ix_orders_promotion_id", "promotion_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_number: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    customer_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
    )
    store_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("stores.id", ondelete="RESTRICT"),
        nullable=False,
    )
    employee_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("employees.id", ondelete="RESTRICT"),
        nullable=False,
    )
    promotion_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("promotions.id", ondelete="RESTRICT"),
        nullable=True,
    )
    order_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        server_default="0",
    )
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        server_default="0",
    )
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        server_default="0",
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        server_default="0",
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    customer: Mapped[Customer] = relationship("Customer", back_populates="orders")
    store: Mapped[Store] = relationship("Store", back_populates="orders")
    employee: Mapped[Employee] = relationship("Employee", back_populates="orders")
    promotion: Mapped[Promotion | None] = relationship("Promotion", back_populates="orders")
    items: Mapped[list[OrderItem]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )
    payments: Mapped[list[Payment]] = relationship("Payment", back_populates="order")
    returns: Mapped[list[Return]] = relationship("Return", back_populates="order")

    def __repr__(self) -> str:
        return f"<Order id={self.id} number={self.order_number!r}>"
