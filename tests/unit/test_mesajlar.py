from leveltodo.presentation.mesajlar import combo_mesaji, kritik_mesaji, tamamlama_mesaji


def test_tamamlama_mesaji_xp_icerir():
    assert "5" in tamamlama_mesaji(5)


def test_kritik_mesaji_degerleri_icerir():
    mesaj = kritik_mesaji(20, 20)
    assert "20" in mesaj and "KRİTİK" in mesaj


def test_combo_mesaji_dolu():
    assert combo_mesaji().strip() != ""
