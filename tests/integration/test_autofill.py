"""Autofill veri katmanı: önceki girişlerden öneri + o değere ait SON kaydı
döndürme (görev, cüzdan, irade, mağaza)."""

from datetime import datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.stats.statlar import Stat
from leveltodo.domain.tasks.kurallar import Tekrar
from leveltodo.infrastructure.saat import SahteSaat


def _c(db_url):
    return build_container(db_url=db_url, saat=SahteSaat(datetime(2026, 6, 1, 10, 0)))


def test_gorev_baslik_onerisi_son_sablonu_doldurur(db_url):
    c = _c(db_url)
    c.gorevler.gorev_olustur("Koşu", Tekrar.GUNLUK, ozel_odul=25, stat=Stat.BEDEN)
    assert "Koşu" in c.gorevler.baslik_onerileri()
    sablon = c.gorevler.sablon_oneri("Koşu")
    assert sablon is not None
    assert sablon.recurrence == "daily"
    assert sablon.reward_override == 25
    assert sablon.stat == Stat.BEDEN.value


def test_cuzdan_aciklama_onerisi_son_islemi_doldurur(db_url):
    c = _c(db_url)
    c.cuzdan.islem_ekle(2000000, "gelir", "maaş")  # 20.000 TL
    c.cuzdan.islem_ekle(1500, "gider", "kahve")
    assert set(c.cuzdan.aciklama_onerileri()) == {"maaş", "kahve"}
    islem = c.cuzdan.islem_oneri("maaş")
    assert islem is not None and islem.amount == 2000000 and islem.tur == "gelir"


def test_irade_baslik_onerisi_son_xp(db_url):
    c = _c(db_url)
    c.irade.ekle("erken kalktım", 80)
    assert "erken kalktım" in c.irade.baslik_onerileri()
    assert c.irade.eylem_oneri("erken kalktım").xp == 80


def test_magaza_ad_onerisi_son_maliyet(db_url):
    c = _c(db_url)
    c.magaza.odul_ekle("Kahve molası", 3)
    assert "Kahve molası" in c.magaza.ad_onerileri()
    assert c.magaza.maliyet_oneri("Kahve molası") == 3
    assert c.magaza.maliyet_oneri("yok böyle") is None
