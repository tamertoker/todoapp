"""İrade eylemleri: Disiplin statına XP yazar, listelenir, seviye atlatınca dondurma verir."""

from datetime import datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.stats.statlar import Stat
from leveltodo.infrastructure.saat import SahteSaat


def test_irade_eylemi_disiplin_xp_yazar(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    assert c.gorevler.stat_durumlari()[Stat.DISIPLIN].seviye == 0

    c.irade.ekle("Erken kalktım", 600)
    assert c.gorevler.stat_durumlari()[Stat.DISIPLIN].seviye == 1  # 600 >= 504

    eylemler = c.irade.son_eylemler()
    assert len(eylemler) == 1
    assert eylemler[0].title == "Erken kalktım" and eylemler[0].xp == 600


def test_irade_profil_seviyesi_dondurma_verir(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.irade.ekle("Büyük irade sınavı", 1584)  # Disiplin seviye 3 → profil 3
    assert c.gorevler.profil_durumu()[0] == 3
    assert c.dondurma.stok() == 1  # 3 levelde bir → +1
