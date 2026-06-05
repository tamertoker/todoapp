"""Seri dondurma (freeze) servisi.

Bir gün kaçırılınca, bir tekrarlı görevin serisini sıfırlanmaktan kurtarmak için
harcanan jeton. Stok SINIRSIZdır (biriktirilebilir) ve ayar deposunda tutulur.
Kazanım: her 7 günlük giriş serisinde +1 (ve debug menüsünden elle).
"""

from __future__ import annotations

from leveltodo.application.settings_service import SettingsService
from leveltodo.domain.events import SeviyeAtlandi


class DondurmaServisi:
    ANAHTAR = "dondurma_stok"
    SEVIYE_ANAHTAR = "dondurma_son_seviye"

    def __init__(self, settings: SettingsService, olay_hatti=None, saat=None) -> None:
        self._settings = settings
        self._olay_hatti = olay_hatti
        self._saat = saat

    def seviye_odulu(self, profil_seviye: int) -> None:
        """Profil seviyesi her 3'ün katını geçtiğinde +1 jeton (3 levelde bir).
        Ayrıca seviye yükseldiyse SeviyeAtlandi olayı yayınlar (ses/bildirim için)."""
        onceki = int(self._settings.get(self.SEVIYE_ANAHTAR))
        if profil_seviye > onceki:
            kazanim = (profil_seviye // 3) - (onceki // 3)
            if kazanim > 0:
                self.ekle(kazanim)
            self._settings.set(self.SEVIYE_ANAHTAR, profil_seviye)
            if self._olay_hatti is not None and self._saat is not None:
                self._olay_hatti.publish(
                    SeviyeAtlandi(occurred_at=self._saat.simdi(), yeni_seviye=profil_seviye)
                )

    def stok(self) -> int:
        return int(self._settings.get(self.ANAHTAR))

    def ekle(self, adet: int = 1) -> None:
        self._settings.set(self.ANAHTAR, self.stok() + adet)

    def kullan(self) -> bool:
        """Bir jeton harca; varsa True döner, yoksa False."""
        mevcut = self.stok()
        if mevcut > 0:
            self._settings.set(self.ANAHTAR, mevcut - 1)
            return True
        return False
