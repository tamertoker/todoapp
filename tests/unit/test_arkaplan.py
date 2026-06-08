"""Saate göre arkaplan zaman dilimi seçimi (5 dilim) — sınır kontrolleri."""

from leveltodo.presentation.common.arkaplan import zaman_dilimi


def test_zaman_dilimleri():
    assert zaman_dilimi(7) == "sabah"
    assert zaman_dilimi(12) == "ogle"
    assert zaman_dilimi(16) == "ikindi"
    assert zaman_dilimi(20) == "aksam"
    assert zaman_dilimi(23) == "gece"
    assert zaman_dilimi(2) == "gece"


def test_zaman_dilimi_sinirlari():
    assert zaman_dilimi(5) == "gece"  # sabahtan hemen önce
    assert zaman_dilimi(6) == "sabah"
    assert zaman_dilimi(11) == "ogle"
    assert zaman_dilimi(15) == "ikindi"
    assert zaman_dilimi(19) == "aksam"
