"""Path helpers anchored at the project root."""

from __future__ import annotations

from pathlib import Path

from app.config.settings import PROJECT_ROOT, get_settings


def project_root() -> Path:
    """Return repository root path."""
    return PROJECT_ROOT


def ensure_dir(path: Path) -> Path:
    """Create directory (and parents) if missing; return the path."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_runtime_dirs() -> None:
    """Ensure standard runtime directories exist (logs, datasets subfolders)."""
    settings = get_settings()
    for path in (
        settings.logs_path,
        settings.datasets_path / "raw",
        settings.cleaned_data_path,
        settings.processed_data_path,
        settings.exports_path,
    ):
        ensure_dir(path)
