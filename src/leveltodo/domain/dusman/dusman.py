"""Düşman (Şeytan) tanımları ve can formülü — saf, test edilebilir.

Şeytan, tembelliğin görsel düşmanıdır. Kazandığın XP kadar hasar alır; canı
biterse bir üst tier (daha çok canlı) düşman gelir. Tier başına maksimum can
1.5 katına çıkar. Düşman isimleri tier'a göre döner.
"""

from __future__ import annotations

from dataclasses import dataclass

BASE_HP = 100


@dataclass(frozen=True, slots=True)
class Dusman:
    anahtar: str  # sprite dosya adı (örn. "erteleyici")
    ad: str  # ekranda görünen ad
    lore: str


DUSMANLAR: list[Dusman] = [
    Dusman("erteleyici", "Erteleyici", "Küçük ama sinsi; her 'sonra yaparım'da büyür."),
    Dusman("dagilan_golge", "Dağılan Gölge", "Dikkatini dağıtır, seni böler."),
    Dusman("tembel_devi", "Tembel Devi", "Ağır ve uyuşuk; kıpırdamanı engeller."),
    Dusman("karanlik_erteleme", "Karanlık Erteleme", "Ertelemenin en kara hâli."),
]


def dusman_getir(tier: int) -> Dusman:
    return DUSMANLAR[tier % len(DUSMANLAR)]


def max_hp(tier: int) -> int:
    return round(BASE_HP * (1.5**tier))
