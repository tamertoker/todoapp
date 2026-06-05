"""Mentor dürtmeleri — saf metin havuzu.

Mentor, düşmanın kötü-ikizidir: düşman tembelliğe çağırır, Mentor seni ileri iter.
Bir gelişim alanına (stat) uzun süre dokunulmadığında durumsal bir dürtme seçilir.
Seçim tohuma (günün sıra numarası) göre deterministiktir.
"""

from __future__ import annotations

MENTOR_DURTMELERI: tuple[str, ...] = (
    "{gun} gündür {stat} sessiz. Küçük bir adım at, kas körelmesin.",
    "{stat} seni bekliyor — {gun} gündür hiç dokunmadın.",
    "{gun} gün ara verdin {stat} için. Bugün bir kıvılcım yeter.",
    "Unutma: {stat} ancak emekle büyür. {gun} gündür beslenmedi.",
    "{stat} tarafın paslanıyor — {gun} gündür beklemede. Hadi.",
)


def mentor_durtme(stat_ad: str, gun: int, tohum: int) -> str:
    return MENTOR_DURTMELERI[tohum % len(MENTOR_DURTMELERI)].format(stat=stat_ad, gun=gun)
