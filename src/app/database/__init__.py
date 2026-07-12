"""Database engine, session factory, and declarative base.

Models are added in a later phase — this package only provides connectivity.
"""

from app.database.base import Base
from app.database.engine import dispose_engine, get_engine
from app.database.session import get_session, session_scope

__all__ = [
    "Base",
    "dispose_engine",
    "get_engine",
    "get_session",
    "session_scope",
]
