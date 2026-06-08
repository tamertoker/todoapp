"""Düşman servisi — aktif Şeytan'ın tier/can/biriken hasarını ve hazinelerini yönetir.

Görev tamamlanınca hasar ANINDA inmez; "biriken hasar"a eklenir. Kullanıcı Düşman
sekmesinde "Vur" deyince biriken hasarın tamamı tek darbede iner — böylece düşmanı
gerçekten kendi elinle devirdiğini hissedersin. Düşman devrilirse bir üst tier
düşman tam canla gelir ve geride bir hazine bırakır. Hasarsız geçen her gün düşman
biraz iyileşir; bu yüzden okuma/vuruş öncesinde bekleyen iyileşme uygulanır.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date

from leveltodo.application.combo_servisi import ComboServisi
from leveltodo.application.settings_service import SettingsService
from leveltodo.domain.dusman.dusman import (
    Dusman,
    HazineOdulu,
    dusman_getir,
    gunluk_iyilesme,
    hasar,
    hazine_odulu,
    lanet_sec,
    max_hp,
    son_soz_sec,
)
from leveltodo.domain.events import DusmanDevrildi
from leveltodo.domain.time.gun import Gun
from leveltodo.domain.time.saat import Saat
from leveltodo.infrastructure.persistence.sqlite.ledger_repository import SqlLedgerRepository
from leveltodo.infrastructure.persistence.sqlite.models import DEFAULT_USER_ID

ODUL_KAYNAGI = "hazine"


@dataclass(frozen=True, slots=True)
class VurusSonucu:
    verilen_hasar: int  # bu vuruşta inen toplam hasar
    kalan_hp: int
    maks_hp: int
    devrilen: int  # bu vuruşta kaç düşman devrildi
    konusma: str  # düşmanın söylediği (lanet ya da son söz)


class DusmanServisi:
    TIER = "dusman_tier"
    HP = "dusman_hp"
    SON_ETKINLIK = "dusman_son_etkinlik"  # son hasar/iyileşme günü (ISO tarih)
    BIRIKEN = "dusman_biriken_hasar"  # vurulmayı bekleyen hasar
    HAZINELER = "dusman_hazineler"  # bekleyen hazinelerin tier listesi

    def __init__(
        self,
        settings: SettingsService,
        saat: Saat,
        gun_baslangic_getir,
        olay_hatti=None,
        defter_repo: SqlLedgerRepository | None = None,
        combo: ComboServisi | None = None,
        user_id: str = DEFAULT_USER_ID,
    ) -> None:
        self._settings = settings
        self._saat = saat
        self._gun_baslangic = gun_baslangic_getir
        self._olay_hatti = olay_hatti
        self._defter = defter_repo
        self._combo = combo
        self._user_id = user_id

    def _bugun(self) -> date:
        return Gun.olustur(self._saat.simdi(), self._gun_baslangic()).tarih

    def _tier(self) -> int:
        return int(self._settings.get(self.TIER))

    def _hp(self) -> int:
        hp = int(self._settings.get(self.HP))
        maks = max_hp(self._tier())
        if hp < 0:  # ilk kez: düşman tam canla başlar
            hp = maks
            self._settings.set(self.HP, hp)
        elif hp > maks:  # can eğrisi değişmiş olabilir — yeni maksimuma sığdır
            hp = maks
        return hp

    def _iyilesme_uygula(self) -> None:
        """Son etkinlikten bu yana hasarsız geçen günler için düşmanı iyileştirir."""
        bugun = self._bugun()
        son_ham = str(self._settings.get(self.SON_ETKINLIK))
        if not son_ham:  # ilk kez: bugünü işaretle, iyileşme yok
            self._settings.set(self.SON_ETKINLIK, bugun.isoformat())
            return
        son = date.fromisoformat(son_ham)
        gun_farki = (bugun - son).days
        if gun_farki >= 1:
            tier = self._tier()
            iyilesme = gunluk_iyilesme(max_hp(tier)) * gun_farki
            hp = min(max_hp(tier), self._hp() + iyilesme)
            self._settings.set(self.HP, hp)
            self._settings.set(self.SON_ETKINLIK, bugun.isoformat())

    def durum(self) -> tuple[Dusman, int, int, int]:
        """(düşman, mevcut_can, maks_can, tier). Okumadan önce iyileşme uygulanır."""
        self._iyilesme_uygula()
        tier = self._tier()
        return dusman_getir(tier), self._hp(), max_hp(tier), tier

    # — Biriken hasar —
    def biriken_hasar(self) -> int:
        return int(self._settings.get(self.BIRIKEN))

    def hasar_biriktir(self, xp: int) -> None:
        """Görevden kazanılan XP'yi vurulmayı bekleyen hasara ekler (anında inmez)."""
        if xp <= 0:
            return
        self._settings.set(self.BIRIKEN, self.biriken_hasar() + hasar(xp))

    def vur(self) -> VurusSonucu:
        """Biriken hasarın tamamını tek darbede düşmana indirir."""
        self._iyilesme_uygula()  # önce bekleyen iyileşme, sonra darbe
        biriken = self.biriken_hasar()
        tier = self._tier()
        hp = self._hp()
        if biriken <= 0:
            return VurusSonucu(0, hp, max_hp(tier), 0, "")

        self._settings.set(self.BIRIKEN, 0)
        devrilen = 0
        kalan = biriken
        while kalan > 0:
            hp -= kalan
            if hp > 0:
                kalan = 0
            else:
                self._hazine_ekle(tier)
                if self._olay_hatti is not None:
                    self._olay_hatti.publish(
                        DusmanDevrildi(occurred_at=self._saat.simdi(), tier=tier)
                    )
                devrilen += 1
                kalan = -hp  # bir sonraki düşmana taşan hasar
                tier += 1
                hp = max_hp(tier)

        self._settings.set(self.TIER, tier)
        self._settings.set(self.HP, hp)
        self._settings.set(self.SON_ETKINLIK, self._bugun().isoformat())

        tohum = int(self._saat.simdi().timestamp())
        konusma = son_soz_sec(tohum) if devrilen else lanet_sec(tohum)
        return VurusSonucu(biriken, hp, max_hp(tier), devrilen, konusma)

    # — Hazineler —
    def _hazine_ekle(self, tier: int) -> None:
        hazineler = list(self._settings.get(self.HAZINELER))
        hazineler.append(tier)
        self._settings.set(self.HAZINELER, hazineler)

    def bekleyen_hazine_sayisi(self) -> int:
        return len(self._settings.get(self.HAZINELER))

    def hazine_ac(self) -> HazineOdulu | None:
        """Bekleyen bir hazineyi açar, ödülü uygular ve döndürür. Yoksa None."""
        hazineler = list(self._settings.get(self.HAZINELER))
        if not hazineler:
            return None
        tier = hazineler.pop(0)
        self._settings.set(self.HAZINELER, hazineler)

        odul = hazine_odulu(tier, random.random(), random.random())
        if odul.tur == "puan" and self._defter is not None:
            self._defter.puan_islem(
                user_id=self._user_id,
                day=self._bugun(),
                source=ODUL_KAYNAGI,
                ref_id=None,
                miktar=odul.miktar,
            )
        elif odul.tur == "xp" and self._defter is not None:
            self._defter.record(
                user_id=self._user_id,
                day=self._bugun(),
                source=ODUL_KAYNAGI,
                ref_id=None,
                xp=odul.miktar,
                points=0,
            )
        elif odul.tur == "combo" and self._combo is not None:
            self._combo.odul_baslat(self._saat.simdi(), odul.miktar)
        return odul
