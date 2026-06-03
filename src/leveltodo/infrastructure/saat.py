"""Saat arayüzünün gerçek ve test implementasyonları.

- SistemSaati: gerçek sistem saatini kullanır (uygulama çalışırken).
- SahteSaat: testlerde sabit bir zaman verir ve istenince ileri alınabilir;
  böylece "yarın", "3 gün sonra" gibi senaryolar anında test edilir.
"""

from __future__ import annotations

from datetime import datetime, timedelta


class SistemSaati:
    def simdi(self) -> datetime:
        return datetime.now()


class SahteSaat:
    def __init__(self, baslangic: datetime) -> None:
        self._an = baslangic

    def simdi(self) -> datetime:
        return self._an

    def ayarla(self, an: datetime) -> None:
        self._an = an

    def ilerlet(self, **delta: float) -> None:
        """Saati ileri al, ör. ilerlet(days=1) ya da ilerlet(hours=2)."""
        self._an += timedelta(**delta)
