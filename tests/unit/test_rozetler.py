from leveltodo.domain.rozetler.rozetler import ROZETLER, RozetDurumu, kosul_saglandi_mi


def _durum(**kw) -> RozetDurumu:
    base = dict(
        tamamlama=0,
        en_iyi_giris_serisi=0,
        profil_seviye=0,
        kritik_yasandi=False,
        combo_yasandi=False,
    )
    base.update(kw)
    return RozetDurumu(**base)


def test_ilk_adim_bir_tamamlamayla():
    assert kosul_saglandi_mi("ilk_adim", _durum(tamamlama=1))
    assert not kosul_saglandi_mi("ilk_adim", _durum(tamamlama=0))


def test_caliskan_10_gorev():
    assert kosul_saglandi_mi("caliskan", _durum(tamamlama=10))
    assert not kosul_saglandi_mi("caliskan", _durum(tamamlama=9))


def test_alev_giris_serisi_7():
    assert kosul_saglandi_mi("alev", _durum(en_iyi_giris_serisi=7))
    assert not kosul_saglandi_mi("alev", _durum(en_iyi_giris_serisi=6))


def test_cevher_profil_9():
    assert kosul_saglandi_mi("cevher", _durum(profil_seviye=9))
    assert not kosul_saglandi_mi("cevher", _durum(profil_seviye=8))


def test_sansli_ve_combocu():
    assert kosul_saglandi_mi("sansli", _durum(kritik_yasandi=True))
    assert kosul_saglandi_mi("combocu", _durum(combo_yasandi=True))


def test_dokuz_rozet_var():
    assert len(ROZETLER) == 9
