"""Product ETL input schema."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.etl.cleaning.rules import parse_bool, parse_decimal


class ProductIn(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    sku: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=255)
    category_code: str = Field(min_length=1)
    brand_code: str | None = None
    supplier_code: str | None = None
    unit_price: Decimal = Field(ge=0)
    cost_price: Decimal = Field(ge=0)
    description: str | None = None
    is_active: bool = True

    @field_validator("unit_price", "cost_price", mode="before")
    @classmethod
    def _money(cls, v: object) -> Decimal:
        d = parse_decimal(v)
        if d is None:
            raise ValueError("price is required")
        return d

    @field_validator("is_active", mode="before")
    @classmethod
    def _active(cls, v: object) -> bool:
        b = parse_bool(v)
        return True if b is None else b
