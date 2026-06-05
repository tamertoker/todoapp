"""Uyandırma kayıtları veri deposu (gün başına tek satır)."""

from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from leveltodo.infrastructure.persistence.sqlite.models import WakeLog


class SqlUyandirmaRepository:
    def __init__(self, session_factory: sessionmaker) -> None:
        self._sf = session_factory

    def gun_kaydi(self, user_id: str, day: date) -> WakeLog | None:
        with self._sf() as s:
            stmt = select(WakeLog).where(WakeLog.user_id == user_id, WakeLog.day == day)
            return s.scalar(stmt)

    def kaydet(
        self, *, id: str, user_id: str, day: date, hedef: str, gercek: str, basarili: bool
    ) -> None:
        with self._sf() as s:
            kayit = s.scalar(
                select(WakeLog).where(WakeLog.user_id == user_id, WakeLog.day == day)
            )
            if kayit is None:
                s.add(
                    WakeLog(
                        id=id,
                        user_id=user_id,
                        day=day,
                        hedef=hedef,
                        gercek=gercek,
                        basarili=basarili,
                    )
                )
            else:
                kayit.hedef = hedef
                kayit.gercek = gercek
                kayit.basarili = basarili
            s.commit()
