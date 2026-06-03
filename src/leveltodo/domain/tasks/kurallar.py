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

SURESIZ_VARSAYILAN_ODUL = 5


class Tekrar(StrEnum):
    YOK = "none"      # tek seferlik
    GUNLUK = "daily"  # her gün tekrar


class GorevDurumu(StrEnum):
    BEKLIYOR = "pending"
    BITTI = "done"


@dataclass(frozen=True, slots=True)
class Odul:
    xp: int
    puan: int


def odul_hesapla(calisilan_saniye: int, ozel_deger: int | None) -> Odul:
    if ozel_deger is not None:
        taban = ozel_deger
    elif calisilan_saniye > 0:
        taban = max(1, round(calisilan_saniye / 60))
    else:
        taban = SURESIZ_VARSAYILAN_ODUL
    return Odul(xp=taban, puan=taban)


def canli_sure(
    islenmis_saniye: int, segment_baslangici: datetime | None, simdi: datetime
) -> int:
    """Kronometre çalışıyorsa, kaydedilmiş süreye o anki segmenti ekler."""
    if segment_baslangici is None:
        return islenmis_saniye
    return islenmis_saniye + max(0, int((simdi - segment_baslangici).total_seconds()))
