"""Rutin alanları veri deposu (tanımlar + günlük değerler)."""

from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from leveltodo.infrastructure.persistence.sqlite.models import RoutineEntry, RoutineField


class SqlRutinRepository:
    def __init__(self, session_factory: sessionmaker) -> None:
        self._sf = session_factory

    # — Alan tanımları —
    def alan_ekle(
        self,
        *,
        id: str,
        user_id: str,
        name: str,
        kind: str,
        direction: str | None,
        target: int | None,
        reward_xp: int,
        stat: str,
        sort_order: int,
    ) -> None:
        with self._sf() as s:
            s.add(
                RoutineField(
                    id=id,
                    user_id=user_id,
                    name=name,
                    kind=kind,
                    direction=direction,
                    target=target,
                    reward_xp=reward_xp,
                    stat=stat,
                    sort_order=sort_order,
                )
            )
            s.commit()

    def aktif_alanlar(self, user_id: str) -> list[RoutineField]:
        with self._sf() as s:
            stmt = (
                select(RoutineField)
                .where(RoutineField.user_id == user_id, RoutineField.is_active.is_(True))
                .order_by(RoutineField.sort_order, RoutineField.created_at)
            )
            return list(s.scalars(stmt))

    def alan_getir(self, field_id: str) -> RoutineField | None:
        with self._sf() as s:
            return s.get(RoutineField, field_id)

    def alan_pasife_al(self, field_id: str) -> None:
        with self._sf() as s:
            alan = s.get(RoutineField, field_id)
            if alan is not None:
                alan.is_active = False
                s.commit()

    def sonraki_sira(self, user_id: str) -> int:
        with self._sf() as s:
            enbuyuk = s.scalar(
                select(func.max(RoutineField.sort_order)).where(
                    RoutineField.user_id == user_id
                )
            )
            return (enbuyuk or 0) + 1

    # — Günlük değerler —
    def gunluk_degerler(self, field_id: str, bas: date, bit: date) -> dict[date, int]:
        """Bir rutin alanının aralıktaki günlük sayısal değerleri {gun: deger}."""
        with self._sf() as s:
            stmt = (
                select(RoutineEntry.day, RoutineEntry.value)
                .where(
                    RoutineEntry.field_id == field_id,
                    RoutineEntry.day >= bas,
                    RoutineEntry.day <= bit,
                )
                .order_by(RoutineEntry.day)
            )
            return {gun: int(deger) for gun, deger in s.execute(stmt).all()}

    def gun_kaydi(self, field_id: str, day: date) -> RoutineEntry | None:
        with self._sf() as s:
            stmt = select(RoutineEntry).where(
                RoutineEntry.field_id == field_id, RoutineEntry.day == day
            )
            return s.scalar(stmt)

    def deger_yaz(
        self,
        *,
        id: str,
        field_id: str,
        user_id: str,
        day: date,
        value: int,
        rewarded: bool,
        value_text: str | None = None,
    ) -> None:
        """Alan+gün için değeri ekler ya da üzerine yazar (tek satır kalır)."""
        with self._sf() as s:
            kayit = s.scalar(
                select(RoutineEntry).where(
                    RoutineEntry.field_id == field_id, RoutineEntry.day == day
                )
            )
            if kayit is None:
                s.add(
                    RoutineEntry(
                        id=id,
                        field_id=field_id,
                        user_id=user_id,
                        day=day,
                        value=value,
                        value_text=value_text,
                        rewarded=rewarded,
                    )
                )
            else:
                kayit.value = value
                kayit.value_text = value_text
                kayit.rewarded = rewarded
            s.commit()
