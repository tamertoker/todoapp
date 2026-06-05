"""Uyandırma disiplini — saf kurallar (PyQt/DB yok).

Bir hedef uyanış saati belirlenir. Sabah "kalktım" denince gerçek saat, hedefe
(küçük bir tolerans payıyla) yetişmiş mi diye bakılır. Vizyon ilkesi gereği CEZA
YOKTUR: zamanında kalkarsan Disiplin'e XP kazanırsın, geç kalırsan sadece ödül
alamazsın.
"""

from __future__ import annotations

UYANDIRMA_ODUL_XP = 50
TOLERANS_DK = 15


def dakikaya(saat_metni: str) -> int:
    """'07:30' → günün dakikası (450). Bozuk girdi 0 sayılır."""
    try:
        saat, dakika = saat_metni.split(":")
        return int(saat) * 60 + int(dakika)
    except (ValueError, AttributeError):
        return 0


def uyanma_basarili_mi(hedef_dk: int, gercek_dk: int, tolerans: int = TOLERANS_DK) -> bool:
    """Gerçek kalkış, hedef + tolerans içindeyse (ya da daha erkense) başarılı."""
    return gercek_dk <= hedef_dk + tolerans
