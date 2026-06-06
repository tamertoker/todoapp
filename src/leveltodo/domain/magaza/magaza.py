"""Mağaza — saf kurallar (PyQt/DB yok).

Oyun-içi Puan, gerçek-hayat ödüllerini (dizi, buluşma, oyun…) DAKİKA cinsinden
satın almak için harcanır. Her ödülün bir 'dk başına puan maliyeti' vardır;
kullanıcı bunu değiştirebilir ama bir TABAN sınırının altına inemez. Fiyat
basitçe dakika × dk-maliyetidir.
"""

from __future__ import annotations

MIN_DK_MALIYET = 1  # bir dakikanın en düşük puan maliyeti

# (ad, dk başına puan maliyeti) — ilk açılışta yüklenen varsayılan ödüller.
VARSAYILAN_ODULLER: tuple[tuple[str, int], ...] = (
    ("Arkadaşlarla buluşma", 2),
    ("Dizi/film/video", 4),
    ("Bilgisayar oyunu", 5),
)


def maliyet_sinirla(deger: int) -> int:
    """Dk maliyetini tabana sabitler (altına inemez)."""
    return max(MIN_DK_MALIYET, int(deger))


def fiyat_hesapla(dakika: int, dk_maliyet: int) -> int:
    """Toplam puan fiyatı = dakika × dk-maliyeti (negatif dakika 0 sayılır)."""
    return max(0, dakika) * maliyet_sinirla(dk_maliyet)
