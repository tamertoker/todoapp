"""Statlar, seviye eğrisi ve unvanlar (saf kurallar).

Dört stat var. Üçü görevlerle büyür (kullanıcı her göreve bir stat seçer);
Disiplin yalnızca irade eylemleriyle büyür (Faz 5).

Seviye eğrisi: bir stat'ı 'seviye'ye çıkarmak için gereken XP, plandaki saat
eğrisinden gelir — (8 + 0.4×seviye) saat. 1 XP ≈ 1 dakika kabul edildiğinden
1 saat ≈ 60 XP. Böylece üst seviyeler giderek daha fazla emek ister.

Profil seviyesi ayrı bir formülle değil, dört stat seviyesinin toplamıyla
bulunur. Unvanlar bu profil seviyesine göre, artan bantlarla verilir.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Stat(StrEnum):
    ENTELEKTUELLIK = "entelektuellik"
    BEDEN = "beden"
    FARKINDALIK = "farkindalik"
    DISIPLIN = "disiplin"


STAT_ETIKET: dict[Stat, str] = {
    Stat.ENTELEKTUELLIK: "Entelektüellik",
    Stat.BEDEN: "Beden",
    Stat.FARKINDALIK: "Farkındalık",
    Stat.DISIPLIN: "Disiplin",
}

# Görevle geliştirilebilen statlar (Disiplin irade eylemlerinden gelir — Faz 5).
GOREV_STATLARI: tuple[Stat, ...] = (Stat.ENTELEKTUELLIK, Stat.BEDEN, Stat.FARKINDALIK)


def _seviye_esigi(seviye: int) -> int:
    """'seviye' seviyesine çıkmak için gereken XP (bir önceki seviyeden)."""
    return round((8 + 0.4 * seviye) * 60)


@dataclass(frozen=True, slots=True)
class SeviyeDurumu:
    seviye: int
    bu_seviyedeki_xp: int    # mevcut seviyede biriken XP
    sonraki_seviye_esigi: int  # sonraki seviyeye geçmek için gereken XP


def seviye_hesapla(toplam_xp: int) -> SeviyeDurumu:
    seviye = 0
    kalan = max(0, toplam_xp)
    while True:
        esik = _seviye_esigi(seviye + 1)
        if kalan >= esik:
            kalan -= esik
            seviye += 1
        else:
            return SeviyeDurumu(seviye=seviye, bu_seviyedeki_xp=kalan, sonraki_seviye_esigi=esik)


# (üst sınır dahil, unvan). Profil seviyesi bu sınırın altında/eşitse o unvan geçerli.
_UNVAN_BANTLARI: tuple[tuple[int, str], ...] = (
    (3, "Çırak"),
    (8, "Yolcu"),
    (16, "Cevher"),
    (26, "Makine"),
    (41, "Usta"),
    (61, "Bilge"),
    (86, "Aydın"),
)
_SON_UNVAN = "Efsane"


@dataclass(frozen=True, slots=True)
class UnvanDurumu:
    unvan: str
    sonraki_unvan: str | None
    sonraki_unvana_kalan: int | None  # kaç profil seviyesi kaldı


def unvan_hesapla(profil_seviye: int) -> UnvanDurumu:
    for indeks, (ust_sinir, ad) in enumerate(_UNVAN_BANTLARI):
        if profil_seviye <= ust_sinir:
            if indeks + 1 < len(_UNVAN_BANTLARI):
                sonraki = _UNVAN_BANTLARI[indeks + 1][1]
            else:
                sonraki = _SON_UNVAN
            return UnvanDurumu(
                unvan=ad,
                sonraki_unvan=sonraki,
                sonraki_unvana_kalan=ust_sinir + 1 - profil_seviye,
            )
    return UnvanDurumu(unvan=_SON_UNVAN, sonraki_unvan=None, sonraki_unvana_kalan=None)
