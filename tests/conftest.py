"""Shared pytest fixtures.

Integration / data-quality tests need PostgreSQL:

    export TEST_DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/sales_dashboard_test

If unset or unreachable, those tests are skipped automatically.
"""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

import app.models  # noqa: F401 — register metadata
from app.config.settings import Settings, get_settings
from app.database.base import Base


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "unit: pure unit tests (no database)")
    config.addinivalue_line("markers", "integration: tests requiring PostgreSQL")
    config.addinivalue_line("markers", "data_quality: invariant / data validation tests")


@pytest.fixture(scope="session")
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def settings() -> Settings:
    """Application settings (reads .env if present)."""
    get_settings.cache_clear()
    return get_settings()


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> Generator[None]:
    """Avoid cross-test pollution of lru_cache on get_settings."""
    yield
    get_settings.cache_clear()


@pytest.fixture(scope="session")
def test_database_url() -> str | None:
    return os.environ.get("TEST_DATABASE_URL") or os.environ.get("DATABASE_URL")


@pytest.fixture(scope="session")
def db_engine(test_database_url: str | None) -> Generator[Engine | None]:
    """Session-scoped engine; None if DB unavailable."""
    if not test_database_url:
        yield None
        return
    engine = create_engine(test_database_url, pool_pre_ping=True, future=True)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        engine.dispose()
        pytest.skip(f"PostgreSQL not available: {exc}")
        yield None
        return

    # Create schema from metadata (idempotent for empty test DB)
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine: Engine | None) -> Generator[Session]:
    """Function-scoped session; skips if no engine."""
    if db_engine is None:
        pytest.skip("TEST_DATABASE_URL / DATABASE_URL not set or DB unreachable")
    factory = sessionmaker(
        bind=db_engine, autoflush=False, autocommit=False, expire_on_commit=False
    )
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@pytest.fixture
def fixtures_dir(project_root: Path) -> Path:
    return project_root / "tests" / "fixtures" / "files"
