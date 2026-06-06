"""Cüzdan servisi — gerçek para (uygulama-içi Puan'dan ayrı).

Gelir/gider işlemleri, bakiye, aylık iki hedef (tasarruf hedefi + harcama bütçesi)
ve wishlist'i yönetir. Wishlist ilerlemesi cüzdan bakiyesinin öğe fiyatına oranıdır
(ayrı kumbara yok; tüm öğeler aynı bakiyeyi paylaşır). Tüm tutarlar KURUŞ.
"""

from __future__ import annotations

from dataclasses import dataclass

from leveltodo.domain.cuzdan.cuzdan import ilerleme_orani
from leveltodo.domain.time.gun import Gun
from leveltodo.domain.time.saat import Saat
from leveltodo.infrastructure.persistence.sqlite.cuzdan_repository import SqlCuzdanRepository
from leveltodo.infrastructure.persistence.sqlite.models import DEFAULT_USER_ID, WalletTransaction
from leveltodo.shared.ids import new_id

_TASARRUF = "tasarruf_hedefi"
_BUTCE = "harcama_butcesi"


@dataclass(frozen=True, slots=True)
class AylikOzet:
    bu_ay_gelir: int
    bu_ay_gider: int
    tasarruf: int  # bu_ay_gelir - bu_ay_gider
    tasarruf_hedefi: int
    harcama_butcesi: int


@dataclass(frozen=True, slots=True)
class WishlistSatiri:
    id: str
    ad: str
    fiyat: int
    resim_yolu: str | None
    oran: float  # 0..1


class CuzdanServisi:
    def __init__(
        self,
        cuzdan_repo: SqlCuzdanRepository,
        settings,
        saat: Saat,
        gun_baslangic_getir,
        user_id: str = DEFAULT_USER_ID,
    ) -> None:
        self._repo = cuzdan_repo
        self._settings = settings
        self._saat = saat
        self._gun_baslangic = gun_baslangic_getir
        self._user_id = user_id

    def _bugun(self):
        return Gun.olustur(self._saat.simdi(), self._gun_baslangic()).tarih

    # — İşlemler —
    def islem_ekle(self, miktar_kurus: int, tur: str, aciklama: str = "") -> None:
        if miktar_kurus <= 0 or tur not in ("gelir", "gider"):
            return
        self._repo.islem_ekle(
            id=new_id(),
            user_id=self._user_id,
            day=self._bugun(),
            amount=miktar_kurus,
            tur=tur,
            aciklama=aciklama.strip(),
        )

    def islem_sil(self, islem_id: str) -> None:
        self._repo.islem_sil(islem_id)

    def bakiye(self) -> int:
        return self._repo.bakiye(self._user_id)

    def son_islemler(self) -> list[WalletTransaction]:
        return self._repo.son_islemler(self._user_id)

    def aciklama_onerileri(self) -> list[str]:
        return self._repo.aciklama_onerileri(self._user_id)

    def islem_oneri(self, aciklama: str):
        """Verilen açıklamalı son işlem (autofill: tutar+tür için). Yoksa None."""
        return self._repo.son_islem_aciklamali(self._user_id, aciklama)

    def aylik_ozet(self) -> AylikOzet:
        bugun = self._bugun()
        gelir, gider = self._repo.ay_toplamlari(self._user_id, bugun.year, bugun.month)
        return AylikOzet(
            bu_ay_gelir=gelir,
            bu_ay_gider=gider,
            tasarruf=gelir - gider,
            tasarruf_hedefi=int(self._settings.get(_TASARRUF)),
            harcama_butcesi=int(self._settings.get(_BUTCE)),
        )

    def hedefler_ayarla(self, tasarruf_hedefi: int, harcama_butcesi: int) -> None:
        self._settings.set(_TASARRUF, max(0, tasarruf_hedefi))
        self._settings.set(_BUTCE, max(0, harcama_butcesi))

    # — Wishlist —
    def wishlist_ekle(self, ad: str, fiyat_kurus: int, resim_yolu: str | None = None) -> None:
        ad = ad.strip()
        if not ad or fiyat_kurus <= 0:
            return
        self._repo.wishlist_ekle(
            id=new_id(),
            user_id=self._user_id,
            name=ad,
            price=fiyat_kurus,
            image_path=resim_yolu,
            sort_order=self._repo.wishlist_sonraki_sira(self._user_id),
        )

    def wishlist_sil(self, oge_id: str) -> None:
        self._repo.wishlist_pasife_al(oge_id)

    def wishlist_ad_onerileri(self) -> list[str]:
        return self._repo.wishlist_ad_onerileri(self._user_id)

    def wishlist_oneri(self, ad: str):
        """Verilen adlı son wishlist öğesi (autofill: fiyat için). Yoksa None."""
        return self._repo.son_wishlist_adli(self._user_id, ad)

    def wishlist(self) -> list[WishlistSatiri]:
        bakiye = self.bakiye()
        return [
            WishlistSatiri(
                id=oge.id,
                ad=oge.name,
                fiyat=oge.price,
                resim_yolu=oge.image_path,
                oran=ilerleme_orani(bakiye, oge.price),
            )
            for oge in self._repo.wishlist_aktif(self._user_id)
        ]
