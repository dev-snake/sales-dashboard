"""Shared pytest fixtures (scaffold).

Integration fixtures that need PostgreSQL will be added in later phases.
"""

from __future__ import annotations

import pytest

from app.config.settings import Settings, get_settings


@pytest.fixture(scope="session")
def settings() -> Settings:
    """Application settings (reads .env if present)."""
    get_settings.cache_clear()
    return get_settings()


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> None:
    """Avoid cross-test pollution of lru_cache on get_settings."""
    yield
    get_settings.cache_clear()
