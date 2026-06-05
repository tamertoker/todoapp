"""Ses motoru — kısa efektleri düşük gecikmeyle çalar (QSoundEffect).

assets/sounds/<anahtar>.wav dosyalarını açılışta yükler. Bir dosya yoksa o ses
sessizce atlanır (uygulama yine çalışır). Ses açık/kapalı ve düzeyi ayar deposundan
okunur, böylece kullanıcı denetler.
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QSoundEffect

from leveltodo.application.settings_service import SettingsService

SES_ANAHTARLARI = (
    "tamamla",
    "kritik",
    "combo",
    "rozet",
    "seviye",
    "dusman_devrildi",
    "hata",
)


class SesMotoru:
    def __init__(self, ses_dir: Path, settings: SettingsService) -> None:
        self._settings = settings
        self._efektler: dict[str, QSoundEffect] = {}
        for ad in SES_ANAHTARLARI:
            yol = ses_dir / f"{ad}.wav"
            if yol.is_file():
                efekt = QSoundEffect()
                efekt.setSource(QUrl.fromLocalFile(str(yol)))
                self._efektler[ad] = efekt

    @property
    def acik(self) -> bool:
        return bool(self._settings.get("ses_acik"))

    @property
    def duzey(self) -> int:
        return int(self._settings.get("ses_duzeyi"))

    def acik_ayarla(self, acik: bool) -> None:
        self._settings.set("ses_acik", acik)

    def duzey_ayarla(self, duzey: int) -> None:
        self._settings.set("ses_duzeyi", duzey)

    def cal(self, anahtar: str) -> None:
        if not self.acik:
            return
        efekt = self._efektler.get(anahtar)
        if efekt is None:
            return
        efekt.setVolume(max(0.0, min(1.0, self.duzey / 100)))
        efekt.play()
