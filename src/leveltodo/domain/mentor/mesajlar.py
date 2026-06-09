"""Mentor dürtmeleri — saf metin havuzu.

Mentor, düşmanın kötü-ikizidir: düşman tembelliğe çağırır, Mentor seni ileri iter.
Bir gelişim alanına (stat) uzun süre dokunulmadığında durumsal bir dürtme seçilir.
Seçim tohuma (günün sıra numarası) göre deterministiktir.
"""

from __future__ import annotations

MENTOR_DURTMELERI: tuple[str, ...] = (
    "{gun} gündür {stat} tarafına hiç bakmadın. Bugün ufak bir şey yapsan?",
    "{stat} biraz ihmal oldu — {gun} gün geçmiş. Beş dakikalık bir şeyle aç hesabı.",
    "{gun} gündür {stat} yok ortalıkta. Çok değil, bir adım yeter bugün.",
    "{stat} için {gun} gün ara vermişsin. Bugün küçük bir başlangıç iyi gelir.",
    "{gun} gündür {stat} beklemede. Bir kıvılcım at, gerisi gelir.",
)


def mentor_durtme(stat_ad: str, gun: int, tohum: int) -> str:
    return MENTOR_DURTMELERI[tohum % len(MENTOR_DURTMELERI)].format(stat=stat_ad, gun=gun)
