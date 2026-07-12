"""Order and order item ETL input schemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.etl.cleaning.rules import normalize_enum, parse_datetime, parse_decimal, parse_int


class OrderIn(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    order_number: str = Field(min_length=1, max_length=40)
    customer_code: str = Field(min_length=1)
    store_code: str = Field(min_length=1)
    employee_code: str = Field(min_length=1)
    order_date: datetime
    status: str
    subtotal: Decimal = Decimal("0")
    discount_amount: Decimal = Decimal("0")
    tax_amount: Decimal = Decimal("0")
    total_amount: Decimal = Decimal("0")
    notes: str | None = None
    promotion_code: str | None = None

    @field_validator("status", mode="before")
    @classmethod
    def _status(cls, v: object) -> str:
        s = normalize_enum(str(v) if v is not None else None)
        if s not in {"pending", "paid", "completed", "cancelled"}:
            raise ValueError(f"invalid order status: {v}")
        return s

    @field_validator("order_date", mode="before")
    @classmethod
    def _od(cls, v: object) -> datetime:
        parsed = parse_datetime(v)
        if parsed is None:
            raise ValueError("order_date required")
        if isinstance(parsed, datetime):
            return parsed
        return datetime.combine(parsed, datetime.min.time())

    @field_validator("subtotal", "discount_amount", "tax_amount", "total_amount", mode="before")
    @classmethod
    def _money(cls, v: object) -> Decimal:
        d = parse_decimal(v)
        return d if d is not None else Decimal("0")


class OrderItemIn(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    order_number: str = Field(min_length=1)
    product_sku: str = Field(min_length=1)
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    unit_cost: Decimal = Field(ge=0)
    discount_amount: Decimal = Decimal("0")
    line_total: Decimal | None = None

    @field_validator("quantity", mode="before")
    @classmethod
    def _qty(cls, v: object) -> int:
        q = parse_int(v)
        if q is None or q <= 0:
            raise ValueError("quantity must be > 0")
        return q

    @field_validator("unit_price", "unit_cost", "discount_amount", "line_total", mode="before")
    @classmethod
    def _money(cls, v: object) -> Decimal | None:
        return parse_decimal(v)
