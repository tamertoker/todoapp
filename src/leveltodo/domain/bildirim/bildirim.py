"""Bildirim — saf kurallar (PyQt/OS bağımsız).

Bildirimler dört kategoriye ayrılır; kullanıcı her birini ayrı açıp kapatabilir.
Ayrıca bir "gece sessizliği" aralığı vardır (vars. 23–07): o saatlerde hiçbir
bildirim gösterilmez. `gosterilsin_mi` bu iki kuralı birleştirir; bildirimin
gerçekten gösterilip gösterilmeyeceğine application katmanı buna bakarak karar verir.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class BildirimKategori(StrEnum):
    HATIRLATMA = "hatirlatma"
    KUTLAMA = "kutlama"
    UYARI = "uyari"
    DURTME = "durtme"


@dataclass(frozen=True, slots=True)
class Bildirim:
    kategori: BildirimKategori
    baslik: str
    govde: str


def sessiz_saatte_mi(saat: int, baslangic: int, bitis: int) -> bool:
    """Verilen saat (0–23) gece sessizliği aralığında mı? Aralık gece yarısını
    sarabilir (ör. 23→7: 23,0,1..6 sessiz)."""
    if baslangic == bitis:
        return False
    if baslangic < bitis:
        return baslangic <= saat < bitis
    return saat >= baslangic or saat < bitis  # gece yarısını saran aralık


def gosterilsin_mi(kategori_acik: bool, sessiz_acik: bool, sessiz_saatte: bool) -> bool:
    return kategori_acik and not (sessiz_acik and sessiz_saatte)
