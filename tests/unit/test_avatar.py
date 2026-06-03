from leveltodo.infrastructure.assets.avatar import ai_avatar_yolu, avatar_katmanlari


def test_avatar_katmanlari_sac_icerir():
    katmanlar = avatar_katmanlari(0)
    assert len(katmanlar) == 3
    assert any("4har" in k for k in katmanlar)


def test_ai_avatar_yolu_yoksa_none(tmp_path):
    assert ai_avatar_yolu(tmp_path, "Çırak") is None


def test_ai_avatar_yolu_varsa_dondurur(tmp_path):
    dizin = tmp_path / "avatar_ai"
    dizin.mkdir()
    (dizin / "cirak.png").write_bytes(b"x")
    assert ai_avatar_yolu(tmp_path, "Çırak") is not None


def test_ai_avatar_bilinmeyen_unvan_none(tmp_path):
    assert ai_avatar_yolu(tmp_path, "Bilinmeyen") is None
