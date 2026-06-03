"""Görevler + denetim kayıtları: tasks, task_instances, xp_events, point_transactions

Revision ID: 0002_tasks
Revises: 0001_initial
Create Date: 2026-06-03
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_tasks"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tasks",
        sa.Column("id", sa.String(length=26), primary_key=True),
        sa.Column("user_id", sa.String(length=26), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("recurrence", sa.String(length=10), nullable=False),
        sa.Column("reward_override", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "task_instances",
        sa.Column("id", sa.String(length=26), primary_key=True),
        sa.Column("task_id", sa.String(length=26), nullable=False),
        sa.Column("user_id", sa.String(length=26), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=10), nullable=False, server_default="pending"),
        sa.Column("committed_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("timer_running", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("segment_started_at", sa.DateTime(), nullable=True),
        sa.Column("reward_xp", sa.Integer(), nullable=True),
        sa.Column("reward_points", sa.Integer(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("task_id", "day", name="uq_instance_task_day"),
    )
    for table in ("xp_events", "point_transactions"):
        op.create_table(
            table,
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("user_id", sa.String(length=26), nullable=False),
            sa.Column("day", sa.Date(), nullable=False),
            sa.Column("source", sa.String(length=40), nullable=False),
            sa.Column("ref_id", sa.String(length=26), nullable=True),
            sa.Column("amount", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        )


def downgrade() -> None:
    op.drop_table("point_transactions")
    op.drop_table("xp_events")
    op.drop_table("task_instances")
    op.drop_table("tasks")
