"""Seri (streak) veri deposu."""

from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from leveltodo.infrastructure.persistence.sqlite.models import Streak


class SqlStreakRepository:
    def __init__(self, session_factory: sessionmaker) -> None:
        self._sf = session_factory

    def getir(self, user_id: str, tip: str) -> Streak | None:
        with self._sf() as s:
            return s.scalar(
                select(Streak).where(Streak.user_id == user_id, Streak.type == tip)
            )

    def upsert(
        self, user_id: str, tip: str, mevcut: int, en_iyi: int, son_gun: date
    ) -> None:
        with self._sf() as s:
            satir = s.scalar(
                select(Streak).where(Streak.user_id == user_id, Streak.type == tip)
            )
            if satir is None:
                s.add(
                    Streak(
                        user_id=user_id,
                        type=tip,
                        current_count=mevcut,
                        best_count=en_iyi,
                        last_day=son_gun,
                    )
                )
            else:
                satir.current_count = mevcut
                satir.best_count = en_iyi
                satir.last_day = son_gun
            s.commit()

    def hepsi(self, user_id: str) -> dict[str, tuple[int, int]]:
        """{tip: (mevcut, en_iyi)}."""
        with self._sf() as s:
            satirlar = s.scalars(select(Streak).where(Streak.user_id == user_id))
            return {r.type: (r.current_count, r.best_count) for r in satirlar}
