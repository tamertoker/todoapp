"""Tamamlama geri bildirim mesajları — tek tip olmasın diye rotasyonlu havuz.

Ton: gündelik, doğal Türkçe + epik bir alt ton; uygulamanın "irade" temasıyla
örtüşür. Hangisinin çıkacağı rastgeledir.
"""

from __future__ import annotations

import random

_NORMAL = [
    "+{xp} XP. Bir tuğla daha yerine oturdu.",
    "+{xp} XP. Çoğu kişi başlamazdı bile; sen bitirdin.",
    "+{xp} XP. Disiplin işte böyle anlardan örülür.",
    "+{xp} XP. Küçük adım, sağlam yol.",
    "+{xp} XP. İrade kasın biraz daha büyüdü.",
    "+{xp} XP. Söz verip tuttun — fark tam burada.",
    "+{xp} XP. Sırada ne var?",
]

_KRITIK = [
    "⚡ KRİTİK! +{xp} XP, +{puan} puan — iki katı! Tam isabet.",
    "⚡ KRİTİK vuruş! Emeğin ikiye katlandı: +{xp} XP, +{puan} puan.",
    "⚡ KRİTİK! Bugün şans senden yana: +{xp} XP, +{puan} puan.",
]

_COMBO = [
    "🔥 COMBO! Akışı yakaladın — 1 saat boyunca her şey ×1.5.",
    "🔥 COMBO başladı! Ritim sende; 1 saat ×1.5 ödül.",
    "🔥 COMBO! Üç vuruş üst üste — 1 saat boyunca ×1.5.",
]


def tamamlama_mesaji(xp: int) -> str:
    return random.choice(_NORMAL).format(xp=xp)


def kritik_mesaji(xp: int, puan: int) -> str:
    return random.choice(_KRITIK).format(xp=xp, puan=puan)


def combo_mesaji() -> str:
    return random.choice(_COMBO)
