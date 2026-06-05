"""Rutin metin türü: routine_entries.value_text

Revision ID: 0010_routine_text
Revises: 0009_journal
Create Date: 2026-06-05
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0010_routine_text"
down_revision: str | None = "0009_journal"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("routine_entries", sa.Column("value_text", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("routine_entries", "value_text")
