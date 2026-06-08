"""Saate göre arkaplan: zaman dilimi seçimi + arkaplan görselini çizen çerçeve.

`zaman_dilimi` saf bir yardımcıdır (Qt bilmez): günün saatine göre beş dilimden
(sabah/öğle/ikindi/akşam/gece) birini verir. `ArkaplanCerceve` verilen görseli
köşeleri yuvarlatılmış biçimde, ekranı kaplayacak şekilde (kırparak) çizer; görsel
yoksa zarif bir degradeye düşer. Üstüne konan etiketler şeffaf olmalı ki arkaplan
görünsün.
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QRect, QRectF, Qt
from PyQt6.QtGui import (
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)
from PyQt6.QtWidgets import QWidget


def zaman_dilimi(saat: int) -> str:
    """Saate (0-23) göre arkaplan zaman dilimi anahtarı."""
    if 6 <= saat < 11:
        return "sabah"
    if 11 <= saat < 15:
        return "ogle"
    if 15 <= saat < 19:
        return "ikindi"
    if 19 <= saat < 23:
        return "aksam"
    return "gece"


def arkaplan_pixmap(assets_dizini: Path, ad: str) -> QPixmap | None:
    """assets/backgrounds/<ad>.png varsa yükler; yoksa None."""
    yol = assets_dizini / "backgrounds" / f"{ad}.png"
    if yol.is_file():
        pm = QPixmap(str(yol))
        if not pm.isNull():
            return pm
    return None


class ArkaplanCerceve(QWidget):
    """Arkasına görsel (ya da degrade) çizen, köşeleri yuvarlatılmış kap."""

    def __init__(self, parent: QWidget | None = None, *, radius: int = 16) -> None:
        super().__init__(parent)
        self._pixmap: QPixmap | None = None
        self._radius = radius

    def arkaplan_ayarla(self, pixmap: QPixmap | None) -> None:
        self._pixmap = pixmap
        self.update()

    def paintEvent(self, event) -> None:  # noqa: ARG002
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        r = self.rect()
        clip = QPainterPath()
        clip.addRoundedRect(QRectF(r), self._radius, self._radius)
        painter.setClipPath(clip)

        if self._pixmap is not None and not self._pixmap.isNull():
            olcekli = self._pixmap.scaled(
                r.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = (olcekli.width() - r.width()) // 2
            y = (olcekli.height() - r.height()) // 2
            painter.drawPixmap(r, olcekli, QRect(x, y, r.width(), r.height()))
        else:
            grad = QLinearGradient(0, 0, 0, r.height())
            grad.setColorAt(0.0, QColor("#2a1f3d"))
            grad.setColorAt(1.0, QColor("#0e0a16"))
            painter.fillRect(r, grad)

        painter.setClipping(False)
        kenar = QPainterPath()
        kenar.addRoundedRect(QRectF(r).adjusted(1, 1, -1, -1), self._radius, self._radius)
        painter.setPen(QPen(QColor("#3a2d52"), 2))
        painter.drawPath(kenar)
