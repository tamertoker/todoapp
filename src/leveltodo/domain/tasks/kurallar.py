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
from datetime import date, datetime, timedelta
from enum import StrEnum

SURESIZ_VARSAYILAN_ODUL = 5


class Tekrar(StrEnum):
    YOK = "none"           # tek seferlik
    GUNLUK = "daily"       # her gün
    HER_X_GUN = "every_x"  # her X günde bir
    HAFTALIK = "weekly"    # haftanın belirli günleri
    AYLIK = "monthly"      # ayın belirli günü


class GorevDurumu(StrEnum):
    BEKLIYOR = "pending"
    BITTI = "done"


@dataclass(frozen=True, slots=True)
class Odul:
    xp: int
    puan: int


def gunde_olusur_mu(
    tekrar: Tekrar, parametre: str, olusturma_gunu: date, hedef_gun: date
) -> bool:
    """Tekrarlı bir görev, verilen günde oluşmalı mı?

    parametre kodlaması:
    - HER_X_GUN: "3" gibi (kaç günde bir)
    - HAFTALIK: "0,2,4" gibi (haftanın günleri; 0=Pazartesi ... 6=Pazar)
    - AYLIK: "15" gibi (ayın günü)
    """
    if hedef_gun < olusturma_gunu:
        return False
    if tekrar is Tekrar.GUNLUK:
        return True
    if tekrar is Tekrar.HER_X_GUN:
        x = int(parametre) if parametre else 1
        return x > 0 and (hedef_gun - olusturma_gunu).days % x == 0
    if tekrar is Tekrar.HAFTALIK:
        gunler = {int(g) for g in parametre.split(",") if g != ""}
        return hedef_gun.weekday() in gunler
    if tekrar is Tekrar.AYLIK:
        return parametre != "" and hedef_gun.day == int(parametre)
    return False


def onceki_olusum(
    tekrar: Tekrar, parametre: str, olusturma_gunu: date, gun: date
) -> date | None:
    """gun'den önceki en yakın 'oluşma günü' (seri hesabı için). Yoksa None."""
    aday = gun - timedelta(days=1)
    for _ in range(400):  # aylık için en fazla ~31 gün geri; güvenli üst sınır
        if aday < olusturma_gunu:
            return None
        if gunde_olusur_mu(tekrar, parametre, olusturma_gunu, aday):
            return aday
        aday -= timedelta(days=1)
    return None


def sonraki_olusum(
    tekrar: Tekrar, parametre: str, olusturma_gunu: date, gun: date
) -> date | None:
    """gun (dahil) ve sonrasındaki ilk 'oluşma günü'. Yoksa None."""
    aday = max(gun, olusturma_gunu)
    for _ in range(800):  # yıllık vb. için güvenli üst sınır
        if gunde_olusur_mu(tekrar, parametre, olusturma_gunu, aday):
            return aday
        aday += timedelta(days=1)
    return None


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
