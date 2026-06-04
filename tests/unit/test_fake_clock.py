from datetime import datetime

from leveltodo.infrastructure.saat import AyarlanabilirSaat, SahteSaat


def test_sahte_saat_verilen_zamani_dondurur():
    saat = SahteSaat(datetime(2026, 6, 2, 9, 0))
    assert saat.simdi() == datetime(2026, 6, 2, 9, 0)


def test_sahte_saat_ilerler():
    saat = SahteSaat(datetime(2026, 6, 2, 9, 0))
    saat.ilerlet(days=1, hours=2)
    assert saat.simdi() == datetime(2026, 6, 3, 11, 0)


def test_sahte_saat_ayarla():
    saat = SahteSaat(datetime(2026, 6, 2, 9, 0))
    saat.ayarla(datetime(2026, 12, 31, 23, 59))
    assert saat.simdi() == datetime(2026, 12, 31, 23, 59)


def test_ayarlanabilir_saat_kaydirma_ve_sifirla():
    saat = AyarlanabilirSaat()
    bugun = saat.simdi().date()
    saat.gun_kaydir(2)
    assert (saat.simdi().date() - bugun).days == 2
    assert saat.ofset_gun() == 2
    saat.sifirla()
    assert saat.simdi().date() == bugun
    assert saat.ofset_gun() == 0
