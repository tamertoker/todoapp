"""Özel stat veri deposu."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from leveltodo.infrastructure.persistence.sqlite.models import CustomStat


class SqlStatRepository:
    def __init__(self, session_factory: sessionmaker) -> None:
        self._sf = session_factory

    def ekle(self, *, id: str, user_id: str, name: str, sort_order: int) -> None:
        with self._sf() as s:
            s.add(CustomStat(id=id, user_id=user_id, name=name, sort_order=sort_order))
            s.commit()

    def aktif(self, user_id: str) -> list[CustomStat]:
        with self._sf() as s:
            stmt = (
                select(CustomStat)
                .where(CustomStat.user_id == user_id, CustomStat.is_active.is_(True))
                .order_by(CustomStat.sort_order, CustomStat.created_at)
            )
            return list(s.scalars(stmt))

    def pasife_al(self, stat_id: str) -> None:
        with self._sf() as s:
            stat = s.get(CustomStat, stat_id)
            if stat is not None:
                stat.is_active = False
                s.commit()

    def sonraki_sira(self, user_id: str) -> int:
        with self._sf() as s:
            enbuyuk = s.scalar(
                select(func.max(CustomStat.sort_order)).where(CustomStat.user_id == user_id)
            )
            return (enbuyuk or 0) + 1
