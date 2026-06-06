"""Resim açılma — bir wishlist öğesinin ilerlemesini görsel olarak gösterir.

İlerleme oranı (0..1) kadar soldan sağa resim "açılır": açılan kısım net, kalanı
karartılmış görünür. Resim yoksa basit bir dolum çubuğu (yeşil) çizilir.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPixmap
from PyQt6.QtWidgets import QWidget


class ResimAcilma(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._pixmap: QPixmap | None = None
        self._oran = 0.0
        self.setMinimumHeight(160)

    def setVeri(self, pixmap: QPixmap | None, oran: float) -> None:
        self._pixmap = pixmap
        self._oran = max(0.0, min(1.0, oran))
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: ANN001
        p = QPainter(self)
        w, h = self.width(), self.height()
        acilan = int(w * self._oran)
        if self._pixmap is not None and not self._pixmap.isNull():
            # Resmin TAMAMI görünsün: kırpmadan, oranını koruyarak sığdır (ortalı).
            p.fillRect(0, 0, w, h, QColor("#1a1a1a"))
            olcekli = self._pixmap.scaled(
                w,
                h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            ox = (w - olcekli.width()) // 2
            oy = (h - olcekli.height()) // 2
            p.drawPixmap(ox, oy, olcekli)
            if acilan < w:  # açılmamış kısmı karart (soldan sağa açılma efekti)
                p.fillRect(acilan, 0, w - acilan, h, QColor(0, 0, 0, 175))
        else:
            p.fillRect(0, 0, acilan, h, QColor("#39d353"))
            p.fillRect(acilan, 0, w - acilan, h, QColor("#2b2f36"))
        p.end()
