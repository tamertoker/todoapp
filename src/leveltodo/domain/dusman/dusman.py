"""Düşman (Şeytan) tanımları ve can formülü — saf, test edilebilir.

Şeytan, tembelliğin görsel düşmanıdır. Kazandığın XP kadar (hasar katsayısıyla
ölçeklenmiş) hasar alır; canı biterse bir üst tier (daha çok canlı) düşman gelir.
Tier başına maksimum can 1.5 katına çıkar. Hiç XP kazanmadığın her gün düşman
biraz iyileşir (tembellik onu güçlendirir). Düşman isimleri tier'a göre döner.
"""

from __future__ import annotations

from dataclasses import dataclass

BASE_HP = 100
# Kazanılan XP'nin hasara çevrilirken çarpıldığı katsayı (denge ayarı).
HASAR_KATSAYISI = 1.0
# XP kazanmadan geçen her gün düşman maksimum canının bu oranı kadar iyileşir.
GUNLUK_IYILESME_ORANI = 0.03


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


# Düşmanın ara sıra fısıldadığı kışkırtmalar — seni tembelliğe çağıran ses.
KISKIRTMALAR: tuple[str, ...] = (
    "Amaan, bugün de olmadı; yarın nasılsa yaparsın...",
    "Otur otur, görevler kaçmıyor ya.",
    "Bir mola daha? Sonuçta hak ettin.",
    "Yarın bol bol vaktin olacak, merak etme.",
    "Bugünlük bu kadar yeter, kendine bu kadar yüklenme.",
    "Şu an pek havanda değilsin, zorlama.",
    "Küçük bir es ver; zaten dünya kurtarmıyorsun.",
)


def dusman_getir(tier: int) -> Dusman:
    return DUSMANLAR[tier % len(DUSMANLAR)]


def kiskirtma_sec(tohum: int) -> str:
    """Verilen tohuma (ör. günün sıra numarası) göre bir kışkırtma seçer."""
    return KISKIRTMALAR[tohum % len(KISKIRTMALAR)]


def max_hp(tier: int) -> int:
    return round(BASE_HP * (1.5**tier))


def hasar(xp: int) -> int:
    """Kazanılan XP'yi katsayıyla düşman hasarına çevirir."""
    return round(xp * HASAR_KATSAYISI)


def gunluk_iyilesme(maks_hp: int) -> int:
    """Bir XP'siz günde düşmanın iyileşeceği can miktarı."""
    return round(maks_hp * GUNLUK_IYILESME_ORANI)
