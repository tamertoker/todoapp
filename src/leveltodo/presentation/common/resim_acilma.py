"""Resim açılma — bir wishlist öğesinin ilerlemesini görsel olarak gösterir.

Resim kendi en-boy oranında, büyükçe (bir üst sınıra kadar) gösterilir; widget
tam resmin boyutuna küçülür, böylece yanlarda boş/siyah bar kalmaz. İlerleme
oranı (0..1) kadar soldan sağa "açılır": açılan kısım net, kalanı karartılmış.
Resim yoksa basit bir dolum çubuğu (yeşil) çizilir.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPixmap
from PyQt6.QtWidgets import QWidget

_MAKS_GENISLIK = 720
_MAKS_YUKSEKLIK = 460
_CUBUK_YUKSEKLIK = 48  # resim yoksa


class ResimAcilma(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._gosterilen: QPixmap | None = None
        self._oran = 0.0

    def setVeri(self, pixmap: QPixmap | None, oran: float) -> None:
        self._oran = max(0.0, min(1.0, oran))
        if pixmap is not None and not pixmap.isNull():
            self._gosterilen = pixmap.scaled(
                _MAKS_GENISLIK,
                _MAKS_YUKSEKLIK,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            # Widget'ı resmin boyutuna sabitle → boş bar yok, tam görünür.
            self.setFixedSize(self._gosterilen.size())
        else:
            self._gosterilen = None
            self.setMinimumHeight(_CUBUK_YUKSEKLIK)
            self.setMaximumHeight(_CUBUK_YUKSEKLIK)
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: ANN001
        p = QPainter(self)
        w, h = self.width(), self.height()
        acilan = int(w * self._oran)
        if self._gosterilen is not None:
            p.drawPixmap(0, 0, self._gosterilen)  # widget tam resim boyutunda → doldurur
            if acilan < w:  # açılmamış kısmı karart (soldan sağa açılma efekti)
                p.fillRect(acilan, 0, w - acilan, h, QColor(0, 0, 0, 175))
        else:
            p.fillRect(0, 0, acilan, h, QColor("#39d353"))
            p.fillRect(acilan, 0, w - acilan, h, QColor("#2b2f36"))
        p.end()
