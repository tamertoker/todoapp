"""Rozet servisi — kazanılan rozetleri ve gereken sayaçları (ayar deposunda) tutar.

Sayaçlar (toplam tamamlama, kritik/combo yaşandı mı) görev tamamlanınca güncellenir.
Rozetler, Rozetler ekranı açıldığında o anki duruma göre değerlendirilir.
"""

from __future__ import annotations

from leveltodo.application.settings_service import SettingsService
from leveltodo.domain.rozetler.rozetler import (
    ROZETLER,
    Rozet,
    RozetDurumu,
    kosul_saglandi_mi,
)


class RozetServisi:
    KAZANILAN = "kazanilan_rozetler"
    TAMAMLAMA = "toplam_tamamlama"
    KRITIK = "kritik_yasandi"
    COMBO = "combo_yasandi"

    def __init__(self, settings: SettingsService) -> None:
        self._settings = settings

    # — Sayaçlar (görev tamamlanınca) —
    def tamamlama_arttir(self) -> None:
        self._settings.set(self.TAMAMLAMA, self.tamamlama() + 1)

    def tamamlama(self) -> int:
        return int(self._settings.get(self.TAMAMLAMA))

    def kritik_isaretle(self) -> None:
        self._settings.set(self.KRITIK, True)

    def kritik_yasandi_mi(self) -> bool:
        return bool(self._settings.get(self.KRITIK))

    def combo_isaretle(self) -> None:
        self._settings.set(self.COMBO, True)

    def combo_yasandi_mi(self) -> bool:
        return bool(self._settings.get(self.COMBO))

    # — Değerlendirme & raf —
    def kazanilanlar(self) -> set[str]:
        return set(self._settings.get(self.KAZANILAN))

    def degerlendir(self, durum: RozetDurumu) -> list[Rozet]:
        """Yeni kazanılan rozetleri kaydeder ve döndürür."""
        mevcut = self.kazanilanlar()
        yeni: list[Rozet] = []
        for rozet in ROZETLER:
            if rozet.id not in mevcut and kosul_saglandi_mi(rozet.id, durum):
                mevcut.add(rozet.id)
                yeni.append(rozet)
        if yeni:
            self._settings.set(self.KAZANILAN, sorted(mevcut))
        return yeni

    def tum_rozetler(self) -> list[tuple[Rozet, bool]]:
        kazanilan = self.kazanilanlar()
        return [(rozet, rozet.id in kazanilan) for rozet in ROZETLER]
