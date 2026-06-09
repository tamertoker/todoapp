"""Yazı tipi (font) yükleme ve seçimi.

assets/fonts altındaki tüm .ttf dosyaları yüklenir, kullanılabilir aile adları
toplanır. Varsayılan "Geo"dur (sayıları daha okunaklı). Kullanıcı ayarlardan
diğer ailelere geçebilir. Hiç font yoksa Windows'ta her zaman bulunan "Consolas"a
düşülür.
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtGui import QFontDatabase

_FALLBACK = "Consolas"
_VARSAYILAN = "Geo"
_yuklenen: list[str] = []


def _fonts_dir() -> Path:
    return Path(__file__).resolve().parents[3].parent / "assets" / "fonts"


def load_all_fonts() -> list[str]:
    """Tüm .ttf'leri Qt'ye yükler ve kullanılabilir aile adlarını döndürür."""
    global _yuklenen
    aileler: set[str] = set()
    fonts_dir = _fonts_dir()
    if fonts_dir.is_dir():
        for ttf in sorted(fonts_dir.glob("*.ttf")):
            font_id = QFontDatabase.addApplicationFont(str(ttf))
            for aile in QFontDatabase.applicationFontFamilies(font_id):
                aileler.add(aile)
    _yuklenen = sorted(aileler) if aileler else [_FALLBACK]
    return _yuklenen


def mevcut_fontlar() -> list[str]:
    """Yüklenmiş font aileleri (load_all_fonts çağrıldıktan sonra)."""
    return _yuklenen or [_FALLBACK]


def varsayilan_font() -> str:
    aileler = mevcut_fontlar()
    return _VARSAYILAN if _VARSAYILAN in aileler else aileler[0]


def gecerli_font(istenen: str) -> str:
    """İstenen font yüklüyse onu, değilse varsayılanı döndürür."""
    return istenen if istenen in mevcut_fontlar() else varsayilan_font()
