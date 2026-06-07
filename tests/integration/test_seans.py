"""Seanslar: başlat→durdur seans kaydeder + süreye göre ödül; aynı başlık altında
birikir; kısa seans ödülsüz; başka görev başlayınca önceki seans kapanır."""

from datetime import datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.stats.statlar import Stat
from leveltodo.domain.tasks.kurallar import Tekrar
from leveltodo.infrastructure.saat import SahteSaat


def test_seans_baslat_durdur_odul_ve_birikme(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.gorevler.gorev_olustur("Kitap oku", Tekrar.GUNLUK, stat=Stat.ENTELEKTUELLIK)
    s = c.gorevler.bugunku_gorevler()[0]

    c.gorevler.seans_baslat(s.kayit_id)
    saat.ilerlet(minutes=30)
    odul = c.gorevler.seans_durdur(s.kayit_id)
    assert odul is not None and odul.xp == 30  # süre-temelli (30 dk)

    seanslar = c.gorevler.seanslar(s.kayit_id)
    assert len(seanslar) == 1
    assert seanslar[0].baslangic == "10:00" and seanslar[0].bitis == "10:30"
    assert seanslar[0].sure == 1800

    # İkinci seans aynı başlık altına eklenir
    c.gorevler.seans_baslat(s.kayit_id)
    saat.ilerlet(minutes=15)
    c.gorevler.seans_durdur(s.kayit_id)
    assert len(c.gorevler.seanslar(s.kayit_id)) == 2

    # Toplam süre = 45 dk; XP de 45 (Entelektüellik)
    s2 = c.gorevler.bugunku_gorevler()[0]
    assert s2.calisilan_saniye == 45 * 60
    assert c.gorevler.stat_durumlari()[Stat.ENTELEKTUELLIK].bu_seviyedeki_xp == 45


def test_kisa_seans_odulsuz_ama_kaydedilir(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.gorevler.gorev_olustur("Hızlı", Tekrar.YOK)
    s = c.gorevler.bugunku_gorevler()[0]
    c.gorevler.seans_baslat(s.kayit_id)
    saat.ilerlet(seconds=30)  # < 1 dk
    assert c.gorevler.seans_durdur(s.kayit_id) is None
    assert c.gorevler.seanslar(s.kayit_id)[0].sure == 30
    assert c.gorevler.toplamlar()[0] == 0  # ödül yok


def test_seans_silinince_gorev_suresi_eksilir(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.gorevler.gorev_olustur("Oku", Tekrar.YOK)
    s = c.gorevler.bugunku_gorevler()[0]
    for _ in range(2):
        c.gorevler.seans_baslat(s.kayit_id)
        saat.ilerlet(minutes=30)
        c.gorevler.seans_durdur(s.kayit_id)
    assert c.gorevler.bugunku_gorevler()[0].calisilan_saniye == 3600  # 1 saat

    ilk = c.gorevler.seanslar(s.kayit_id)[0]
    c.gorevler.seans_sil(ilk.seans_id)  # 30 dk sil
    assert c.gorevler.bugunku_gorevler()[0].calisilan_saniye == 1800  # 30 dk kaldı
    assert len(c.gorevler.seanslar(s.kayit_id)) == 1


def test_seans_saati_duzenlenebilir(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.gorevler.gorev_olustur("Oku", Tekrar.YOK)
    s = c.gorevler.bugunku_gorevler()[0]
    c.gorevler.seans_baslat(s.kayit_id)
    saat.ilerlet(minutes=30)
    c.gorevler.seans_durdur(s.kayit_id)

    se = c.gorevler.seanslar(s.kayit_id)[0]
    assert c.gorevler.seans_guncelle(se.seans_id, "12:00", "12:45") is True
    g = c.gorevler.seanslar(s.kayit_id)[0]
    assert g.baslangic == "12:00" and g.bitis == "12:45" and g.sure == 45 * 60
    assert c.gorevler.bugunku_gorevler()[0].calisilan_saniye == 45 * 60  # toplam güncellendi
    assert c.gorevler.seans_guncelle(se.seans_id, "12:00", "11:00") is False  # geçersiz


def test_manuel_seans_ekle(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.gorevler.gorev_olustur("Oku", Tekrar.YOK)
    s = c.gorevler.bugunku_gorevler()[0]
    assert c.gorevler.seans_manuel_ekle(s.kayit_id, "12:00", "12:30") is True
    assert len(c.gorevler.seanslar(s.kayit_id)) == 1
    assert c.gorevler.bugunku_gorevler()[0].calisilan_saniye == 1800


def test_baska_gorev_baslayinca_onceki_seans_kapanir(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.gorevler.gorev_olustur("A", Tekrar.YOK)
    c.gorevler.gorev_olustur("B", Tekrar.YOK)
    rows = {r.baslik: r for r in c.gorevler.bugunku_gorevler()}

    c.gorevler.seans_baslat(rows["A"].kayit_id)
    saat.ilerlet(minutes=10)
    c.gorevler.seans_baslat(rows["B"].kayit_id)  # A'yı kapatıp ödüllendirir

    a_seans = c.gorevler.seanslar(rows["A"].kayit_id)
    assert len(a_seans) == 1 and a_seans[0].sure == 600
    assert c.gorevler.toplamlar()[0] == 10  # A 10 dk ödül
