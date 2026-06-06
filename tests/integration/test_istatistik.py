"""İstatistik: günlük seri (XP/çalışma/tamamlama/rutin), metrik seçenekleri,
stat dağılımı, kişisel rekorlar."""

from datetime import date, datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.rutinler.rutinler import RutinTuru, Yon
from leveltodo.domain.stats.statlar import Stat
from leveltodo.domain.tasks.kurallar import Tekrar
from leveltodo.infrastructure.saat import SahteSaat


def test_gunluk_seri_xp_calisma_tamamlama(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.gorevler.gorev_olustur("İş", Tekrar.YOK, ozel_odul=20)
    satir = c.gorevler.bugunku_gorevler()[0]
    c.gorevler.tamamla(satir.kayit_id, elle_dakika=30)

    bas, bit = c.istatistik.gun_araligi("hafta")
    assert c.istatistik.gunluk_seri("xp", bas, bit).get(date(2026, 6, 1)) == 20
    assert c.istatistik.gunluk_seri("calisma", bas, bit).get(date(2026, 6, 1)) == 30  # dk
    assert c.istatistik.gunluk_seri("tamamlama", bas, bit).get(date(2026, 6, 1)) == 1


def test_rutin_metrik_secenek_ve_seri(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.rutin.alan_ekle("su", RutinTuru.SAYI, Stat.BEDEN, 30, yon=Yon.EN_AZ, hedef=8)
    fid = c.rutin.bugunku_alanlar()[0].field_id
    c.rutin.deger_gir(fid, 7)

    secenekler = c.istatistik.metrik_secenekleri()
    assert any(m.anahtar == f"rutin:{fid}" and m.etiket == "su" for m in secenekler)

    bas, bit = c.istatistik.gun_araligi("hafta")
    seri = c.istatistik.gunluk_seri(f"rutin:{fid}", bas, bit)
    assert seri.get(date(2026, 6, 1)) == 7


def test_stat_dagilimi(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.gorevler.gelistirme_xp_ekle(Stat.BEDEN, 120)
    dagilim = c.istatistik.stat_dagilimi()
    assert dagilim["Beden"] == 120
    assert dagilim["Disiplin"] == 0


def test_rekorlar(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.gorevler.gorev_olustur("İş", Tekrar.YOK, ozel_odul=50)
    satir = c.gorevler.bugunku_gorevler()[0]
    c.gorevler.tamamla(satir.kayit_id, elle_dakika=40)

    r = c.istatistik.rekorlar()
    assert r.en_uretken_gun == (date(2026, 6, 1), 50)
    assert r.en_uzun_kronometre_sn == 40 * 60
    assert r.en_cok_gorev_gun == (date(2026, 6, 1), 1)
    assert r.en_uzun_seri >= 0
