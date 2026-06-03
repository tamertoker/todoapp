"""Geçici uygulama ikonu.

Gerçek avatar/ikon Faz 2'de gelecek. Şimdilik kodla küçük bir pixel ikon
çiziyoruz: koyu zemin, vurgu renginde kenarlık ve ortada bir eşkenar dörtgen.
Bu ikon hem pencere köşesinde hem sistem tepsisinde (tray) kullanılır.
"""

from __future__ import annotations

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QBrush, QColor, QIcon, QPainter, QPixmap, QPolygonF

from leveltodo.presentation.theme.palette import Palette


def make_app_icon(palette: Palette, size: int = 64) -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.fillRect(0, 0, size, size, QColor(palette.panel))
    painter.setPen(QColor(palette.border))
    painter.drawRect(1, 1, size - 3, size - 3)

    m = size / 2
    diamond = QPolygonF(
        [QPointF(m, m * 0.5), QPointF(m * 1.5, m), QPointF(m, m * 1.5), QPointF(m * 0.5, m)]
    )
    painter.setBrush(QBrush(QColor(palette.accent)))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawPolygon(diamond)
    painter.end()

    return QIcon(pixmap)
