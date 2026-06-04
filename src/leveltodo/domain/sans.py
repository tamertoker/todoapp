"""Şans arayüzü (Sans).

Rastgelelik de saat gibi dışarıdan verilir; böylece testlerde "kritik geldi"
ya da "gelmedi" senaryolarını kesin kurabiliriz (gerçek rastgeleliği beklemeden).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Sans(Protocol):
    def kritik_mi(self, olasilik: float) -> bool:
        """Verilen olasılıkla (0..1) True döner."""
        ...
