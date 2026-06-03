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

    def ai_resmi(self, yol: Path, hedef: int = 256) -> QPixmap:
        """Kullanıcının ürettiği hazır avatar resmini (tek PNG) net büyütür."""
        pixmap = QPixmap(str(yol))
        return pixmap.scaled(
            hedef,
            hedef,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation,
        )

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


def kategori_secenekleri(assets_dizini: Path) -> dict[str, list[str]]:
    """Avatar editörü için her kategorideki katman dosyalarını listeler.
    Anahtarlar: vucut, kiyafet, sac, sapka. Değerler char_a_p1'e göreli yollar."""
    p1 = assets_dizini / "char_a_p1"

    def alt(klasor: str, on_ek: str) -> list[str]:
        dizin = p1 / klasor
        if not dizin.is_dir():
            return []
        return sorted(on_ek + dosya.name for dosya in dizin.glob("*.png"))

    return {
        "vucut": sorted(d.name for d in p1.glob("char_a_p1_0bas_*.png")),
        "kiyafet": alt("1out", "1out/"),
        "sac": alt("4har", "4har/"),
        "sapka": alt("5hat", "5hat/"),
    }


def avatar_katmanlari(profil_seviye: int) -> list[str]:
    """Profil seviyesine göre hangi katmanların gösterileceği.
    Seviye yükseldikçe vücut paleti (v00→v10) ve kıyafet (v01→v05) ilerler."""
    bas_v = min(10, max(0, profil_seviye))
    kiyafet_v = min(5, 1 + max(0, profil_seviye) // 5)
    return [
        f"char_a_p1_0bas_humn_v{bas_v:02d}.png",
        f"1out/char_a_p1_1out_fstr_v{kiyafet_v:02d}.png",
        "4har/char_a_p1_4har_bob1_v00.png",
    ]


# Unvan -> AI avatar dosya adı (kullanıcının üreteceği resimler).
UNVAN_DOSYA: dict[str, str] = {
    "Çırak": "cirak",
    "Yolcu": "yolcu",
    "Cevher": "cevher",
    "Makine": "makine",
    "Usta": "usta",
    "Bilge": "bilge",
    "Aydın": "aydin",
    "Efsane": "efsane",
}


def ai_avatar_yolu(assets_dizini: Path, unvan: str) -> Path | None:
    """Kullanıcının o unvan için ürettiği AI avatar resmi varsa yolu, yoksa None.
    Beklenen dosya: assets/avatar_ai/<unvan>.png (ör. cirak.png, efsane.png)."""
    ad = UNVAN_DOSYA.get(unvan)
    if ad is None:
        return None
    yol = assets_dizini / "avatar_ai" / f"{ad}.png"
    return yol if yol.is_file() else None
