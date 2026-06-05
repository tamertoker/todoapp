"""Bildirim servisi.

Bir bildirim isteğini alır, kategorisi açık mı ve gece sessizliğinde miyiz diye
bakar; gösterilecekse kayıtlı kanallara (OS bildirimi + uygulama-içi toast)
iletir. Kanallar dışarıdan eklenir (PyQt/OS bağımlılığı bu katmana sızmaz).
"""

from __future__ import annotations

from collections.abc import Callable

from leveltodo.application.settings_service import SettingsService
from leveltodo.domain.bildirim.bildirim import (
    Bildirim,
    BildirimKategori,
    gosterilsin_mi,
    sessiz_saatte_mi,
)
from leveltodo.domain.time.saat import Saat

Kanal = Callable[[Bildirim], None]


class BildirimServisi:
    def __init__(self, settings: SettingsService, saat: Saat) -> None:
        self._settings = settings
        self._saat = saat
        self._kanallar: list[Kanal] = []

    def kanal_ekle(self, kanal: Kanal) -> None:
        self._kanallar.append(kanal)

    def kategori_acik(self, kategori: BildirimKategori) -> bool:
        return bool(self._settings.get(f"bildirim_{kategori.value}"))

    def kategori_ayarla(self, kategori: BildirimKategori, acik: bool) -> None:
        self._settings.set(f"bildirim_{kategori.value}", acik)

    @property
    def sessiz_acik(self) -> bool:
        return bool(self._settings.get("bildirim_sessiz_acik"))

    @property
    def sessiz_baslangic(self) -> int:
        return int(self._settings.get("bildirim_sessiz_baslangic"))

    @property
    def sessiz_bitis(self) -> int:
        return int(self._settings.get("bildirim_sessiz_bitis"))

    def sessiz_ayarla(self, acik: bool, baslangic: int, bitis: int) -> None:
        self._settings.set("bildirim_sessiz_acik", acik)
        self._settings.set("bildirim_sessiz_baslangic", baslangic)
        self._settings.set("bildirim_sessiz_bitis", bitis)

    def _su_an_sessiz_mi(self) -> bool:
        return sessiz_saatte_mi(
            self._saat.simdi().hour, self.sessiz_baslangic, self.sessiz_bitis
        )

    def bildir(self, kategori: BildirimKategori, baslik: str, govde: str) -> bool:
        """Kurallar elveriyorsa bildirimi tüm kanallara iletir. Gösterildiyse True."""
        if not gosterilsin_mi(
            self.kategori_acik(kategori), self.sessiz_acik, self._su_an_sessiz_mi()
        ):
            return False
        bildirim = Bildirim(kategori=kategori, baslik=baslik, govde=govde)
        for kanal in self._kanallar:
            kanal(bildirim)
        return True
