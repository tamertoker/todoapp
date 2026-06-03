from leveltodo.domain.tasks.kurallar import Odul, odul_hesapla


def test_ozel_deger_her_seyi_ezer():
    assert odul_hesapla(calisilan_saniye=9999, ozel_deger=20) == Odul(xp=20, puan=20)


def test_sureye_gore_dakikada_bir():
    assert odul_hesapla(calisilan_saniye=120, ozel_deger=None) == Odul(xp=2, puan=2)


def test_kisa_sure_yine_de_en_az_bir_verir():
    # 20 saniye yuvarlanınca 0 eder ama en az 1 verilir.
    assert odul_hesapla(calisilan_saniye=20, ozel_deger=None).xp == 1


def test_suresiz_tamamlama_sabit_varsayilan_verir():
    assert odul_hesapla(calisilan_saniye=0, ozel_deger=None) == Odul(xp=5, puan=5)
