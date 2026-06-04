"""Seri (streak) kuralları — saf, test edilebilir.

İki tür seri var:
- GIRIS: kaç ardışık gün uygulamayı açtın.
- GOREV: kaç ardışık gün en az bir görev tamamladın.

Mantık aynı: bir günü "işaretlersin"; o gün bir öncekinin hemen ertesiyse seri
artar, araya boşluk girerse 1'e döner. Aynı gün ikinci kez işaretlemek bir şey
değiştirmez. Seri uzadıkça rengi değişir.
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum


class SeriTipi(StrEnum):
    GIRIS = "login"
    GOREV = "task"


def seri_ilerlet(
    mevcut: int, en_iyi: int, son_gun: date | None, gun: date
) -> tuple[int, int, date]:
    """(yeni_seri, yeni_rekor, yeni_son_gun) döndürür."""
    if son_gun == gun:
        return mevcut, en_iyi, gun
    if son_gun is not None and (gun - son_gun).days == 1:
        yeni = mevcut + 1
    else:
        yeni = 1
    return yeni, max(en_iyi, yeni), gun


def seri_rengi(sayi: int) -> str:
    """Seri uzunluğuna göre renk (temadan bağımsız, canlı tonlar)."""
    if sayi >= 30:
        return "#ffd24a"  # altın
    if sayi >= 14:
        return "#c86bff"  # mor
    if sayi >= 7:
        return "#4fc3dc"  # mavi
    if sayi >= 3:
        return "#7ed957"  # yeşil
    return "#9a8fb8"  # soluk (kısa seri)
