"""Tamamlama geri bildirim mesajları — tek tip olmasın diye rotasyonlu havuz.

Ton: gündelik, doğal Türkçe + epik bir alt ton; uygulamanın "irade" temasıyla
örtüşür. Hangisinin çıkacağı rastgeledir.
"""

from __future__ import annotations

import random

_NORMAL = [
    "+{xp} XP. Bir görev daha bitti, eline sağlık.",
    "+{xp} XP. Bravo, hadi sıradaki.",
    "+{xp} XP. Ertelemedin, hallettin. Güzel.",
    "+{xp} XP. Momentum yakaladın, bozma.",
]

_KRITIK = [
    "KRİTİK geldi! +{xp} XP, +{puan} puan. Bugün şans yanında.",
    "KRİTİK! Aynı işe çifte karşılık: +{xp} XP, +{puan} puan.",
    "KRİTİK vuruş, ikiye katlandı: +{xp} XP, +{puan} puan. Aferin.",
]

_COMBO = [
    "Üç işi üst üste devirdin — 1 saat boyunca ödüller 1,5 kat. Bas gaza.",
    "Combo açıldı. Ritmi bozma; 1 saat boyunca her şey 1,5 kat."
]


def tamamlama_mesaji(xp: int) -> str:
    return random.choice(_NORMAL).format(xp=xp)


def kritik_mesaji(xp: int, puan: int) -> str:
    return random.choice(_KRITIK).format(xp=xp, puan=puan)


def combo_mesaji() -> str:
    return random.choice(_COMBO)
