"""Mağaza servisi.

Oyun-içi Puan ile gerçek-hayat ödüllerini DAKİKA cinsinden satın alırsın. Her
ödülün dk başına puan maliyeti vardır (kullanıcı belirler, tabandan düşemez).
Satın alma, Puan bakiyesinden düşer (point_transactions'a negatif kayıt) ve
geçmişe yazılır. İlk açılışta varsayılan ödüller tohumlanır.
"""

from __future__ import annotations

from leveltodo.domain.magaza.magaza import (
    VARSAYILAN_ODULLER,
    fiyat_hesapla,
    maliyet_sinirla,
)
from leveltodo.domain.time.gun import Gun
from leveltodo.domain.time.saat import Saat
from leveltodo.infrastructure.persistence.sqlite.ledger_repository import SqlLedgerRepository
from leveltodo.infrastructure.persistence.sqlite.magaza_repository import SqlMagazaRepository
from leveltodo.infrastructure.persistence.sqlite.models import (
    DEFAULT_USER_ID,
    StorePurchase,
    StoreReward,
)
from leveltodo.shared.ids import new_id

_MAGAZA_KAYNAGI = "store"


class MagazaServisi:
    def __init__(
        self,
        magaza_repo: SqlMagazaRepository,
        defter_repo: SqlLedgerRepository,
        saat: Saat,
        gun_baslangic_getir,
        user_id: str = DEFAULT_USER_ID,
    ) -> None:
        self._repo = magaza_repo
        self._defter = defter_repo
        self._saat = saat
        self._gun_baslangic = gun_baslangic_getir
        self._user_id = user_id

    def _bugun(self):
        return Gun.olustur(self._saat.simdi(), self._gun_baslangic()).tarih

    def bakiye_puan(self) -> int:
        return self._defter.puan_bakiye(self._user_id)

    def oduller(self) -> list[StoreReward]:
        mevcut = self._repo.aktif_oduller(self._user_id)
        if not mevcut:  # ilk açılış: varsayılanları tohumla
            for ad, maliyet in VARSAYILAN_ODULLER:
                self.odul_ekle(ad, maliyet)
            mevcut = self._repo.aktif_oduller(self._user_id)
        return mevcut

    def odul_ekle(self, ad: str, dk_maliyet: int) -> None:
        ad = ad.strip()
        if not ad:
            return
        self._repo.odul_ekle(
            id=new_id(),
            user_id=self._user_id,
            name=ad,
            cost_per_min=maliyet_sinirla(dk_maliyet),
            sort_order=self._repo.sonraki_sira(self._user_id),
        )

    def odul_sil(self, odul_id: str) -> None:
        self._repo.odul_pasife_al(odul_id)

    def maliyet_ayarla(self, odul_id: str, dk_maliyet: int) -> None:
        self._repo.maliyet_guncelle(odul_id, maliyet_sinirla(dk_maliyet))

    def fiyat(self, dk_maliyet: int, dakika: int) -> int:
        return fiyat_hesapla(dakika, dk_maliyet)

    def satin_al(self, odul_id: str, dakika: int) -> bool:
        """Yeterli puan varsa satın alır (bakiyeden düşer, geçmişe yazar). Aksi False."""
        odul = self._repo.odul_getir(odul_id)
        if odul is None or dakika <= 0:
            return False
        maliyet = fiyat_hesapla(dakika, odul.cost_per_min)
        if maliyet <= 0 or self.bakiye_puan() < maliyet:
            return False
        gun = self._bugun()
        self._defter.puan_islem(
            user_id=self._user_id,
            day=gun,
            source=_MAGAZA_KAYNAGI,
            ref_id=odul_id,
            miktar=-maliyet,
        )
        self._repo.satin_alma_ekle(
            id=new_id(),
            user_id=self._user_id,
            reward_name=odul.name,
            minutes=dakika,
            cost=maliyet,
            day=gun,
        )
        return True

    def gecmis(self) -> list[StorePurchase]:
        return self._repo.son_satin_almalar(self._user_id)

    def ad_onerileri(self) -> list[str]:
        return self._repo.ad_onerileri(self._user_id)

    def maliyet_oneri(self, ad: str) -> int | None:
        """Verilen adlı son ödülün dk-maliyeti (autofill). Yoksa None."""
        odul = self._repo.son_odul_adli(self._user_id, ad)
        return odul.cost_per_min if odul is not None else None
