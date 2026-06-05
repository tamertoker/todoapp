"""Bildirim: kategori aç/kapa, gece sessizliği (gece yarısını saran aralık),
kanal dağıtımı."""

from datetime import datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.bildirim.bildirim import (
    BildirimKategori,
    gosterilsin_mi,
    sessiz_saatte_mi,
)
from leveltodo.infrastructure.saat import SahteSaat


# — Saf kurallar —
def test_sessiz_saatte_mi_gece_yarisini_sarar():
    assert sessiz_saatte_mi(23, 23, 7) is True
    assert sessiz_saatte_mi(3, 23, 7) is True
    assert sessiz_saatte_mi(6, 23, 7) is True
    assert sessiz_saatte_mi(7, 23, 7) is False
    assert sessiz_saatte_mi(12, 23, 7) is False
    # Sarmayan aralık
    assert sessiz_saatte_mi(13, 12, 14) is True
    assert sessiz_saatte_mi(15, 12, 14) is False


def test_gosterilsin_mi_kurallari():
    assert gosterilsin_mi(True, False, False) is True
    assert gosterilsin_mi(False, False, False) is False  # kategori kapalı
    assert gosterilsin_mi(True, True, True) is False  # sessiz saatte
    assert gosterilsin_mi(True, True, False) is True  # sessiz açık ama saat dışı


# — Servis (entegrasyon) —
def _gelenler(c):
    gelen = []
    c.bildirim.kanal_ekle(gelen.append)
    return gelen


def test_kapali_kategori_gosterilmez(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 12, 0))  # gündüz
    c = build_container(db_url=db_url, saat=saat)
    gelen = _gelenler(c)

    assert c.bildirim.bildir(BildirimKategori.KUTLAMA, "Aferin", "XP kazandın") is True
    assert len(gelen) == 1

    c.bildirim.kategori_ayarla(BildirimKategori.KUTLAMA, False)
    assert c.bildirim.bildir(BildirimKategori.KUTLAMA, "Aferin", "tekrar") is False
    assert len(gelen) == 1  # ikincisi gösterilmedi


def test_gece_sessizliginde_bastirilir(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 2, 0))  # gece 02:00, vars. sessiz 23-07
    c = build_container(db_url=db_url, saat=saat)
    gelen = _gelenler(c)
    assert c.bildirim.bildir(BildirimKategori.HATIRLATMA, "Hey", "görev var") is False
    assert gelen == []

    # Sessizliği kapatınca aynı saatte gösterilir.
    c.bildirim.sessiz_ayarla(False, 23, 7)
    assert c.bildirim.bildir(BildirimKategori.HATIRLATMA, "Hey", "görev var") is True
    assert len(gelen) == 1
