"""Seans (session) veri deposu."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import delete, func, select
from sqlalchemy.orm import sessionmaker

from leveltodo.infrastructure.persistence.sqlite.models import Session


class SqlSeansRepository:
    def __init__(self, session_factory: sessionmaker) -> None:
        self._sf = session_factory

    def ac(self, *, id: str, instance_id: str, user_id: str, day: date, start_at: datetime) -> None:
        with self._sf() as s:
            s.add(
                Session(
                    id=id,
                    instance_id=instance_id,
                    user_id=user_id,
                    day=day,
                    start_at=start_at,
                )
            )
            s.commit()

    def kapat(self, instance_id: str, end_at: datetime, duration: int) -> None:
        """Açık (bitmemiş) seansı kapatır: bitiş + süre yazar."""
        with self._sf() as s:
            stmt = (
                select(Session)
                .where(Session.instance_id == instance_id, Session.end_at.is_(None))
                .order_by(Session.start_at.desc())
                .limit(1)
            )
            seans = s.scalar(stmt)
            if seans is not None:
                seans.end_at = end_at
                seans.duration = duration
                s.commit()

    def gun_seanslari(self, instance_id: str, day: date) -> list[Session]:
        with self._sf() as s:
            stmt = (
                select(Session)
                .where(Session.instance_id == instance_id, Session.day == day)
                .order_by(Session.start_at)
            )
            return list(s.scalars(stmt))

    def gun_seans_sayisi(self, instance_id: str, day: date) -> int:
        with self._sf() as s:
            return int(
                s.scalar(
                    select(func.count())
                    .select_from(Session)
                    .where(Session.instance_id == instance_id, Session.day == day)
                )
            )

    def seans_sil(self, seans_id: str) -> None:
        with self._sf() as s:
            seans = s.get(Session, seans_id)
            if seans is not None:
                s.delete(seans)
                s.commit()

    def acik_seanslari_sil(self, user_id: str) -> None:
        """Açılışta: bitmemiş (çökme/kapanmadan kalan) seansları temizler."""
        with self._sf() as s:
            s.execute(
                delete(Session).where(Session.user_id == user_id, Session.end_at.is_(None))
            )
            s.commit()
