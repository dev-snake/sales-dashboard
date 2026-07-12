"""Unit tests for configuration scaffold."""

from __future__ import annotations

from app.config.settings import PROJECT_ROOT, Settings


def test_settings_defaults() -> None:
    settings = Settings(
        _env_file=None,  # type: ignore[call-arg]
        database_url="postgresql+psycopg://u:p@localhost:5432/testdb",
    )
    assert settings.app_name == "sales-dashboard"
    assert settings.default_currency == "VND"
    assert settings.etl_batch_size == 1000
    assert settings.project_root == PROJECT_ROOT


def test_resolve_datasets_path() -> None:
    settings = Settings(
        _env_file=None,  # type: ignore[call-arg]
        datasets_dir="datasets",
    )
    path = settings.datasets_path
    assert path.is_absolute()
    assert path.name == "datasets"


def test_app_version_importable() -> None:
    from app import __version__

    assert __version__
