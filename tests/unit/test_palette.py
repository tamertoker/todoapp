from leveltodo.presentation.theme.palette import DARK, THEMES, get_palette


def test_all_themes_resolve_to_their_palette():
    for key, palette in THEMES.items():
        assert get_palette(key) is palette


def test_unknown_theme_falls_back_to_dark():
    assert get_palette("olmayan-tema") is DARK


def test_six_themes_available():
    assert set(THEMES) == {"dark", "light", "midnight", "forest", "sunset", "arcane"}
