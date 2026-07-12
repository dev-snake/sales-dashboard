"""Inventory movement ledger."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.store import Store


class StockMovement(TimestampMixin, Base):
    __tablename__ = "stock_movements"
    __table_args__ = (
        CheckConstraint(
            "movement_type IN ("
            "'purchase_in', 'sale_out', 'return_in', "
            "'transfer_in', 'transfer_out', 'adjustment', 'damage_out'"
            ")",
            name="ck_stock_movements_type",
        ),
        CheckConstraint("quantity <> 0", name="ck_stock_movements_quantity_nonzero"),
        Index("ix_stock_movements_store_product", "store_id", "product_id"),
        Index("ix_stock_movements_moved_at", "moved_at"),
        Index("ix_stock_movements_type", "movement_type"),
        Index("ix_stock_movements_reference", "reference_type", "reference_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    store_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("stores.id", ondelete="RESTRICT"),
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
    )
    movement_type: Mapped[str] = mapped_column(String(30), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    reference_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    reference_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    moved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    store: Mapped[Store] = relationship("Store", back_populates="stock_movements")
    product: Mapped[Product] = relationship("Product", back_populates="stock_movements")

    def __repr__(self) -> str:
        return f"<StockMovement id={self.id} type={self.movement_type!r} qty={self.quantity}>"
