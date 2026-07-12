"""Session factory and context managers."""

from __future__ import annotations

from collections.abc import Generator, Iterator
from contextlib import contextmanager

from sqlalchemy.orm import Session, sessionmaker

from app.database.engine import get_engine

_SessionLocal: sessionmaker[Session] | None = None


def _get_session_factory() -> sessionmaker[Session]:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=get_engine(),
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            class_=Session,
        )
    return _SessionLocal


def reset_session_factory() -> None:
    """Reset session factory (tests / engine reload)."""
    global _SessionLocal
    _SessionLocal = None


# Re-export for callers that import from session module
__all__ = ["get_session", "session_scope", "reset_session_factory"]


def get_session() -> Generator[Session]:
    """Yield a session and guarantee close (generator style for DI-like use)."""
    session = _get_session_factory()()
    try:
        yield session
    finally:
        session.close()


@contextmanager
def session_scope(*, commit: bool = True) -> Iterator[Session]:
    """Provide a transactional scope around a series of operations.

    Usage::

        with session_scope() as session:
            session.execute(...)
    """
    session = _get_session_factory()()
    try:
        yield session
        if commit:
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
