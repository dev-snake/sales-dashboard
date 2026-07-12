"""Payment ETL input schema."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.etl.cleaning.rules import normalize_enum, parse_datetime, parse_decimal


class PaymentIn(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    payment_number: str = Field(min_length=1, max_length=40)
    order_number: str = Field(min_length=1)
    method: str
    amount: Decimal = Field(gt=0)
    status: str
    paid_at: datetime | None = None

    @field_validator("method", mode="before")
    @classmethod
    def _method(cls, v: object) -> str:
        m = normalize_enum(str(v) if v is not None else None)
        if m not in {"cash", "card", "transfer", "e_wallet", "other"}:
            raise ValueError(f"invalid payment method: {v}")
        return m

    @field_validator("status", mode="before")
    @classmethod
    def _status(cls, v: object) -> str:
        s = normalize_enum(str(v) if v is not None else None)
        if s not in {"pending", "completed", "failed", "refunded"}:
            raise ValueError(f"invalid payment status: {v}")
        return s

    @field_validator("amount", mode="before")
    @classmethod
    def _amount(cls, v: object) -> Decimal:
        d = parse_decimal(v)
        if d is None or d <= 0:
            raise ValueError("amount must be > 0")
        return d

    @field_validator("paid_at", mode="before")
    @classmethod
    def _paid(cls, v: object) -> datetime | None:
        if v is None or v == "":
            return None
        parsed = parse_datetime(v)
        if isinstance(parsed, datetime):
            return parsed
        if parsed is not None:
            return datetime.combine(parsed, datetime.min.time())
        return None
