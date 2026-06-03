"""Esnek tekrar parametresi: tasks.recurrence_param

Revision ID: 0004_recurrence_param
Revises: 0003_stats
Create Date: 2026-06-04
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_recurrence_param"
down_revision: str | None = "0003_stats"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("tasks", sa.Column("recurrence_param", sa.String(length=60), nullable=True))


def downgrade() -> None:
    op.drop_column("tasks", "recurrence_param")
