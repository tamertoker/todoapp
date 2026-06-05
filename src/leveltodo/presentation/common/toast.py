"""Uygulama-içi pixel toast — garantili bildirim kanalı.

OS bildirimi başarısız olsa bile bu her zaman çalışır: ana pencerenin sağ üst
köşesinde küçük bir kart belirir, birkaç saniyede kendiliğinden kaybolur. Üst üste
gelen bildirimler dikey istiflenir.
"""

from __future__ import annotations

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from leveltodo.domain.bildirim.bildirim import Bildirim

_KENAR = 16  # pencere kenarından boşluk
_GENISLIK = 300
_SURE_MS = 4000


class ToastYoneticisi:
    def __init__(self, ana_pencere: QWidget) -> None:
        self._ana = ana_pencere
        self._aktif: list[QFrame] = []

    def goster(self, bildirim: Bildirim) -> None:
        kart = self._kart(bildirim)
        kart.setParent(self._ana)
        self._aktif.append(kart)
        self._yerlestir()
        kart.show()
        kart.raise_()
        QTimer.singleShot(_SURE_MS, lambda: self._kapat(kart))

    def _kart(self, bildirim: Bildirim) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Toast")
        frame.setFixedWidth(_GENISLIK)
        v = QVBoxLayout(frame)
        v.setContentsMargins(12, 10, 12, 10)
        v.setSpacing(2)
        baslik = QLabel(bildirim.baslik)
        baslik.setObjectName("ToastBaslik")
        baslik.setWordWrap(True)
        govde = QLabel(bildirim.govde)
        govde.setObjectName("ToastGovde")
        govde.setWordWrap(True)
        v.addWidget(baslik)
        v.addWidget(govde)
        return frame

    def _yerlestir(self) -> None:
        y = _KENAR
        for kart in self._aktif:
            kart.adjustSize()
            x = self._ana.width() - _GENISLIK - _KENAR
            kart.move(max(_KENAR, x), y)
            y += kart.height() + 8

    def _kapat(self, kart: QFrame) -> None:
        if kart in self._aktif:
            self._aktif.remove(kart)
            kart.setParent(None)
            kart.deleteLater()
            self._yerlestir()
