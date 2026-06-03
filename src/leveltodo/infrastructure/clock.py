"""IClock'un gerçek ve test implementasyonları.

- SystemClock: gerçek sistem saatini kullanır (uygulama çalışırken).
- FakeClock: testlerde sabit bir zaman verir ve istenince ileri alınabilir;
  böylece "yarın", "3 gün sonra" gibi senaryolar anında test edilir.
"""

from __future__ import annotations

from datetime import datetime, timedelta


class SystemClock:
    def now(self) -> datetime:
        return datetime.now()


class FakeClock:
    def __init__(self, start: datetime) -> None:
        self._now = start

    def now(self) -> datetime:
        return self._now

    def set(self, moment: datetime) -> None:
        self._now = moment

    def advance(self, **delta: float) -> None:
        """Saati ileri al, ör. advance(days=1) ya da advance(hours=2)."""
        self._now += timedelta(**delta)
