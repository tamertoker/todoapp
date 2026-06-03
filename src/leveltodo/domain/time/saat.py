"""Saat arayüzü (Saat).

Kod hiçbir yerde doğrudan `datetime.now()` çağırmaz; her zaman bir Saat
üzerinden zamanı sorar. Böylece testlerde "sahte saat" (SahteSaat) verip
zamanı istediğimiz güne ilerletebiliriz — gerçek saatin geçmesini beklemeden.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable


@runtime_checkable
class Saat(Protocol):
    def simdi(self) -> datetime:
        """Şu anki yerel tarih-saati döndürür."""
        ...
