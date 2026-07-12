"""Employee master data with manager hierarchy."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    String,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.store import Store


class Employee(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "employees"
    __table_args__ = (
        CheckConstraint(
            "manager_id IS DISTINCT FROM id",
            name="ck_employees_manager_not_self",
        ),
        Index("ix_employees_store_id", "store_id"),
        Index("ix_employees_manager_id", "manager_id"),
        Index("ix_employees_hire_date", "hire_date"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    store_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("stores.id", ondelete="RESTRICT"),
        nullable=False,
    )
    manager_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("employees.id", ondelete="RESTRICT"),
        nullable=True,
    )
    job_title: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        server_default="Sales Associate",
    )
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=true())

    store: Mapped[Store] = relationship("Store", back_populates="employees")
    manager: Mapped[Employee | None] = relationship(
        "Employee",
        remote_side="Employee.id",
        back_populates="direct_reports",
        foreign_keys=[manager_id],
    )
    direct_reports: Mapped[list[Employee]] = relationship(
        "Employee",
        back_populates="manager",
        foreign_keys=[manager_id],
    )
    orders: Mapped[list[Order]] = relationship("Order", back_populates="employee")

    def __repr__(self) -> str:
        return f"<Employee id={self.id} code={self.code!r}>"
