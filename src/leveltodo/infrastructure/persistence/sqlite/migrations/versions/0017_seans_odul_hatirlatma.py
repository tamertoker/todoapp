"""Seans ödülü (geri alma için) + görev hatırlatması

Revision ID: 0017_seans_odul_hatirlatma
Revises: 0016_sessions
Create Date: 2026-06-05
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0017_seans_odul_hatirlatma"
down_revision: str | None = "0016_sessions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "sessions", sa.Column("reward_xp", sa.Integer(), nullable=False, server_default="0")
    )
    op.add_column(
        "sessions", sa.Column("reward_points", sa.Integer(), nullable=False, server_default="0")
    )
    op.add_column("tasks", sa.Column("reminder", sa.String(length=5), nullable=True))
    op.add_column("tasks", sa.Column("reminder_last", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("tasks", "reminder_last")
    op.drop_column("tasks", "reminder")
    op.drop_column("sessions", "reward_points")
    op.drop_column("sessions", "reward_xp")
