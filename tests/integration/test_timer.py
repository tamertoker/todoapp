"""Kronometre: başlat/duraklat süre biriktirir, çalışırken bitirme süreyi sayar,
tek kronometre kuralı, ve checkpoint + çökme kurtarma."""

from datetime import datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.tasks.kurallar import Tekrar, canli_sure
from leveltodo.infrastructure.saat import SahteSaat


def test_canli_sure_durmusken_kayitli_sureyi_dondurur():
    assert canli_sure(100, None, datetime(2026, 6, 3, 10, 0)) == 100


def test_canli_sure_calisirken_segmenti_ekler():
    seg = datetime(2026, 6, 3, 10, 0, 0)
    simdi = datetime(2026, 6, 3, 10, 1, 30)  # 90 saniye sonra
    assert canli_sure(100, seg, simdi) == 190


def _container(db_url, saat):
    return build_container(db_url=db_url, saat=saat)


def test_baslat_duraklat_sure_biriktirir(db_url):
    saat = SahteSaat(datetime(2026, 6, 3, 10, 0, 0))
    c = _container(db_url, saat)
    c.gorevler.gorev_olustur("Çalış", Tekrar.YOK)
    satir = c.gorevler.bugunku_gorevler()[0]

    c.kronometre.baslat(satir.kayit_id)
    saat.ilerlet(seconds=130)
    c.kronometre.duraklat(satir.kayit_id)

    g = c.gorevler.bugunku_gorevler()[0]
    assert g.calisilan_saniye == 130
    assert g.calisiyor is False

    odul = c.gorevler.tamamla(satir.kayit_id)  # süreye-dayalı: round(130/60)=2
    assert odul is not None and odul.xp == 2
    assert c.gorevler.toplamlar() == (2, 2)


def test_calisirken_bitir_sureyi_sayar(db_url):
    saat = SahteSaat(datetime(2026, 6, 3, 10, 0, 0))
    c = _container(db_url, saat)
    c.gorevler.gorev_olustur("Çalış", Tekrar.YOK)
    satir = c.gorevler.bugunku_gorevler()[0]

    c.kronometre.baslat(satir.kayit_id)
    saat.ilerlet(seconds=120)
    odul = c.gorevler.tamamla(satir.kayit_id)  # durdurmadan bitir
    assert odul is not None and odul.xp == 2


def test_tek_kronometre_digerini_durdurur(db_url):
    saat = SahteSaat(datetime(2026, 6, 3, 10, 0, 0))
    c = _container(db_url, saat)
    c.gorevler.gorev_olustur("A", Tekrar.YOK)
    c.gorevler.gorev_olustur("B", Tekrar.YOK)
    satirlar = c.gorevler.bugunku_gorevler()
    a, b = satirlar[0], satirlar[1]

    c.kronometre.baslat(a.kayit_id)
    saat.ilerlet(seconds=60)
    c.kronometre.baslat(b.kayit_id)  # A durmalı, B çalışmalı

    durum = {s.kayit_id: s for s in c.gorevler.bugunku_gorevler()}
    assert durum[a.kayit_id].calisiyor is False
    assert durum[a.kayit_id].calisilan_saniye == 60
    assert durum[b.kayit_id].calisiyor is True


def test_checkpoint_sonrasi_kurtarma_kayitli_sureyi_korur(db_url):
    saat = SahteSaat(datetime(2026, 6, 3, 10, 0, 0))
    c = _container(db_url, saat)
    c.gorevler.gorev_olustur("Çalış", Tekrar.YOK)
    satir = c.gorevler.bugunku_gorevler()[0]

    c.kronometre.baslat(satir.kayit_id)
    saat.ilerlet(seconds=50)
    c.kronometre.checkpoint()   # 50 sn DB'ye yazıldı
    saat.ilerlet(seconds=100)   # bu 100 sn "çökmede" kaybolacak

    # Uygulamayı kapatıp açmak gibi: aynı veritabanıyla yeni container.
    c2 = _container(db_url, saat)
    assert c2.kronometre.kurtar() == 1

    g = c2.gorevler.bugunku_gorevler()[0]
    assert g.calisiyor is False
    assert g.calisilan_saniye == 50  # checkpoint'lenen korunur, askıdaki 100 sn atılır
