"""Seanslar: sessions tablosu

Revision ID: 0016_sessions
Revises: 0015_custom_stats
Create Date: 2026-06-05
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0016_sessions"
down_revision: str | None = "0015_custom_stats"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sessions",
        sa.Column("id", sa.String(length=26), primary_key=True),
        sa.Column("instance_id", sa.String(length=26), nullable=False),
        sa.Column("user_id", sa.String(length=26), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("start_at", sa.DateTime(), nullable=False),
        sa.Column("end_at", sa.DateTime(), nullable=True),
        sa.Column("duration", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["instance_id"], ["task_instances.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    op.drop_table("sessions")
