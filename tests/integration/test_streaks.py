"""Seri sistemi: giriş ve görev serileri ardışık günlerde artar, boşlukta sıfırlanır."""

from datetime import datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.streaks.seriler import SeriTipi
from leveltodo.domain.tasks.kurallar import Tekrar
from leveltodo.infrastructure.saat import SahteSaat


def test_giris_serisi_ardisik_gun_ve_bosluk(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)

    c.seri.giris_kaydet()
    assert c.seri.durumlar()[SeriTipi.GIRIS] == (1, 1)

    saat.ilerlet(days=1)
    c.seri.giris_kaydet()
    assert c.seri.durumlar()[SeriTipi.GIRIS] == (2, 2)

    c.seri.giris_kaydet()  # aynı gün tekrar → değişmez
    assert c.seri.durumlar()[SeriTipi.GIRIS] == (2, 2)

    saat.ilerlet(days=3)  # araya boşluk
    c.seri.giris_kaydet()
    assert c.seri.durumlar()[SeriTipi.GIRIS] == (1, 2)  # seri 1, rekor 2 korunur


def test_gorev_serisi_tamamlamayla_artar(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)

    c.gorevler.gorev_olustur("Her gün", Tekrar.GUNLUK)
    c.gorevler.tamamla(c.gorevler.bugunku_gorevler()[0].kayit_id)
    assert c.seri.durumlar()[SeriTipi.GOREV][0] == 1

    saat.ilerlet(days=1)
    c.gorevler.tamamla(c.gorevler.bugunku_gorevler()[0].kayit_id)
    assert c.seri.durumlar()[SeriTipi.GOREV][0] == 2
