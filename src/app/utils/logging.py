"""Loguru logging setup — console + rotating file."""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger

from app.config.settings import Settings, get_settings

_CONFIGURED = False


def setup_logging(settings: Settings | None = None) -> None:
    """Configure loguru sinks once per process.

    - stderr: colorized, level from settings
    - logs/app.log: rotation 10 MB, retention 14 days
    """
    global _CONFIGURED
    if _CONFIGURED:
        return

    cfg = settings or get_settings()
    log_dir: Path = cfg.logs_path
    log_dir.mkdir(parents=True, exist_ok=True)

    logger.remove()

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stderr,
        level=cfg.log_level,
        format=log_format,
        colorize=True,
        backtrace=cfg.debug,
        diagnose=cfg.debug,
    )

    logger.add(
        log_dir / "app.log",
        level=cfg.log_level,
        format=log_format,
        colorize=False,
        rotation="10 MB",
        retention="14 days",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=cfg.debug,
    )

    _CONFIGURED = True
    logger.debug(
        "Logging configured | env={} level={} log_dir={}",
        cfg.app_env,
        cfg.log_level,
        log_dir,
    )


def get_logger() -> object:
    """Return the shared loguru logger (after setup_logging)."""
    return logger
