"""Gun — "mantıksal gün" kavramı.

Sorun: Gece 03:00'te uygulamayı açan biri için bu hâlâ "dünkü gün" olmalı.
Çözüm: Kullanıcının belirlediği bir "gün başlangıç saati" (varsayılan 04:00)
vardır. O saatten önceki her an, bir önceki güne sayılır.

Örnek (gün başlangıcı 04:00):
- 2 Haziran 03:30 → mantıksal gün = 1 Haziran
- 2 Haziran 04:30 → mantıksal gün = 2 Haziran
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta


@dataclass(frozen=True, slots=True, order=True)
class Gun:
    tarih: date

    @classmethod
    def olustur(cls, an: datetime, gun_baslangic_saati: int) -> Gun:
        if not 0 <= gun_baslangic_saati <= 23:
            raise ValueError("gun_baslangic_saati 0 ile 23 arasında olmalı")
        return cls((an - timedelta(hours=gun_baslangic_saati)).date())

    def __str__(self) -> str:
        return self.tarih.isoformat()
