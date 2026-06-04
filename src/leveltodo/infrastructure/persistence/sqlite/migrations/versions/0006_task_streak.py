"""Göreve özel seri: tasks.streak_count + tasks.streak_last_day

Revision ID: 0006_task_streak
Revises: 0005_streaks
Create Date: 2026-06-04
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006_task_streak"
down_revision: str | None = "0005_streaks"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "tasks", sa.Column("streak_count", sa.Integer(), nullable=False, server_default="0")
    )
    op.add_column("tasks", sa.Column("streak_last_day", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("tasks", "streak_last_day")
    op.drop_column("tasks", "streak_count")
