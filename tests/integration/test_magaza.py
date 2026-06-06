"""Mağaza: varsayılan ödüller, fiyat (dakika×maliyet), maliyet tabanı, Puan ile
satın alma (bakiyeden düşer / yetmezse reddeder), geçmiş."""

from datetime import datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.magaza.magaza import fiyat_hesapla, maliyet_sinirla
from leveltodo.domain.stats.statlar import Stat
from leveltodo.domain.tasks.kurallar import Tekrar
from leveltodo.infrastructure.saat import SahteSaat


def test_fiyat_ve_taban():
    assert fiyat_hesapla(35, 4) == 140
    assert fiyat_hesapla(60, 4) == 240  # daha çok dakika daha pahalı
    assert maliyet_sinirla(0) == 1  # taban altına inmez
    assert fiyat_hesapla(10, 0) == 10  # maliyet tabana çekilir (1)


def test_varsayilan_oduller_tohumlanir(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    oduller = c.magaza.oduller()
    adlar = {o.name for o in oduller}
    assert "Arkadaşlarla buluşma" in adlar
    assert len(oduller) == 3


def _puan_kazan(c, miktar):
    # Görev tamamlayıp Puan kazandır (ozel_odul puanı da belirler).
    c.gorevler.gorev_olustur("İş", Tekrar.YOK, ozel_odul=miktar)
    c.gorevler.tamamla(c.gorevler.bugunku_gorevler()[0].kayit_id)


def test_satin_alma_bakiyeden_duser(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    _puan_kazan(c, 200)  # 200 puan
    assert c.magaza.bakiye_puan() == 200

    film = next(o for o in c.magaza.oduller() if o.name == "Dizi/film/video")  # 4 puan/dk
    assert c.magaza.satin_al(film.id, 35) is True  # 35×4 = 140
    assert c.magaza.bakiye_puan() == 60
    assert len(c.magaza.gecmis()) == 1
    assert c.magaza.gecmis()[0].cost == 140

    # 60 puan kaldı; 35 dk film (140) artık alınamaz
    assert c.magaza.satin_al(film.id, 35) is False
    assert c.magaza.bakiye_puan() == 60


def test_maliyet_ayarla_tabanin_altina_inmez(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    odul = c.magaza.oduller()[0]
    c.magaza.maliyet_ayarla(odul.id, 0)  # 0 verildi → tabana (1) çekilir
    yeni = next(o for o in c.magaza.oduller() if o.id == odul.id)
    assert yeni.cost_per_min == 1


def test_stat_dagilimi_etkilenmez_puan_harcaninca(db_url):
    # Puan harcama XP'ye dokunmamalı (yalnız point_transactions).
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.gorevler.gelistirme_xp_ekle(Stat.BEDEN, 100)
    _puan_kazan(c, 100)
    xp_once = c.gorevler.toplamlar()[0]
    odul = c.magaza.oduller()[0]
    c.magaza.satin_al(odul.id, 5)
    assert c.gorevler.toplamlar()[0] == xp_once  # XP değişmedi
