"""Yazı tipi (font) seçimi.

Asıl pixel-art font dosyası Faz 6'da eklenecek. Şimdilik, varsa assets/fonts
altındaki bir .ttf yüklenir; yoksa Windows'ta her zaman bulunan monospace
"Consolas"a düşülür. Tema yapısı, font dosyası gelince hazır olacak şekilde
kuruldu.
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtGui import QFontDatabase

_FALLBACK = "Consolas"


def load_pixel_font() -> str:
    fonts_dir = Path(__file__).resolve().parents[3].parent / "assets" / "fonts"
    if fonts_dir.is_dir():
        for ttf in sorted(fonts_dir.glob("*.ttf")):
            font_id = QFontDatabase.addApplicationFont(str(ttf))
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                return families[0]
    return _FALLBACK
