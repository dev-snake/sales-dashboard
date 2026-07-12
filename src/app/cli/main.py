"""Typer CLI skeleton — commands are stubs until later phases."""

from __future__ import annotations

import typer
from loguru import logger
from sqlalchemy import text

from app import __version__
from app.config import get_settings
from app.utils.logging import setup_logging
from app.utils.paths import ensure_runtime_dirs

app = typer.Typer(
    name="sales-dashboard",
    help="Sales Analytics Dashboard CLI (scaffold — business commands come later).",
    add_completion=False,
    no_args_is_help=True,
)

db_app = typer.Typer(help="Database utilities")
etl_app = typer.Typer(help="ETL pipeline (stub)")
seed_app = typer.Typer(help="Seed data (stub)")
report_app = typer.Typer(help="Reports (stub)")
sql_app = typer.Typer(help="SQL catalog runner (stub)")

app.add_typer(db_app, name="db")
app.add_typer(etl_app, name="etl")
app.add_typer(seed_app, name="seed")
app.add_typer(report_app, name="report")
app.add_typer(sql_app, name="sql")


def _mask_database_url(url: str) -> str:
    """Hide password segment of a SQLAlchemy URL for safe display."""
    if "@" not in url or "://" not in url:
        return url
    scheme, rest = url.split("://", 1)
    if "@" not in rest:
        return url
    creds, hostpart = rest.split("@", 1)
    user = creds.split(":", 1)[0]
    return f"{scheme}://{user}:***@{hostpart}"


@app.callback()
def main_callback(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable DEBUG logging"),
) -> None:
    """Global options applied before every command."""
    settings = get_settings()
    if verbose:
        object.__setattr__(settings, "log_level", "DEBUG")
    setup_logging(settings)
    ensure_runtime_dirs()


@app.command("version")
def version_cmd() -> None:
    """Print application version."""
    typer.echo(f"sales-dashboard v{__version__}")


@app.command("info")
def info_cmd() -> None:
    """Show runtime configuration summary (password masked)."""
    settings = get_settings()
    typer.echo("Sales Analytics Dashboard — scaffold")
    typer.echo(f"  version     : {__version__}")
    typer.echo(f"  app_env     : {settings.app_env}")
    typer.echo(f"  log_level   : {settings.log_level}")
    typer.echo(f"  database_url: {_mask_database_url(settings.database_url)}")
    typer.echo(f"  project_root: {settings.project_root}")
    typer.echo(f"  datasets    : {settings.datasets_path}")
    typer.echo(f"  logs        : {settings.logs_path}")
    typer.echo(f"  exports     : {settings.exports_path}")
    typer.echo(f"  currency    : {settings.default_currency}")


@db_app.command("ping")
def db_ping() -> None:
    """Test PostgreSQL connectivity with SELECT 1."""
    from app.database.engine import get_engine
    from app.utils.errors import DatabaseError

    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar_one()
        if result != 1:
            raise DatabaseError("Unexpected ping result", details={"result": result})
        typer.echo("OK — database connection successful")
        logger.info("Database ping succeeded")
    except DatabaseError:
        raise
    except Exception as exc:
        logger.exception("Database ping failed")
        typer.echo(f"ERROR — database connection failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc


def _alembic_config() -> object:
    """Build Alembic Config rooted at the project directory."""
    from alembic.config import Config

    from app.config.settings import PROJECT_ROOT

    cfg = Config(str(PROJECT_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(PROJECT_ROOT / "alembic"))
    return cfg


@db_app.command("migrate")
def db_migrate(
    revision: str = typer.Option("head", help="Target revision (default: head)"),
) -> None:
    """Apply Alembic migrations (upgrade)."""
    from alembic import command

    from app.utils.errors import DatabaseError

    try:
        command.upgrade(_alembic_config(), revision)  # type: ignore[arg-type]
        typer.echo(f"OK — migrated to {revision}")
        logger.info("Alembic upgrade to {}", revision)
    except Exception as exc:
        logger.exception("Alembic upgrade failed")
        typer.echo(f"ERROR — migration failed: {exc}", err=True)
        raise typer.Exit(code=1) from DatabaseError(str(exc))


@db_app.command("downgrade")
def db_downgrade(
    revision: str = typer.Option("-1", help="Target revision (default: -1 = one step)"),
) -> None:
    """Roll back Alembic migrations."""
    from alembic import command

    try:
        command.downgrade(_alembic_config(), revision)  # type: ignore[arg-type]
        typer.echo(f"OK — downgraded to {revision}")
        logger.info("Alembic downgrade to {}", revision)
    except Exception as exc:
        logger.exception("Alembic downgrade failed")
        typer.echo(f"ERROR — downgrade failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc


@db_app.command("current")
def db_current() -> None:
    """Show current Alembic revision."""
    from alembic import command

    try:
        command.current(_alembic_config())  # type: ignore[arg-type]
    except Exception as exc:
        logger.exception("Alembic current failed")
        typer.echo(f"ERROR — {exc}", err=True)
        raise typer.Exit(code=1) from exc


@db_app.command("tables")
def db_tables() -> None:
    """List ORM table names registered in metadata."""
    from app.models import Base

    names = sorted(Base.metadata.tables.keys())
    typer.echo(f"Registered tables ({len(names)}):")
    for name in names:
        typer.echo(f"  - {name}")


@etl_app.command("run")
def etl_run() -> None:
    """ETL run — not implemented in scaffold phase."""
    typer.echo("ETL not implemented yet (see Phase 5).")


@seed_app.command("run")
def seed_run(
    scale: str = typer.Option("100", help="Scale tier: 100 | 1k | 10k | 100k | 1m"),
) -> None:
    """Seed data — not implemented in scaffold phase."""
    typer.echo(f"Seed not implemented yet (Phase 3). Requested scale={scale}")


@report_app.command("generate")
def report_generate(
    report_type: str = typer.Option("monthly", "--type", help="daily|weekly|monthly|..."),
    fmt: str = typer.Option("excel", "--format", help="excel|pdf|both"),
) -> None:
    """Report generation — not implemented in scaffold phase."""
    typer.echo(f"Reports not implemented yet (Phase 9). type={report_type} format={fmt}")


@sql_app.command("list")
def sql_list() -> None:
    """List SQL catalog entries — not implemented yet."""
    typer.echo("SQL catalog runner not implemented yet (Phase 4).")


def run() -> None:
    """Entry point for ``python -m app.cli.main``."""
    app()


if __name__ == "__main__":
    run()
