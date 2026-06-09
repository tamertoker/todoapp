"""Saat arayüzünün gerçek ve test implementasyonları.

- SistemSaati: gerçek sistem saatini kullanır (uygulama çalışırken).
- SahteSaat: testlerde sabit bir zaman verir ve istenince ileri alınabilir;
  böylece "yarın", "3 gün sonra" gibi senaryolar anında test edilir.
"""

from __future__ import annotations

from datetime import datetime, timedelta

# domain'de saat dosyasında simdi fonksiyonunu protokol ile beraber tanımlamıştım,
# burada da hepsinde simdi olmak zorunda.


class SistemSaati:
    def simdi(self) -> datetime:
        return datetime.now()


class AyarlanabilirSaat:
    """Gerçek saati kullanır ama gün/zaman kaydırılabilir (debug menüsü için).
    Varsayılan kaydırma 0 olduğundan normalde sistem saatiyle aynıdır."""

    def __init__(self) -> None:
        self._ofset = timedelta()

    def simdi(self) -> datetime:
        return datetime.now() + self._ofset

    def gun_kaydir(self, gun: int) -> None:
        self._ofset += timedelta(days=gun)

    def saate_atla(self, hedef_saat: int) -> None:
        """Şimdiki saati verilen saate getirir (debug: sabah/öğle/akşam avatar testi)."""
        self._ofset += timedelta(hours=hedef_saat - self.simdi().hour)

    def sifirla(self) -> None:
        self._ofset = timedelta()

    def ofset_gun(self) -> int:
        return self._ofset.days


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
