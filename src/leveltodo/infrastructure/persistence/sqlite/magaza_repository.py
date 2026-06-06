"""Mağaza veri deposu — ödüller + satın alma geçmişi."""

from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from leveltodo.infrastructure.persistence.sqlite.models import StorePurchase, StoreReward


class SqlMagazaRepository:
    def __init__(self, session_factory: sessionmaker) -> None:
        self._sf = session_factory

    # — Ödüller —
    def odul_ekle(
        self, *, id: str, user_id: str, name: str, cost_per_min: int, sort_order: int
    ) -> None:
        with self._sf() as s:
            s.add(
                StoreReward(
                    id=id,
                    user_id=user_id,
                    name=name,
                    cost_per_min=cost_per_min,
                    sort_order=sort_order,
                )
            )
            s.commit()

    def odul_getir(self, odul_id: str) -> StoreReward | None:
        with self._sf() as s:
            return s.get(StoreReward, odul_id)

    def aktif_oduller(self, user_id: str) -> list[StoreReward]:
        with self._sf() as s:
            stmt = (
                select(StoreReward)
                .where(StoreReward.user_id == user_id, StoreReward.is_active.is_(True))
                .order_by(StoreReward.sort_order, StoreReward.created_at)
            )
            return list(s.scalars(stmt))

    def odul_pasife_al(self, odul_id: str) -> None:
        with self._sf() as s:
            odul = s.get(StoreReward, odul_id)
            if odul is not None:
                odul.is_active = False
                s.commit()

    def maliyet_guncelle(self, odul_id: str, cost_per_min: int) -> None:
        with self._sf() as s:
            odul = s.get(StoreReward, odul_id)
            if odul is not None:
                odul.cost_per_min = cost_per_min
                s.commit()

    def ad_onerileri(self, user_id: str) -> list[str]:
        with self._sf() as s:
            stmt = (
                select(StoreReward.name)
                .where(StoreReward.user_id == user_id)
                .order_by(StoreReward.created_at.desc())
            )
            gorulen: list[str] = []
            for (ad,) in s.execute(stmt).all():
                if ad not in gorulen:
                    gorulen.append(ad)
            return gorulen

    def son_odul_adli(self, user_id: str, ad: str) -> StoreReward | None:
        with self._sf() as s:
            stmt = (
                select(StoreReward)
                .where(StoreReward.user_id == user_id, StoreReward.name == ad)
                .order_by(StoreReward.created_at.desc())
                .limit(1)
            )
            return s.scalar(stmt)

    def sonraki_sira(self, user_id: str) -> int:
        with self._sf() as s:
            enbuyuk = s.scalar(
                select(func.max(StoreReward.sort_order)).where(StoreReward.user_id == user_id)
            )
            return (enbuyuk or 0) + 1

    # — Satın almalar —
    def satin_alma_ekle(
        self, *, id: str, user_id: str, reward_name: str, minutes: int, cost: int, day: date
    ) -> None:
        with self._sf() as s:
            s.add(
                StorePurchase(
                    id=id,
                    user_id=user_id,
                    reward_name=reward_name,
                    minutes=minutes,
                    cost=cost,
                    day=day,
                )
            )
            s.commit()

    def son_satin_almalar(self, user_id: str, limit: int = 50) -> list[StorePurchase]:
        with self._sf() as s:
            stmt = (
                select(StorePurchase)
                .where(StorePurchase.user_id == user_id)
                .order_by(StorePurchase.created_at.desc())
                .limit(limit)
            )
            return list(s.scalars(stmt))
