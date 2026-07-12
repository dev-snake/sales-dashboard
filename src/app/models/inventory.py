"""Inventory snapshot per store × product."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.store import Store


class Inventory(TimestampMixin, Base):
    __tablename__ = "inventory"
    __table_args__ = (
        CheckConstraint("quantity_on_hand >= 0", name="ck_inventory_qty_nonneg"),
        CheckConstraint("reorder_level >= 0", name="ck_inventory_reorder_nonneg"),
        CheckConstraint(
            "max_level IS NULL OR max_level >= reorder_level",
            name="ck_inventory_max_level",
        ),
        UniqueConstraint("store_id", "product_id", name="uq_inventory_store_product"),
        Index("ix_inventory_product_id", "product_id"),
        Index(
            "ix_inventory_low_stock",
            "store_id",
            "product_id",
            postgresql_where=text("quantity_on_hand <= reorder_level"),
        ),
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
    quantity_on_hand: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    reorder_level: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    max_level: Mapped[int | None] = mapped_column(Integer, nullable=True)

    store: Mapped[Store] = relationship("Store", back_populates="inventory_rows")
    product: Mapped[Product] = relationship("Product", back_populates="inventory_rows")

    def __repr__(self) -> str:
        return (
            f"<Inventory id={self.id} store_id={self.store_id} "
            f"product_id={self.product_id} qty={self.quantity_on_hand}>"
        )
