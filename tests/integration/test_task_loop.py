"""Çekirdek döngünün uçtan uca testi (kronometresiz):
ekle → listele → bitir → ödül → toplamlar → günlük tekrar → kalıcılık."""

from datetime import datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.tasks.kurallar import Tekrar
from leveltodo.infrastructure.saat import SahteSaat


def _gorevler(db_url, saat):
    return build_container(db_url=db_url, saat=saat).gorevler


def test_tam_dongu(db_url):
    saat = SahteSaat(datetime(2026, 6, 3, 10, 0))
    svc = _gorevler(db_url, saat)

    svc.gorev_olustur("Kitap oku", Tekrar.GUNLUK)
    svc.gorev_olustur("Faturayı öde", Tekrar.YOK, ozel_odul=20)

    satirlar = svc.bugunku_gorevler()
    assert len(satirlar) == 2

    tek = next(s for s in satirlar if s.tekrar == "none")
    odul = svc.tamamla(tek.kayit_id)
    assert odul is not None and odul.xp == 20 and odul.puan == 20
    assert svc.toplamlar() == (20, 20)

    # Tek seferlik görev bitince listeden düşer.
    basliklar = [s.baslik for s in svc.bugunku_gorevler()]
    assert "Faturayı öde" not in basliklar

    # Her-gün görevi hâlâ bekliyor; bitir (kronometresiz → sabit 5).
    gunluk = next(s for s in svc.bugunku_gorevler() if s.tekrar == "daily")
    assert svc.tamamla(gunluk.kayit_id).xp == 5
    assert svc.toplamlar() == (25, 25)

    # Ertesi mantıksal günde her-gün görevi yeniden bekliyor olarak gelir.
    saat.ilerlet(days=1)
    yarin = svc.bugunku_gorevler()
    assert any(s.tekrar == "daily" and s.durum == "pending" for s in yarin)
    assert svc.toplamlar() == (25, 25)


def test_iki_kez_tamamlamak_cift_odul_vermez(db_url):
    saat = SahteSaat(datetime(2026, 6, 3, 10, 0))
    svc = _gorevler(db_url, saat)

    svc.gorev_olustur("Tek iş", Tekrar.YOK)
    satir = svc.bugunku_gorevler()[0]

    assert svc.tamamla(satir.kayit_id) is not None
    assert svc.tamamla(satir.kayit_id) is None  # ikinci kez ödül yok
    assert svc.toplamlar() == (5, 5)


def test_biten_gorevi_silmek_listeden_cikarir(db_url):
    saat = SahteSaat(datetime(2026, 6, 3, 10, 0))
    svc = _gorevler(db_url, saat)
    svc.gorev_olustur("Her gün koş", Tekrar.GUNLUK)
    satir = svc.bugunku_gorevler()[0]

    svc.tamamla(satir.kayit_id)
    # Biten her-gün görevi bugün hâlâ listede (✓ ile).
    assert any(s.kayit_id == satir.kayit_id for s in svc.bugunku_gorevler())

    svc.gorev_sil(satir.kayit_id)
    # Silinince listeden çıkar.
    assert all(s.kayit_id != satir.kayit_id for s in svc.bugunku_gorevler())


def test_veri_yeniden_baslatmada_kalir(db_url):
    saat = SahteSaat(datetime(2026, 6, 3, 10, 0))
    svc = _gorevler(db_url, saat)
    svc.gorev_olustur("Kalıcı görev", Tekrar.GUNLUK)
    svc.tamamla(svc.bugunku_gorevler()[0].kayit_id)

    # Aynı veritabanıyla yeni container (uygulamayı kapatıp açmak gibi).
    svc2 = _gorevler(db_url, saat)
    assert svc2.toplamlar() == (5, 5)
