"""Şans arayüzünün gerçek implementasyonu (rastgele sayı)."""

from __future__ import annotations

import random


class GercekSans:
    def kritik_mi(self, olasilik: float) -> bool:
        return random.random() < olasilik
