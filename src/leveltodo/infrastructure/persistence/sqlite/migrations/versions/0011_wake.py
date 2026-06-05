"""Uyandırma disiplini: wake_logs

Revision ID: 0011_wake
Revises: 0010_routine_text
Create Date: 2026-06-05
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0011_wake"
down_revision: str | None = "0010_routine_text"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "wake_logs",
        sa.Column("id", sa.String(length=26), primary_key=True),
        sa.Column("user_id", sa.String(length=26), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("hedef", sa.String(length=5), nullable=False),
        sa.Column("gercek", sa.String(length=5), nullable=False),
        sa.Column("basarili", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "day", name="uq_wake_user_day"),
    )


def downgrade() -> None:
    op.drop_table("wake_logs")
