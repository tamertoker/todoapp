from datetime import date

from leveltodo.domain.tasks.kurallar import Tekrar, gunde_olusur_mu

OLUSTURMA = date(2026, 6, 1)


def test_gunluk_her_gun_olusur():
    assert gunde_olusur_mu(Tekrar.GUNLUK, "", OLUSTURMA, date(2026, 6, 5)) is True


def test_olusturmadan_once_olusmaz():
    assert gunde_olusur_mu(Tekrar.GUNLUK, "", date(2026, 6, 10), date(2026, 6, 5)) is False


def test_her_x_gun():
    assert gunde_olusur_mu(Tekrar.HER_X_GUN, "3", OLUSTURMA, date(2026, 6, 1)) is True   # gün 0
    assert gunde_olusur_mu(Tekrar.HER_X_GUN, "3", OLUSTURMA, date(2026, 6, 4)) is True   # gün 3
    assert gunde_olusur_mu(Tekrar.HER_X_GUN, "3", OLUSTURMA, date(2026, 6, 5)) is False  # gün 4


def test_haftalik_secili_gun():
    hedef = date(2026, 6, 3)
    param = str(hedef.weekday())  # tam olarak o günün haftagünü seçili
    assert gunde_olusur_mu(Tekrar.HAFTALIK, param, OLUSTURMA, hedef) is True
    baska = date(2026, 6, 4)
    beklenen = baska.weekday() == hedef.weekday()
    assert gunde_olusur_mu(Tekrar.HAFTALIK, param, OLUSTURMA, baska) is beklenen


def test_haftalik_coklu_gun():
    # Pazartesi(0), Çarşamba(2), Cuma(4)
    param = "0,2,4"
    assert gunde_olusur_mu(Tekrar.HAFTALIK, param, OLUSTURMA, date(2026, 6, 1)) is (
        date(2026, 6, 1).weekday() in {0, 2, 4}
    )


def test_aylik():
    assert gunde_olusur_mu(Tekrar.AYLIK, "15", OLUSTURMA, date(2026, 6, 15)) is True
    assert gunde_olusur_mu(Tekrar.AYLIK, "15", OLUSTURMA, date(2026, 7, 15)) is True
    assert gunde_olusur_mu(Tekrar.AYLIK, "15", OLUSTURMA, date(2026, 6, 16)) is False
