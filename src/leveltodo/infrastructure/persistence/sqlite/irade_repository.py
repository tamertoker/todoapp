"""İrade eylemleri veri deposu."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from leveltodo.infrastructure.persistence.sqlite.models import WillAct


class SqlIradeRepository:
    def __init__(self, session_factory: sessionmaker) -> None:
        self._sf = session_factory

    def ekle(
        self, *, id: str, user_id: str, day: date, title: str, xp: int, created_at: datetime
    ) -> None:
        with self._sf() as s:
            s.add(
                WillAct(
                    id=id, user_id=user_id, day=day, title=title, xp=xp, created_at=created_at
                )
            )
            s.commit()

    def son_eylemler(self, user_id: str, limit: int = 20) -> list[WillAct]:
        with self._sf() as s:
            stmt = (
                select(WillAct)
                .where(WillAct.user_id == user_id)
                .order_by(WillAct.created_at.desc())
                .limit(limit)
            )
            return list(s.scalars(stmt))

    def baslik_onerileri(self, user_id: str) -> list[str]:
        with self._sf() as s:
            stmt = (
                select(WillAct.title)
                .where(WillAct.user_id == user_id)
                .order_by(WillAct.created_at.desc())
            )
            gorulen: list[str] = []
            for (baslik,) in s.execute(stmt).all():
                if baslik not in gorulen:
                    gorulen.append(baslik)
            return gorulen

    def son_eylem_baslikli(self, user_id: str, baslik: str) -> WillAct | None:
        with self._sf() as s:
            stmt = (
                select(WillAct)
                .where(WillAct.user_id == user_id, WillAct.title == baslik)
                .order_by(WillAct.created_at.desc())
                .limit(1)
            )
            return s.scalar(stmt)
