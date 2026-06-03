"""Avatar oluşturucu — Mana Seed katmanlarını birleştirir.

512×512'lik sprite sayfalarından sol-üstteki 64×64 kareyi (karşıya bakan, dik
duruş) alır, katmanları üst üste bindirir (önce vücut, sonra kıyafet) ve net
(bulanıklaştırmadan) büyütür. Şapka katmanı şimdilik yok.
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QPainter, QPixmap

_KARE = 64


class AvatarOlusturucu:
    def __init__(self, assets_dizini: Path) -> None:
        self._p1 = assets_dizini / "char_a_p1"

    def olustur(self, katman_dosyalari: list[str], buyutme: int = 4) -> QPixmap:
        sonuc = QPixmap(_KARE, _KARE)
        sonuc.fill(Qt.GlobalColor.transparent)
        painter = QPainter(sonuc)
        for dosya in katman_dosyalari:
            sayfa = QPixmap(str(self._p1 / dosya))
            if sayfa.isNull():
                continue
            on_kare = sayfa.copy(QRect(0, 0, _KARE, _KARE))
            painter.drawPixmap(0, 0, on_kare)
        painter.end()
        return sonuc.scaled(
            _KARE * buyutme,
            _KARE * buyutme,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation,  # nearest-neighbor: keskin pixel
        )


def avatar_katmanlari(profil_seviye: int) -> list[str]:
    """Profil seviyesine göre hangi katmanların gösterileceği.
    Seviye yükseldikçe vücut paleti (v00→v10) ve kıyafet (v01→v05) ilerler."""
    bas_v = min(10, max(0, profil_seviye))
    kiyafet_v = min(5, 1 + max(0, profil_seviye) // 5)
    return [
        f"char_a_p1_0bas_humn_v{bas_v:02d}.png",
        f"1out/char_a_p1_1out_fstr_v{kiyafet_v:02d}.png",
    ]
