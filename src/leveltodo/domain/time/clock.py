"""Saat arayüzü (IClock).

Kod hiçbir yerde doğrudan `datetime.now()` çağırmaz; her zaman bir IClock
üzerinden zamanı sorar. Böylece testlerde "sahte saat" (FakeClock) verip
zamanı istediğimiz güne ilerletebiliriz — gerçek saatin geçmesini beklemeden.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable


@runtime_checkable
class IClock(Protocol):
    def now(self) -> datetime:
        """Şu anki yerel tarih-saati döndürür."""
        ...
