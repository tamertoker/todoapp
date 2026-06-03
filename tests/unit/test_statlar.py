from leveltodo.domain.stats.statlar import Stat, seviye_hesapla, unvan_hesapla


def test_sifir_xp_seviye_sifir():
    d = seviye_hesapla(0)
    assert d.seviye == 0
    assert d.bu_seviyedeki_xp == 0
    assert d.sonraki_seviye_esigi == round(8.4 * 60)  # 504


def test_ilk_seviye_esiginde_seviye_atlar():
    d = seviye_hesapla(504)  # tam eşik
    assert d.seviye == 1
    assert d.bu_seviyedeki_xp == 0


def test_esik_alti_seviye_atlamaz():
    d = seviye_hesapla(503)
    assert d.seviye == 0
    assert d.bu_seviyedeki_xp == 503


def test_unvan_baslangic_cirak():
    u = unvan_hesapla(0)
    assert u.unvan == "Çırak"
    assert u.sonraki_unvan == "Yolcu"
    assert u.sonraki_unvana_kalan == 4  # 3 + 1 - 0


def test_unvan_bantlari():
    assert unvan_hesapla(3).unvan == "Çırak"
    assert unvan_hesapla(4).unvan == "Yolcu"
    assert unvan_hesapla(9).unvan == "Cevher"
    assert unvan_hesapla(17).unvan == "Makine"
    assert unvan_hesapla(27).unvan == "Usta"
    assert unvan_hesapla(62).unvan == "Aydın"
    assert unvan_hesapla(90).unvan == "Efsane"


def test_efsane_sonrasi_unvan_yok():
    u = unvan_hesapla(90)
    assert u.sonraki_unvan is None
    assert u.sonraki_unvana_kalan is None


def test_dort_stat_var():
    assert len(list(Stat)) == 4
