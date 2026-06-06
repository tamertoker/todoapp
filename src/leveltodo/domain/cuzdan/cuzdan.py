"""Cüzdan — saf yardımcılar (PyQt/DB yok).

Para her yerde KURUŞ (tam sayı) olarak dolaşır; ekrana yazarken TL'ye çevrilir.
Wishlist ilerlemesi, cüzdan bakiyesinin öğe fiyatına oranıdır (0..1).
"""

from __future__ import annotations


def ilerleme_orani(bakiye_kurus: int, fiyat_kurus: int) -> float:
    """Bakiyenin fiyata oranı, 0 ile 1 arasına sıkıştırılmış."""
    if fiyat_kurus <= 0:
        return 1.0
    return max(0.0, min(1.0, bakiye_kurus / fiyat_kurus))


def kurus_tl(kurus: int) -> str:
    """123456 kuruş → '1.234,56 ₺' (Türkçe biçim: nokta binlik, virgül kuruş)."""
    eksi = "-" if kurus < 0 else ""
    kurus = abs(int(kurus))
    tam, kalan = divmod(kurus, 100)
    binlik = f"{tam:,}".replace(",", ".")
    return f"{eksi}{binlik},{kalan:02d} ₺"
