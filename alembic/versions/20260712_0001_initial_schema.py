"""Initial schema: 16 tables + calendar + set_updated_at triggers.

Revision ID: 20260712_0001
Revises:
Create Date: 2026-07-12

Schema follows docs/database-design.md.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from app.models import UPDATED_AT_TABLES, Base

# revision identifiers, used by Alembic.
revision: str = "20260712_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SET_UPDATED_AT_FN = """
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""


def upgrade() -> None:
    """Create all tables from SQLAlchemy metadata and attach updated_at triggers."""
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)

    op.execute(sa.text(SET_UPDATED_AT_FN))

    for table_name in UPDATED_AT_TABLES:
        op.execute(
            sa.text(
                f"""
                DROP TRIGGER IF EXISTS trg_{table_name}_set_updated_at ON {table_name};
                CREATE TRIGGER trg_{table_name}_set_updated_at
                    BEFORE UPDATE ON {table_name}
                    FOR EACH ROW
                    EXECUTE PROCEDURE set_updated_at();
                """
            )
        )


def downgrade() -> None:
    """Drop triggers, function, then all tables."""
    for table_name in UPDATED_AT_TABLES:
        op.execute(
            sa.text(f"DROP TRIGGER IF EXISTS trg_{table_name}_set_updated_at ON {table_name};")
        )

    op.execute(sa.text("DROP FUNCTION IF EXISTS set_updated_at() CASCADE;"))

    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
