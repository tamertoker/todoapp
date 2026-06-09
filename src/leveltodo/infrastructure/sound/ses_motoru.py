"""Ses motoru — olay seslerini QMediaPlayer ile çalar.

assets/sounds/<anahtar>.wav dosyaları açılışta yüklenir; her ses için ayrı bir
oynatıcı + çıkış tutulur (sesler birbirini kesmesin). Önceden QSoundEffect
kullanılıyordu ama uzun dosyalarda (ör. birkaç saniyelik tamamlama sesi) yükleme
yarışı yüzünden güvenilir çalmıyordu; QMediaPlayer her uzunlukta wav'ı çalar.
Dosya yoksa o ses sessizce atlanır. Ses açık/kapalı ve düzeyi ayar deposundan
okunur, böylece kullanıcı denetler.
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer

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
        self._oynaticilar: dict[str, QMediaPlayer] = {}
        self._cikislar: dict[str, QAudioOutput] = {}
        for ad in SES_ANAHTARLARI:
            yol = ses_dir / f"{ad}.wav"
            if yol.is_file():
                cikis = QAudioOutput()
                oynatici = QMediaPlayer()
                oynatici.setAudioOutput(cikis)
                oynatici.setSource(QUrl.fromLocalFile(str(yol)))
                self._oynaticilar[ad] = oynatici
                self._cikislar[ad] = cikis

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
        oynatici = self._oynaticilar.get(anahtar)
        if oynatici is None:
            return
        self._cikislar[anahtar].setVolume(max(0.0, min(1.0, self.duzey / 100)))
        oynatici.stop()  # baştan çalsın (art arda tetiklenirse)
        oynatici.play()
