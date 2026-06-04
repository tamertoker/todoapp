"""Düşman servisi — aktif Şeytan'ın tier ve canını yönetir (ayar deposunda).

Görev tamamlanınca (kazanılan XP) düşman hasar alır; canı biterse bir üst tier
düşman tam canla gelir.
"""

from __future__ import annotations

from leveltodo.application.settings_service import SettingsService
from leveltodo.domain.dusman.dusman import Dusman, dusman_getir, max_hp


class DusmanServisi:
    TIER = "dusman_tier"
    HP = "dusman_hp"

    def __init__(self, settings: SettingsService) -> None:
        self._settings = settings

    def _tier(self) -> int:
        return int(self._settings.get(self.TIER))

    def _hp(self) -> int:
        hp = int(self._settings.get(self.HP))
        if hp < 0:  # ilk kez: düşman tam canla başlar
            hp = max_hp(self._tier())
            self._settings.set(self.HP, hp)
        return hp

    def durum(self) -> tuple[Dusman, int, int, int]:
        """(düşman, mevcut_can, maks_can, tier)."""
        tier = self._tier()
        return dusman_getir(tier), self._hp(), max_hp(tier), tier

    def hasar_ver(self, xp: int) -> None:
        if xp <= 0:
            return
        hp = self._hp() - xp
        tier = self._tier()
        if hp <= 0:  # düşman devrildi → bir üst tier, tam can
            tier += 1
            self._settings.set(self.TIER, tier)
            hp = max_hp(tier)
        self._settings.set(self.HP, hp)
