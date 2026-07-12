"""Central application settings loaded from environment / `.env`."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root: src/app/config/settings.py -> parents[3] == repo root
PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Runtime configuration for the Sales Analytics Dashboard.

    Values are read from environment variables and an optional `.env` file.
    No business logic lives here — only configuration.
    """

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Application ---
    app_name: str = Field(default="sales-dashboard", description="Application identifier")
    app_env: Literal["development", "test", "production"] = Field(default="development")
    debug: bool = Field(default=True)
    log_level: Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO"
    )

    # --- Database ---
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/sales_dashboard",
        description="SQLAlchemy URL using the psycopg (v3) driver",
    )
    db_echo: bool = Field(default=False, description="Echo SQL to logs (dev only)")
    db_pool_size: int = Field(default=5, ge=1, le=50)
    db_max_overflow: int = Field(default=10, ge=0, le=100)
    db_pool_pre_ping: bool = Field(default=True)

    # --- Paths ---
    project_root: Path = Field(default=PROJECT_ROOT)
    datasets_dir: Path = Field(default=Path("datasets"))
    logs_dir: Path = Field(default=Path("logs"))
    exports_dir: Path = Field(default=Path("datasets/exported"))

    # --- ETL defaults (consumed in later phases) ---
    etl_batch_size: int = Field(default=1000, ge=1)
    etl_strict_mode: bool = Field(default=False)

    # --- Business defaults ---
    default_currency: str = Field(default="VND")
    default_locale: str = Field(default="vi_VN")
    tax_rate: float = Field(default=0.08, ge=0.0, le=1.0)

    @field_validator("datasets_dir", "logs_dir", "exports_dir", mode="before")
    @classmethod
    def _coerce_path(cls, value: Path | str) -> Path:
        return Path(value) if not isinstance(value, Path) else value

    def resolve_path(self, path: Path) -> Path:
        """Resolve a path relative to project root when not absolute."""
        if path.is_absolute():
            return path
        return (self.project_root / path).resolve()

    @property
    def datasets_path(self) -> Path:
        return self.resolve_path(self.datasets_dir)

    @property
    def logs_path(self) -> Path:
        return self.resolve_path(self.logs_dir)

    @property
    def exports_path(self) -> Path:
        return self.resolve_path(self.exports_dir)

    @property
    def raw_data_path(self) -> Path:
        return self.datasets_path / "raw"

    @property
    def cleaned_data_path(self) -> Path:
        return self.datasets_path / "cleaned"

    @property
    def processed_data_path(self) -> Path:
        return self.datasets_path / "processed"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a process-wide cached Settings instance."""
    return Settings()
