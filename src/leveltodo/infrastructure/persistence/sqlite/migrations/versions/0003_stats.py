"""Statlar: tasks.stat + xp_events.stat kolonları

Revision ID: 0003_stats
Revises: 0002_tasks
Create Date: 2026-06-03
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_stats"
down_revision: str | None = "0002_tasks"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("tasks", sa.Column("stat", sa.String(length=20), nullable=True))
    op.add_column("xp_events", sa.Column("stat", sa.String(length=20), nullable=True))


def downgrade() -> None:
    op.drop_column("xp_events", "stat")
    op.drop_column("tasks", "stat")
