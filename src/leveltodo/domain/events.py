"""Domain olayları (events).

Bir olay, sistemde "olmuş bitmiş" bir şeyi temsil eder (ör. uygulama açıldı,
görev tamamlandı). Olaylar saf veridir; ne yapılacağını bilmezler. Onları
dinleyen "handler"lar tepki verir (ses çal, bildirim göster, XP ekle...).
Bu sayede yeni bir tepki eklemek, mevcut kodu bozmadan yeni bir dinleyici
eklemekten ibaret olur.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class DomainEvent:
    """Tüm olayların ortak atası. `occurred_at` olayın gerçekleştiği andır."""

    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class AppStarted(DomainEvent):
    """Uygulama açıldığında yayınlanır. Faz 0'da event hattını kanıtlar."""


@dataclass(frozen=True, slots=True)
class TaskCompleted(DomainEvent):
    """Bir görev tamamlandığında yayınlanır; kazanılan XP ve puanı taşır."""

    instance_id: str
    xp: int
    points: int
