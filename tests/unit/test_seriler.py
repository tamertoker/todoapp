from datetime import date

from leveltodo.domain.streaks.seriler import seri_ilerlet, seri_rengi


def test_ilk_isaret_seri_bir():
    assert seri_ilerlet(0, 0, None, date(2026, 6, 1)) == (1, 1, date(2026, 6, 1))


def test_ardisik_gun_artar():
    assert seri_ilerlet(3, 5, date(2026, 6, 1), date(2026, 6, 2)) == (4, 5, date(2026, 6, 2))


def test_yeni_rekor():
    assert seri_ilerlet(5, 5, date(2026, 6, 1), date(2026, 6, 2)) == (6, 6, date(2026, 6, 2))


def test_ayni_gun_degismez():
    assert seri_ilerlet(4, 7, date(2026, 6, 2), date(2026, 6, 2)) == (4, 7, date(2026, 6, 2))


def test_bosluk_sifirlar():
    assert seri_ilerlet(9, 9, date(2026, 6, 1), date(2026, 6, 4)) == (1, 9, date(2026, 6, 4))


def test_renk_esikleri():
    assert seri_rengi(2) == seri_rengi(0)      # ikisi de soluk
    assert seri_rengi(3) != seri_rengi(2)      # 3'te renk değişir
    assert seri_rengi(30) == "#ffd24a"         # altın
