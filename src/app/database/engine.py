"""SQLAlchemy engine factory (psycopg v3 driver)."""

from __future__ import annotations

from functools import lru_cache

from sqlalchemy import Engine, create_engine

from app.config.settings import Settings, get_settings


@lru_cache(maxsize=1)
def get_engine(url: str | None = None) -> Engine:
    """Create (or return cached) SQLAlchemy engine.

    Parameters
    ----------
    url:
        Optional override for tests. When omitted, uses ``Settings.database_url``.
    """
    settings: Settings = get_settings()
    database_url = url or settings.database_url

    return create_engine(
        database_url,
        echo=settings.db_echo,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_pre_ping=settings.db_pool_pre_ping,
        future=True,
    )


def dispose_engine() -> None:
    """Dispose cached engine and clear LRU cache (useful in tests)."""
    try:
        engine = get_engine()
        engine.dispose()
    except Exception:  # noqa: BLE001 — best-effort cleanup
        pass
    get_engine.cache_clear()
