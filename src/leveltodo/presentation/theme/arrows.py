"""Spinbox (sayı kutusu) için yukarı/aşağı ok simgeleri üretir.

Qt artık hazır ok simgesi getirmiyor; biz de küçük üçgen okları kodla çizip
geçici bir önbellek (cache) dizinine PNG olarak kaydediyoruz. QSS bu dosyaları
`image: url(...)` ile kullanır. Renk temaya göre verilir (yazı rengi).
"""

from __future__ import annotations

from pathlib import Path

from platformdirs import user_cache_dir
from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QColor, QPainter, QPixmap, QPolygon


def _ok_ciz(yon: str, renk: str) -> str:
    boyut = 16
    pixmap = QPixmap(boyut, boyut)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setBrush(QColor(renk))
    painter.setPen(Qt.PenStyle.NoPen)
    if yon == "up":
        ucgen = QPolygon([QPoint(8, 4), QPoint(3, 11), QPoint(13, 11)])
    else:
        ucgen = QPolygon([QPoint(3, 5), QPoint(13, 5), QPoint(8, 12)])
    painter.drawPolygon(ucgen)
    painter.end()

    dizin = Path(user_cache_dir("leveltodo", appauthor=False)) / "arrows"
    dizin.mkdir(parents=True, exist_ok=True)
    dosya = dizin / f"{yon}_{renk.lstrip('#')}.png"
    pixmap.save(str(dosya))
    return str(dosya).replace("\\", "/")


def ok_yollari(renk: str) -> tuple[str, str]:
    """(yukari_ok_yolu, asagi_ok_yolu) — QSS'in kullanacağı dosya yolları."""
    return _ok_ciz("up", renk), _ok_ciz("down", renk)
