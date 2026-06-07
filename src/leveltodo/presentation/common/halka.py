"""Halka (donut) grafiği — etiket-süre dağılımını QPainter ile çizer.

Her dilim bir etiketin payını gösterir (kendi rengiyle). Ortası boştur (donut).
"""

from __future__ import annotations

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QColor, QPainter, QPalette
from PyQt6.QtWidgets import QWidget


class Halka(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._veri: list[tuple[str, str, int]] = []  # (etiket, renk, saniye)
        self.setMinimumSize(240, 240)

    def setVeri(self, veri: list[tuple[str, str, int]]) -> None:
        self._veri = veri
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: ANN001
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        boyut = min(w, h) - 12
        x, y = (w - boyut) // 2, (h - boyut) // 2
        rect = QRect(x, y, boyut, boyut)
        toplam = sum(v for _, _, v in self._veri)
        if toplam <= 0:
            p.end()
            return
        bas = 90 * 16  # tepeden başla, saat yönü
        for _ad, renk, val in self._veri:
            aci = -int(360 * 16 * val / toplam)
            p.setBrush(QColor(renk))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawPie(rect, bas, aci)
            bas += aci
        # Ortadaki delik (donut)
        delik = int(boyut * 0.56)
        dx, dy = (w - delik) // 2, (h - delik) // 2
        p.setBrush(self.palette().color(QPalette.ColorRole.Window))
        p.drawEllipse(dx, dy, delik, delik)
        p.end()
