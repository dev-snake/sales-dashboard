"""Seed data service — orchestrates DatabaseSeeder and sample exports."""

from __future__ import annotations

from pathlib import Path

from loguru import logger
from sqlalchemy.orm import Session

from app.seed.sample_export import export_etl_samples
from app.seed.scale_config import ScaleConfig, get_scale_config
from app.seed.seeder import DatabaseSeeder, SeedResult


class SeedService:
    """High-level API for CLI and tests."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def run(
        self,
        scale: str = "100",
        *,
        seed: int = 42,
        locale: str = "vi_VN",
        reset: bool = False,
        export_samples: bool = True,
        samples_dir: Path | None = None,
    ) -> SeedResult:
        """Generate seed data for the given scale tier."""
        config: ScaleConfig = get_scale_config(scale)
        logger.info(
            "Starting seed | scale={} orders={} seed={} reset={}",
            config.name,
            config.orders,
            seed,
            reset,
        )
        seeder = DatabaseSeeder(
            self.session,
            config,
            seed=seed,
            locale=locale,
        )
        result = seeder.run(reset=reset)

        if export_samples:
            path = export_etl_samples(samples_dir)
            logger.info("ETL sample files written under {}", path)
            result.counts["sample_export"] = 1

        return result
