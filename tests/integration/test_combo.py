"""Combo: 15 dk içinde, her biri ≥10 dk 3 görev → 1 saat boyunca ×1.5 ödül."""

from datetime import datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.tasks.kurallar import Tekrar
from leveltodo.infrastructure.saat import SahteSaat


def _ekle_tamamla(c, baslik, dakika):
    c.gorevler.gorev_olustur(baslik, Tekrar.YOK, ozel_odul=10)
    satir = next(s for s in c.gorevler.bugunku_gorevler() if s.baslik == baslik)
    return c.gorevler.tamamla(satir.kayit_id, elle_dakika=dakika)


def test_combo_3_gorevle_tetiklenir_ve_carpan_uygular(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0, 0))
    c = build_container(db_url=db_url, saat=saat)  # kritik conftest'te kapalı

    assert _ekle_tamamla(c, "A", 10).xp == 10
    saat.ilerlet(minutes=1)
    assert _ekle_tamamla(c, "B", 10).xp == 10
    saat.ilerlet(minutes=1)
    assert _ekle_tamamla(c, "C", 10).xp == 10  # tetikleyen görev bonus almaz
    assert c.combo.aktif_mi(saat.simdi())

    saat.ilerlet(minutes=1)
    assert _ekle_tamamla(c, "D", 10).xp == 15  # combo aktif → 10 × 1.5


def test_kisa_gorevler_combo_tetiklemez(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0, 0))
    c = build_container(db_url=db_url, saat=saat)
    for ad in ("A", "B", "C"):
        _ekle_tamamla(c, ad, 5)  # 5 dk < 10 dk → saymaz
        saat.ilerlet(minutes=1)
    assert not c.combo.aktif_mi(saat.simdi())


def test_combo_15dk_disinda_tetiklenmez(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0, 0))
    c = build_container(db_url=db_url, saat=saat)
    _ekle_tamamla(c, "A", 10)
    saat.ilerlet(minutes=10)
    _ekle_tamamla(c, "B", 10)
    saat.ilerlet(minutes=10)  # A artık 20 dk önce → pencere dışı
    _ekle_tamamla(c, "C", 10)
    assert not c.combo.aktif_mi(saat.simdi())
