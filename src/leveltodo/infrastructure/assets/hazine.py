"""Hazine sandığı sprite yükleyici.

Kullanıcının ürettiği assets/treasure/sandik_(kapali|acik).png varsa onu net
ölçekler; yoksa basit bir emoji yer-tutucu (🎁) çizer.
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPainter, QPixmap


def hazine_resmi(assets_dizini: Path, acik: bool = False, hedef: int = 96) -> QPixmap:
    ad = "sandik_acik" if acik else "sandik_kapali"
    yol = assets_dizini / "treasure" / f"{ad}.png"
    if yol.is_file():
        pm = QPixmap(str(yol))
        if not pm.isNull():
            return pm.scaled(
                hedef,
                hedef,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
    pm = QPixmap(hedef, hedef)
    pm.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pm)
    font = QFont()
    font.setPixelSize(int(hedef * 0.72))
    painter.setFont(font)
    painter.drawText(pm.rect(), Qt.AlignmentFlag.AlignCenter, "🎁")
    painter.end()
    return pm
