"""Göreve hedef çalışma süresi (mikro ilerleme barı için)

Revision ID: 0018_gorev_hedef_sure
Revises: 0017_seans_odul_hatirlatma
Create Date: 2026-06-09
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0018_gorev_hedef_sure"
down_revision: str | None = "0017_seans_odul_hatirlatma"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("tasks", sa.Column("hedef_sure", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("tasks", "hedef_sure")
