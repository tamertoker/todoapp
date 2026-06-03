from datetime import datetime

from leveltodo.infrastructure.saat import SahteSaat


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
