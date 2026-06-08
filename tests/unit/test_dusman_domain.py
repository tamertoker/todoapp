"""Düşman saf mantığı: tier→karakter/boyut eşlemesi, can eğrisi, hazine ödülü."""

from leveltodo.domain.dusman.dusman import (
    DUSMANLAR,
    KADEME,
    ODUL_TURLERI,
    boyut_carpani,
    dusman_getir,
    hazine_odulu,
    max_hp,
)


def test_tier_3_kademe_ayni_karakter():
    for t in range(KADEME):
        assert dusman_getir(t).anahtar == DUSMANLAR[0].anahtar
    assert dusman_getir(KADEME).anahtar == DUSMANLAR[1].anahtar


def test_dort_karakter_dongusu_basa_doner():
    assert dusman_getir(KADEME * len(DUSMANLAR)).anahtar == DUSMANLAR[0].anahtar


def test_boyut_kademe_icinde_artar_sonra_sifirlanir():
    assert boyut_carpani(0) < boyut_carpani(1) < boyut_carpani(2)
    assert boyut_carpani(KADEME) == boyut_carpani(0)


def test_max_hp_dogrusal_ve_artan():
    assert max_hp(0) == 100
    assert max_hp(5) > max_hp(2) > max_hp(0)


def test_hazine_odulu_tur_secimi():
    assert hazine_odulu(0, 0.0, 0.5).tur == ODUL_TURLERI[0]  # puan
    assert hazine_odulu(0, 0.4, 0.5).tur == "xp"
    assert hazine_odulu(0, 0.99, 0.5).tur == "combo"


def test_hazine_odulu_tier_ile_comertlesir():
    dusuk = hazine_odulu(0, 0.0, 0.5).miktar  # tier 0 puan
    yuksek = hazine_odulu(8, 0.0, 0.5).miktar  # tier 8 puan
    assert yuksek > dusuk


def test_hazine_odulu_miktar_pozitif_ve_mesajli():
    for secim in (0.0, 0.5, 0.99):
        odul = hazine_odulu(3, secim, 0.5)
        assert odul.miktar > 0
        assert odul.mesaj
