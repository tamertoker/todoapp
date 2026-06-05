"""Düşman servisi — aktif Şeytan'ın tier ve canını yönetir (ayar deposunda).

Görev tamamlanınca (kazanılan XP × katsayı) düşman hasar alır; canı biterse bir
üst tier düşman tam canla gelir. XP kazanmadan geçen her gün düşman biraz iyileşir
(tembellik onu güçlendirir) — bu yüzden okuma (durum) ve hasar öncesinde bekleyen
iyileşme uygulanır.
"""

from __future__ import annotations

from datetime import date

from leveltodo.application.settings_service import SettingsService
from leveltodo.domain.dusman.dusman import (
    Dusman,
    dusman_getir,
    gunluk_iyilesme,
    hasar,
    max_hp,
)
from leveltodo.domain.events import DusmanDevrildi
from leveltodo.domain.time.gun import Gun
from leveltodo.domain.time.saat import Saat


class DusmanServisi:
    TIER = "dusman_tier"
    HP = "dusman_hp"
    SON_ETKINLIK = "dusman_son_etkinlik"  # son hasar/iyileşme günü (ISO tarih)

    def __init__(
        self, settings: SettingsService, saat: Saat, gun_baslangic_getir, olay_hatti=None
    ) -> None:
        self._settings = settings
        self._saat = saat
        self._gun_baslangic = gun_baslangic_getir
        self._olay_hatti = olay_hatti

    def _bugun(self) -> date:
        return Gun.olustur(self._saat.simdi(), self._gun_baslangic()).tarih

    def _tier(self) -> int:
        return int(self._settings.get(self.TIER))

    def _hp(self) -> int:
        hp = int(self._settings.get(self.HP))
        if hp < 0:  # ilk kez: düşman tam canla başlar
            hp = max_hp(self._tier())
            self._settings.set(self.HP, hp)
        return hp

    def _iyilesme_uygula(self) -> None:
        """Son etkinlikten bu yana XP'siz geçen günler için düşmanı iyileştirir."""
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

    def hasar_ver(self, xp: int) -> None:
        if xp <= 0:
            return
        self._iyilesme_uygula()  # önce bekleyen iyileşme, sonra darbe
        hp = self._hp() - hasar(xp)
        tier = self._tier()
        if hp <= 0:  # düşman devrildi → bir üst tier, tam can
            devrilen_tier = tier
            tier += 1
            self._settings.set(self.TIER, tier)
            hp = max_hp(tier)
            if self._olay_hatti is not None:
                self._olay_hatti.publish(
                    DusmanDevrildi(occurred_at=self._saat.simdi(), tier=devrilen_tier)
                )
        self._settings.set(self.HP, hp)
        self._settings.set(self.SON_ETKINLIK, self._bugun().isoformat())
