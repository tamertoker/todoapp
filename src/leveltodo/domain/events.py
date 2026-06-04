from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class DomainEvent:
    #Olayların gerçekleştiği an
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class AppStarted(DomainEvent):
    """Uygulama açıldığında yayınlanır.""" 


@dataclass(frozen=True, slots=True)
class TaskCompleted(DomainEvent):
    """Bir görev tamamlandığında yayınlanır; kazanılan XP ve puanı taşır."""

    instance_id: str
    xp: int
    points: int
    kritik: bool = False
    combo_tetik: bool = False
