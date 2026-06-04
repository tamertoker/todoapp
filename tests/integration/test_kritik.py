"""Kritik başarı: kritikte hem XP hem Puan ikiye katlanır (şans servisiyle test)."""

from datetime import datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.tasks.kurallar import Tekrar
from leveltodo.infrastructure.saat import SahteSaat


class SabitSans:
    def __init__(self, deger: bool) -> None:
        self._deger = deger

    def kritik_mi(self, olasilik: float) -> bool:
        return self._deger


def test_kritik_odulu_ikiye_katlar(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat, sans=SabitSans(True))
    c.gorevler.gorev_olustur("İş", Tekrar.YOK, ozel_odul=10)
    satir = c.gorevler.bugunku_gorevler()[0]

    odul = c.gorevler.tamamla(satir.kayit_id)
    assert odul is not None and odul.xp == 20 and odul.puan == 20  # 10 × 2
    assert c.gorevler.toplamlar() == (20, 20)


def test_kritik_yoksa_normal_odul(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat, sans=SabitSans(False))
    c.gorevler.gorev_olustur("İş", Tekrar.YOK, ozel_odul=10)
    satir = c.gorevler.bugunku_gorevler()[0]

    odul = c.gorevler.tamamla(satir.kayit_id)
    assert odul is not None and odul.xp == 10 and odul.puan == 10
