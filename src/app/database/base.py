"""SQLAlchemy 2.x declarative base.

Table models will inherit from ``Base`` in the models phase.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Project-wide ORM base class."""

    pass
