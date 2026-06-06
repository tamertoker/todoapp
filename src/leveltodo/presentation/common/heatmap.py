"""Isı haritası — GitHub tarzı yıllık aktivite ızgarası (QPainter).

Sütunlar haftalar, satırlar haftanın günleri (Pzt üstte). Her kare o günün
değerine göre koyulaşır (yeşil tonları). Karenin üstüne gelince o günün tarihi
ve değeri tooltip olarak çıkar. Hangi metrik gösterildiği setVeri ile verilir.
"""

from __future__ import annotations

from datetime import date, timedelta

from PyQt6.QtCore import QRect
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QWidget

_HUCRE = 14
_BOSLUK = 3
# 0 (boş) → 4 (en yoğun) yeşil basamakları (GitHub'a benzer)
_TONLAR = ("#2b2f36", "#0e4429", "#006d32", "#26a641", "#39d353")


class IsiHaritasi(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._seri: dict[date, int] = {}
        self._bas: date | None = None
        self._bit: date | None = None
        self._birim = ""
        self._hucreler: list[tuple[QRect, date, int]] = []
        self.setMouseTracking(True)
        self.setMinimumHeight(7 * (_HUCRE + _BOSLUK) + 6)

    def setVeri(self, seri: dict[date, int], bas: date, bit: date, birim: str) -> None:
        self._seri = seri
        self._bas = bas
        self._bit = bit
        self._birim = birim
        self.updateGeometry()
        self.update()

    def _hafta_sayisi(self) -> int:
        if self._bas is None or self._bit is None:
            return 0
        ilk = self._bas - timedelta(days=self._bas.weekday())
        return (self._bit - ilk).days // 7 + 1

    def sizeHint(self):  # noqa: ANN201 - Qt override
        from PyQt6.QtCore import QSize

        return QSize(self._hafta_sayisi() * (_HUCRE + _BOSLUK) + 6, self.minimumHeight())

    def _renk(self, deger: int, maks: int) -> QColor:
        if deger <= 0:
            return QColor(_TONLAR[0])
        oran = deger / maks if maks > 0 else 0
        basamak = 1 + min(3, int(oran * 4)) if oran < 1 else 4
        return QColor(_TONLAR[max(1, basamak)])

    def paintEvent(self, _event) -> None:  # noqa: ANN001
        if self._bas is None or self._bit is None:
            return
        p = QPainter(self)
        self._hucreler = []
        ilk_pazartesi = self._bas - timedelta(days=self._bas.weekday())
        maks = max(self._seri.values(), default=0)
        gun = ilk_pazartesi
        while gun <= self._bit:
            kol = (gun - ilk_pazartesi).days // 7
            satir = gun.weekday()
            x = 2 + kol * (_HUCRE + _BOSLUK)
            y = 2 + satir * (_HUCRE + _BOSLUK)
            rect = QRect(x, y, _HUCRE, _HUCRE)
            if gun >= self._bas:
                deger = self._seri.get(gun, 0)
                p.fillRect(rect, self._renk(deger, maks))
                self._hucreler.append((rect, gun, deger))
            gun += timedelta(days=1)
        p.end()

    def mouseMoveEvent(self, event) -> None:  # noqa: ANN001
        nokta = event.position().toPoint()
        for rect, gun, deger in self._hucreler:
            if rect.contains(nokta):
                self.setToolTip(f"{gun.strftime('%d.%m.%Y')}: {deger} {self._birim}".strip())
                return
        self.setToolTip("")
