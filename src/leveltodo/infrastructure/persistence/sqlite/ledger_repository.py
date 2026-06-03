"""XP/puan defteri.

Kazanılan her XP ve puan ayrı birer satır olarak yazılır (xp_events,
point_transactions). Bu, "neyi ne zaman kazandın" geçmişini ve ileride
grafikleri besler. Toplamlar bu satırların toplanmasıyla bulunur — tek
doğruluk kaynağı budur, ayrı bir 'bakiye' alanı tutulmaz.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from leveltodo.infrastructure.persistence.sqlite.models import PointTransaction, XpEvent


class SqlLedgerRepository:
    def __init__(self, session_factory: sessionmaker) -> None:
        self._sf = session_factory

    def record(
        self, *, user_id: str, day: date, source: str, ref_id: str | None, xp: int, points: int
    ) -> None:
        with self._sf() as s:
            s.add(XpEvent(user_id=user_id, day=day, source=source, ref_id=ref_id, amount=xp))
            s.add(
                PointTransaction(
                    user_id=user_id, day=day, source=source, ref_id=ref_id, amount=points
                )
            )
            s.commit()

    def totals(self, user_id: str) -> tuple[int, int]:
        with self._sf() as s:
            xp = s.scalar(
                select(func.coalesce(func.sum(XpEvent.amount), 0)).where(
                    XpEvent.user_id == user_id
                )
            )
            points = s.scalar(
                select(func.coalesce(func.sum(PointTransaction.amount), 0)).where(
                    PointTransaction.user_id == user_id
                )
            )
            return int(xp), int(points)
