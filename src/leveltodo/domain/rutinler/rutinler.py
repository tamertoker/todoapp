"""Rutin alanları — saf kurallar (PyQt/DB yok).

Üç tür rutin alanı var:
- SAYI: günlük bir sayı (kaç bardak su, kaç sayfa). Hedef bir yön taşır:
  EN_AZ (en az şu kadar olsun) ya da EN_FAZLA (şu kadarı geçme).
- EVET_HAYIR: işaretli mi değil mi (0/1). Hedef = işaretlemek.
- METIN: serbest kısa not (ör. "bugünkü ruh hali"). Hedefi/ödülü yoktur; sadece
  günlük takip içindir.

`hedef_tuttu_mu` o günkü değerin hedefi karşılayıp karşılamadığını söyler;
ödülün verilip verilmeyeceğine application katmanı buna bakarak karar verir.
METIN türünün hedefi olmadığından her zaman False döner (ödül yok).
"""

from __future__ import annotations

from enum import StrEnum


class RutinTuru(StrEnum):
    SAYI = "number"
    EVET_HAYIR = "bool"
    METIN = "text"


class Yon(StrEnum):
    EN_AZ = "min"
    EN_FAZLA = "max"


def hedef_tuttu_mu(
    tur: RutinTuru, deger: int, yon: Yon | None = None, hedef: int | None = None
) -> bool:
    if tur is RutinTuru.METIN:
        return False  # metin alanının hedefi/ödülü yok
    if tur is RutinTuru.EVET_HAYIR:
        return deger >= 1
    if hedef is None:
        return False
    if yon is Yon.EN_FAZLA:
        return deger <= hedef
    return deger >= hedef  # EN_AZ (varsayılan)
