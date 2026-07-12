"""Customer ETL input schema."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.etl.cleaning.rules import normalize_email, normalize_phone, parse_datetime


class CustomerIn(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    code: str = Field(min_length=1, max_length=30)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str | None = None
    phone: str | None = None
    city: str | None = None
    region_code: str | None = None
    registered_at: datetime | None = None
    gender: str | None = None
    address: str | None = None
    is_active: bool = True

    @field_validator("email", mode="before")
    @classmethod
    def _email(cls, v: object) -> str | None:
        if v is None or v == "":
            return None
        return normalize_email(str(v))

    @field_validator("phone", mode="before")
    @classmethod
    def _phone(cls, v: object) -> str | None:
        if v is None or v == "":
            return None
        return normalize_phone(str(v))

    @field_validator("registered_at", mode="before")
    @classmethod
    def _registered(cls, v: object) -> datetime | None:
        if v is None or v == "":
            return None
        parsed = parse_datetime(v)
        if isinstance(parsed, datetime):
            return parsed
        if parsed is not None:
            return datetime.combine(parsed, datetime.min.time())
        return None

    @field_validator("gender", mode="before")
    @classmethod
    def _gender(cls, v: object) -> str | None:
        if v is None or v == "":
            return None
        g = str(v).strip().lower()
        if g not in {"male", "female", "other", "unknown"}:
            raise ValueError(f"invalid gender: {v}")
        return g
