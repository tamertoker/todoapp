"""Cüzdan: gelir/gider + bakiye, aylık özet (iki hedef), wishlist ilerlemesi
(bakiyeye göre), kuruş→TL biçimi."""

from datetime import datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.cuzdan.cuzdan import ilerleme_orani, kurus_tl
from leveltodo.infrastructure.saat import SahteSaat


def test_ilerleme_ve_bicim():
    assert ilerleme_orani(5000, 10000) == 0.5
    assert ilerleme_orani(20000, 10000) == 1.0  # taşmaz
    assert ilerleme_orani(0, 0) == 1.0  # fiyatsız
    assert kurus_tl(123456) == "1.234,56 ₺"
    assert kurus_tl(-5000) == "-50,00 ₺"


def test_gelir_gider_bakiye(db_url):
    saat = SahteSaat(datetime(2026, 6, 10, 12, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.cuzdan.islem_ekle(100000, "gelir", "maaş")  # 1000 TL
    c.cuzdan.islem_ekle(30000, "gider", "market")  # 300 TL
    assert c.cuzdan.bakiye() == 70000  # 700 TL
    assert len(c.cuzdan.son_islemler()) == 2


def test_aylik_ozet_iki_hedef(db_url):
    saat = SahteSaat(datetime(2026, 6, 10, 12, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.cuzdan.hedefler_ayarla(tasarruf_hedefi=50000, harcama_butcesi=40000)
    c.cuzdan.islem_ekle(100000, "gelir")
    c.cuzdan.islem_ekle(30000, "gider")
    # Önceki ay işlemi bu aya sayılmamalı
    saat.ayarla(datetime(2026, 5, 1, 12, 0))
    c.cuzdan.islem_ekle(99999, "gider")
    saat.ayarla(datetime(2026, 6, 10, 12, 0))

    ozet = c.cuzdan.aylik_ozet()
    assert ozet.bu_ay_gelir == 100000
    assert ozet.bu_ay_gider == 30000
    assert ozet.tasarruf == 70000
    assert ozet.tasarruf_hedefi == 50000
    assert ozet.harcama_butcesi == 40000


def test_wishlist_bakiyeye_gore_ilerler(db_url):
    saat = SahteSaat(datetime(2026, 6, 10, 12, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.cuzdan.islem_ekle(60000, "gelir")  # bakiye 600 TL
    c.cuzdan.wishlist_ekle("Kulaklık", 100000)  # 1000 TL
    satir = c.cuzdan.wishlist()[0]
    assert satir.ad == "Kulaklık"
    assert abs(satir.oran - 0.6) < 1e-9

    c.cuzdan.wishlist_sil(satir.id)
    assert c.cuzdan.wishlist() == []
