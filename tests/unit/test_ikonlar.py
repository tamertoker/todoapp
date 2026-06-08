"""Streak (giriş serisi) kademe eşikleri — kullanıcının verdiği sınırlara uyum testi.

Alt sınırlar: 5, 21, 40, 80, 150 gün. (1-4 gün = kademe 1; 0 gün = seri yok.)
"""

from leveltodo.presentation.common.ikonlar import seri_kademe, seri_sonraki_esik


def test_seri_kademe_esikler():
    assert seri_kademe(0) == 0  # seri yok
    assert seri_kademe(1) == 1
    assert seri_kademe(4) == 1
    assert seri_kademe(5) == 2
    assert seri_kademe(20) == 2
    assert seri_kademe(21) == 3
    assert seri_kademe(39) == 3
    assert seri_kademe(40) == 4
    assert seri_kademe(79) == 4
    assert seri_kademe(80) == 5
    assert seri_kademe(149) == 5
    assert seri_kademe(150) == 6
    assert seri_kademe(1000) == 6


def test_seri_sonraki_esik():
    assert seri_sonraki_esik(0) == 5
    assert seri_sonraki_esik(4) == 5
    assert seri_sonraki_esik(5) == 21
    assert seri_sonraki_esik(21) == 40
    assert seri_sonraki_esik(40) == 80
    assert seri_sonraki_esik(80) == 150
    assert seri_sonraki_esik(150) is None  # en üst kademe
    assert seri_sonraki_esik(500) is None
