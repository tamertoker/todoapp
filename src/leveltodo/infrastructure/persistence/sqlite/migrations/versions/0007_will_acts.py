"""İrade eylemleri: will_acts tablosu (Disiplin statını besler)

Revision ID: 0007_will_acts
Revises: 0006_task_streak
Create Date: 2026-06-04
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007_will_acts"
down_revision: str | None = "0006_task_streak"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "will_acts",
        sa.Column("id", sa.String(length=26), primary_key=True),
        sa.Column("user_id", sa.String(length=26), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("xp", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    op.drop_table("will_acts")
