"""Store master data."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, Date, ForeignKey, Index, String, Text, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.inventory import Inventory
    from app.models.order import Order
    from app.models.region import Region
    from app.models.return_ import Return
    from app.models.stock_movement import StockMovement


class Store(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "stores"
    __table_args__ = (
        Index("ix_stores_region_id", "region_id"),
        Index("ix_stores_is_active", "is_active"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    region_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("regions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    opened_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=true())

    region: Mapped[Region] = relationship("Region", back_populates="stores")
    employees: Mapped[list[Employee]] = relationship("Employee", back_populates="store")
    orders: Mapped[list[Order]] = relationship("Order", back_populates="store")
    inventory_rows: Mapped[list[Inventory]] = relationship("Inventory", back_populates="store")
    stock_movements: Mapped[list[StockMovement]] = relationship(
        "StockMovement", back_populates="store"
    )
    returns: Mapped[list[Return]] = relationship("Return", back_populates="store")

    def __repr__(self) -> str:
        return f"<Store id={self.id} code={self.code!r}>"
