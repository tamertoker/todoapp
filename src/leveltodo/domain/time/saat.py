"""Saat arayüzü (Saat).

Kod hiçbir yerde doğrudan `datetime.now()` çağırmaz; her zaman bir Saat
üzerinden zamanı sorar. Böylece testlerde "sahte saat" (SahteSaat) verip
zamanı istediğimiz güne ilerletebiliriz — gerçek saatin geçmesini beklemeden.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable


# bu aşağıdaki protokolün runtime'da instance ile kontrol edilebilmesini sağlar
@runtime_checkable
# protokol olduğu için aslında diyoruz ki saat nesnesi şu metodu sağlamalı. sözleşme gibi.
class Saat(Protocol):
    def simdi(self) -> datetime:
        """Şu anki yerel tarih-saati döndürür."""
        ...
