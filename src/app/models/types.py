"""Shared SQLAlchemy column type aliases."""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated

from sqlalchemy import Numeric
from sqlalchemy.orm import mapped_column

# Money: NUMERIC(18, 2)
Money = Annotated[Decimal, mapped_column(Numeric(18, 2))]
