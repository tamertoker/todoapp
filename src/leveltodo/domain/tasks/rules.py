"""Görevlerle ilgili saf kurallar (PyQt ve veritabanından bağımsız).

Burada "para hesabı" yapılır ama hiçbir şey saklanmaz veya gösterilmez —
sadece girdi alıp sonuç döndüren kurallar. Bu yüzden saniyeler içinde test
edilebilir.

Ödül mantığı (Faz 1):
- Kullanıcı göreve elle özel bir değer verdiyse, o değer geçerli.
- Yoksa ve kronometre çalıştıysa: her dakika için 1 birim (en az 1).
- Yoksa ve kronometre hiç çalışmadıysa (sadece "bitti" işaretlendiyse):
  sabit küçük bir ödül.
XP ve Puan şimdilik aynı taban değeri alır; ileride ayrı ayrı ayarlanabilir.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

UNTIMED_DEFAULT_REWARD = 5


class Recurrence(StrEnum):
    NONE = "none"   # tek seferlik
    DAILY = "daily"  # her gün tekrar


class TaskStatus(StrEnum):
    PENDING = "pending"
    DONE = "done"


@dataclass(frozen=True, slots=True)
class Reward:
    xp: int
    points: int


def compute_reward(elapsed_seconds: int, override: int | None) -> Reward:
    if override is not None:
        base = override
    elif elapsed_seconds > 0:
        base = max(1, round(elapsed_seconds / 60))
    else:
        base = UNTIMED_DEFAULT_REWARD
    return Reward(xp=base, points=base)


def live_elapsed(
    committed_seconds: int, segment_started_at: datetime | None, now: datetime
) -> int:
    """Kronometre çalışıyorsa, kaydedilmiş süreye o anki segmenti ekler."""
    if segment_started_at is None:
        return committed_seconds
    return committed_seconds + max(0, int((now - segment_started_at).total_seconds()))
