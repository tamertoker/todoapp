"""Seriler: streaks tablosu (giriş + görev serileri tek tabloda)

Revision ID: 0005_streaks
Revises: 0004_recurrence_param
Create Date: 2026-06-04
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_streaks"
down_revision: str | None = "0004_recurrence_param"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "streaks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(length=26), nullable=False),
        sa.Column("type", sa.String(length=10), nullable=False),
        sa.Column("current_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("best_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_day", sa.Date(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "type", name="uq_streak_user_type"),
    )


def downgrade() -> None:
    op.drop_table("streaks")
