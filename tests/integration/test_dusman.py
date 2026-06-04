"""Düşman: can formülü, hasar, tier yenileme; görev tamamlama düşmana hasar verir."""

from datetime import datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.dusman.dusman import DUSMANLAR, dusman_getir, max_hp
from leveltodo.domain.tasks.kurallar import Tekrar
from leveltodo.infrastructure.saat import SahteSaat


def test_max_hp_tier_ile_artar():
    assert max_hp(0) == 100
    assert max_hp(1) == 150  # round(100 * 1.5)
    assert max_hp(2) == 225  # round(100 * 2.25)


def test_dusman_tier_ile_doner():
    assert dusman_getir(0).anahtar == "erteleyici"
    assert dusman_getir(len(DUSMANLAR)).anahtar == DUSMANLAR[0].anahtar


def test_hasar_ve_tier_yenileme(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    _, hp, maks, tier = c.dusman.durum()
    assert (tier, hp, maks) == (0, 100, 100)

    c.dusman.hasar_ver(30)
    assert c.dusman.durum()[1] == 70

    c.dusman.hasar_ver(100)  # 70 - 100 <= 0 → bir üst tier, tam can
    dusman2, hp2, maks2, tier2 = c.dusman.durum()
    assert (tier2, hp2, maks2) == (1, 150, 150)
    assert dusman2.anahtar == "dagilan_golge"


def test_gorev_tamamlama_dusmana_hasar_verir(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.gorevler.gorev_olustur("İş", Tekrar.YOK, ozel_odul=20)
    satir = c.gorevler.bugunku_gorevler()[0]
    c.gorevler.tamamla(satir.kayit_id)  # 20 XP → düşmana 20 hasar
    assert c.dusman.durum()[1] == 80  # 100 - 20
