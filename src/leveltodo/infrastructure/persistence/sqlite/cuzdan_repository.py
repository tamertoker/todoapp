"""Cüzdan veri deposu — işlemler (gelir/gider) + wishlist öğeleri."""

from __future__ import annotations

from datetime import date

from sqlalchemy import extract, func, select
from sqlalchemy.orm import sessionmaker

from leveltodo.infrastructure.persistence.sqlite.models import WalletTransaction, WishlistItem


class SqlCuzdanRepository:
    def __init__(self, session_factory: sessionmaker) -> None:
        self._sf = session_factory

    # — İşlemler —
    def islem_ekle(
        self, *, id: str, user_id: str, day: date, amount: int, tur: str, aciklama: str
    ) -> None:
        with self._sf() as s:
            s.add(
                WalletTransaction(
                    id=id, user_id=user_id, day=day, amount=amount, tur=tur, aciklama=aciklama
                )
            )
            s.commit()

    def islem_sil(self, islem_id: str) -> None:
        with self._sf() as s:
            islem = s.get(WalletTransaction, islem_id)
            if islem is not None:
                s.delete(islem)
                s.commit()

    def _tur_toplami(self, s, user_id: str, tur: str) -> int:
        return int(
            s.scalar(
                select(func.coalesce(func.sum(WalletTransaction.amount), 0)).where(
                    WalletTransaction.user_id == user_id, WalletTransaction.tur == tur
                )
            )
        )

    def bakiye(self, user_id: str) -> int:
        with self._sf() as s:
            return self._tur_toplami(s, user_id, "gelir") - self._tur_toplami(s, user_id, "gider")

    def ay_toplamlari(self, user_id: str, yil: int, ay: int) -> tuple[int, int]:
        """O ayki (gelir_kurus, gider_kurus)."""
        with self._sf() as s:
            stmt = (
                select(
                    WalletTransaction.tur,
                    func.coalesce(func.sum(WalletTransaction.amount), 0),
                )
                .where(
                    WalletTransaction.user_id == user_id,
                    extract("year", WalletTransaction.day) == yil,
                    extract("month", WalletTransaction.day) == ay,
                )
                .group_by(WalletTransaction.tur)
            )
            toplam = {tur: int(t) for tur, t in s.execute(stmt).all()}
            return toplam.get("gelir", 0), toplam.get("gider", 0)

    def son_islemler(self, user_id: str, limit: int = 50) -> list[WalletTransaction]:
        with self._sf() as s:
            stmt = (
                select(WalletTransaction)
                .where(WalletTransaction.user_id == user_id)
                .order_by(WalletTransaction.day.desc(), WalletTransaction.created_at.desc())
                .limit(limit)
            )
            return list(s.scalars(stmt))

    def aciklama_onerileri(self, user_id: str) -> list[str]:
        with self._sf() as s:
            stmt = (
                select(WalletTransaction.aciklama)
                .where(WalletTransaction.user_id == user_id, WalletTransaction.aciklama != "")
                .order_by(WalletTransaction.created_at.desc())
            )
            gorulen: list[str] = []
            for (aciklama,) in s.execute(stmt).all():
                if aciklama not in gorulen:
                    gorulen.append(aciklama)
            return gorulen

    def son_islem_aciklamali(self, user_id: str, aciklama: str) -> WalletTransaction | None:
        with self._sf() as s:
            stmt = (
                select(WalletTransaction)
                .where(
                    WalletTransaction.user_id == user_id,
                    WalletTransaction.aciklama == aciklama,
                )
                .order_by(WalletTransaction.created_at.desc())
                .limit(1)
            )
            return s.scalar(stmt)

    # — Wishlist —
    def wishlist_ekle(
        self,
        *,
        id: str,
        user_id: str,
        name: str,
        price: int,
        image_path: str | None,
        sort_order: int,
    ) -> None:
        with self._sf() as s:
            s.add(
                WishlistItem(
                    id=id,
                    user_id=user_id,
                    name=name,
                    price=price,
                    image_path=image_path,
                    sort_order=sort_order,
                )
            )
            s.commit()

    def wishlist_aktif(self, user_id: str) -> list[WishlistItem]:
        with self._sf() as s:
            stmt = (
                select(WishlistItem)
                .where(WishlistItem.user_id == user_id, WishlistItem.is_active.is_(True))
                .order_by(WishlistItem.sort_order, WishlistItem.created_at)
            )
            return list(s.scalars(stmt))

    def wishlist_pasife_al(self, oge_id: str) -> None:
        with self._sf() as s:
            oge = s.get(WishlistItem, oge_id)
            if oge is not None:
                oge.is_active = False
                s.commit()

    def wishlist_ad_onerileri(self, user_id: str) -> list[str]:
        with self._sf() as s:
            stmt = (
                select(WishlistItem.name)
                .where(WishlistItem.user_id == user_id)
                .order_by(WishlistItem.created_at.desc())
            )
            gorulen: list[str] = []
            for (ad,) in s.execute(stmt).all():
                if ad not in gorulen:
                    gorulen.append(ad)
            return gorulen

    def son_wishlist_adli(self, user_id: str, ad: str) -> WishlistItem | None:
        with self._sf() as s:
            stmt = (
                select(WishlistItem)
                .where(WishlistItem.user_id == user_id, WishlistItem.name == ad)
                .order_by(WishlistItem.created_at.desc())
                .limit(1)
            )
            return s.scalar(stmt)

    def wishlist_sonraki_sira(self, user_id: str) -> int:
        with self._sf() as s:
            enbuyuk = s.scalar(
                select(func.max(WishlistItem.sort_order)).where(WishlistItem.user_id == user_id)
            )
            return (enbuyuk or 0) + 1
