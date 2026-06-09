"""Uygulama imleci (cursor) — seçilen görseli tüm uygulamada imleç yapar.

assets/cursors/<ad>.png görseli 32 piksele indirgenip QApplication.setOverrideCursor
ile imleç olur. Boş seçim sistem imlecine döner. Yüklenen her görsel imleç boyutuna
(32 px) ölçeklenir; böylece büyük görseller de sığar.
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QPixmap
from PyQt6.QtWidgets import QApplication

IMLEC_BOYUT = 48


def imlec_pixmap(yol: Path, boy: int = IMLEC_BOYUT) -> QPixmap | None:
    if not yol.is_file():
        return None
    px = QPixmap(str(yol))
    if px.isNull():
        return None
    return px.scaled(
        boy,
        boy,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


def imlec_uygula(assets_dir: Path, ad: str) -> None:
    """Önceki özel imleci kaldırır; ad boş değilse yenisini uygular (yığın derinliği ≤1)."""
    app = QApplication.instance()
    if app is None:
        return
    app.restoreOverrideCursor()  # öncekini geri al (yoksa zararsız)
    if not ad:
        return
    px = imlec_pixmap(assets_dir / "cursors" / ad)
    if px is not None:
        app.setOverrideCursor(QCursor(px, 0, 0))
