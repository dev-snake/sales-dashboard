"""Region dimension (self-referential hierarchy)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Index, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.store import Store


class Region(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "regions"
    __table_args__ = (
        CheckConstraint("level BETWEEN 1 AND 5", name="ck_regions_level_range"),
        Index("ix_regions_parent_id", "parent_id"),
        Index("ix_regions_name", "name"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("regions.id", ondelete="RESTRICT"),
        nullable=True,
    )
    level: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        server_default="1",
        default=1,
    )

    parent: Mapped[Region | None] = relationship(
        "Region",
        remote_side="Region.id",
        back_populates="children",
        foreign_keys=[parent_id],
    )
    children: Mapped[list[Region]] = relationship(
        "Region",
        back_populates="parent",
        foreign_keys=[parent_id],
    )
    stores: Mapped[list[Store]] = relationship("Store", back_populates="region")
    customers: Mapped[list[Customer]] = relationship("Customer", back_populates="region")

    def __repr__(self) -> str:
        return f"<Region id={self.id} code={self.code!r}>"
