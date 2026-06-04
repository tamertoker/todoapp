"""Düşman sprite yükleyici. Kullanıcının ürettiği assets/enemies/<ad>.png
varsa onu net büyütür; yoksa basit bir yer-tutucu döndürür."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPixmap


def dusman_resmi(assets_dizini: Path, anahtar: str, hedef: int = 110) -> QPixmap:
    yol = assets_dizini / "enemies" / f"{anahtar}.png"
    if yol.is_file():
        return QPixmap(str(yol)).scaled(
            hedef,
            hedef,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation,
        )
    pixmap = QPixmap(hedef, hedef)
    pixmap.fill(QColor("#3a2a4a"))
    return pixmap
