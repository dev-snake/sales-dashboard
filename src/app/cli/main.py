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
    scale: str = typer.Option("100", "--scale", help="Scale: 100 | 1k | 10k | 100k | 1m"),
    seed: int = typer.Option(42, "--seed", help="Random seed for reproducibility"),
    locale: str = typer.Option("vi_VN", "--locale", help="Faker locale"),
    reset: bool = typer.Option(False, "--reset", help="TRUNCATE all tables before seed"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation when --reset"),
    export_samples: bool = typer.Option(
        True,
        "--export-samples/--no-export-samples",
        help="Write ETL sample files under datasets/raw/samples/",
    ),
) -> None:
    """Generate synthetic seed data into PostgreSQL."""
    from app.database.engine import dispose_engine, get_engine
    from app.database.session import reset_session_factory, session_scope
    from app.seed.scale_config import get_scale_config
    from app.services.seed_service import SeedService

    try:
        config = get_scale_config(scale)
    except ValueError as exc:
        typer.echo(f"ERROR — {exc}", err=True)
        raise typer.Exit(code=2) from exc

    if reset and not yes:
        typer.confirm(
            f"This will TRUNCATE all business tables then seed scale={config.name}. Continue?",
            abort=True,
        )

    typer.echo(f"Seeding scale={config.name} orders={config.orders} seed={seed} reset={reset} …")
    # Ensure fresh engine if settings changed
    dispose_engine()
    reset_session_factory()
    _ = get_engine()

    try:
        with session_scope(commit=False) as session:
            service = SeedService(session)
            result = service.run(
                scale=config.name,
                seed=seed,
                locale=locale,
                reset=reset,
                export_samples=export_samples,
            )
        typer.echo(f"OK — seed finished in {result.duration_seconds:.1f}s")
        for key, value in sorted(result.counts.items()):
            typer.echo(f"  {key}: {value}")
        logger.info("Seed CLI completed | {}", result.counts)
    except Exception as exc:
        logger.exception("Seed failed")
        typer.echo(f"ERROR — seed failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc


@seed_app.command("samples")
def seed_samples() -> None:
    """Export ETL sample files only (no database writes)."""
    from app.seed.sample_export import export_etl_samples

    path = export_etl_samples()
    typer.echo(f"OK — samples written to {path}")


@report_app.command("generate")
def report_generate(
    report_type: str = typer.Option("monthly", "--type", help="daily|weekly|monthly|..."),
    fmt: str = typer.Option("excel", "--format", help="excel|pdf|both"),
) -> None:
    """Report generation — not implemented in scaffold phase."""
    typer.echo(f"Reports not implemented yet (Phase 9). type={report_type} format={fmt}")


@sql_app.command("list")
def sql_list(
    level: str | None = typer.Option(
        None,
        "--level",
        "-l",
        help="Filter: basic | intermediate | advanced | reporting | optimization",
    ),
) -> None:
    """List SQL catalog entries."""
    from app.sql_catalog import list_entries

    try:
        entries = list_entries(level=level.lower() if level else None)
    except Exception as exc:
        typer.echo(f"ERROR — {exc}", err=True)
        raise typer.Exit(code=1) from exc

    if not entries:
        typer.echo("No SQL entries found.")
        raise typer.Exit(code=0)

    typer.echo(f"{'ID':<6} {'Level':<14} {'Title'}")
    typer.echo("-" * 60)
    for e in entries:
        typer.echo(f"{e.id:<6} {e.level:<14} {e.title}")
    typer.echo(f"\nTotal: {len(entries)}")


@sql_app.command("show")
def sql_show(query_id: str = typer.Argument(..., help="Query id, e.g. R04 or B01")) -> None:
    """Print SQL text for a catalog entry."""
    from app.sql_catalog import load_entry

    try:
        entry = load_entry(query_id)
    except KeyError as exc:
        typer.echo(f"ERROR — {exc}", err=True)
        raise typer.Exit(code=2) from exc

    typer.echo(f"-- {entry.id}: {entry.title}")
    typer.echo(f"-- File: {entry.path}")
    typer.echo(f"-- Skills: {entry.skills}")
    typer.echo(f"-- Tables: {entry.tables}")
    typer.echo("")
    typer.echo(entry.sql)


@sql_app.command("run")
def sql_run(
    query_id: str = typer.Argument(..., help="Query id, e.g. R04"),
    limit: int | None = typer.Option(
        None,
        "--limit",
        "-n",
        help="Optional max rows to print (client-side truncate)",
    ),
) -> None:
    """Execute a catalog SQL query against PostgreSQL and print rows."""
    from sqlalchemy import text

    from app.database.engine import get_engine
    from app.sql_catalog import load_entry

    try:
        entry = load_entry(query_id)
    except KeyError as exc:
        typer.echo(f"ERROR — {exc}", err=True)
        raise typer.Exit(code=2) from exc

    # Skip pure comment / multi-statement lab notes carefully: execute full text
    sql_text = entry.sql
    if not sql_text.strip():
        typer.echo("ERROR — empty SQL body", err=True)
        raise typer.Exit(code=1)

    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text(sql_text))
            if not result.returns_rows:
                typer.echo("OK — statement executed (no rows returned).")
                return
            rows = result.fetchall()
            keys = list(result.keys())
    except Exception as exc:
        logger.exception("SQL run failed | id={}", query_id)
        typer.echo(f"ERROR — query failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(" | ".join(keys))
    typer.echo("-" * 80)
    shown = rows if limit is None else rows[:limit]
    for row in shown:
        typer.echo(" | ".join(str(v) for v in row))
    typer.echo(f"\nRows: {len(rows)}" + (f" (showing {len(shown)})" if limit else ""))


def run() -> None:
    """Entry point for ``python -m app.cli.main``."""
    app()


if __name__ == "__main__":
    run()
