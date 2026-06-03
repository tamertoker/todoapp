"""Ayarların gerçekten kalıcı olduğunu kanıtlar.

Bir container'da ayarı değiştirip, aynı veritabanıyla yeni bir container kurar
ve değerin korunduğunu doğrular. Bu, migration + depo + servis zincirinin
uçtan uca çalıştığını gösterir.
"""

from leveltodo.bootstrap import build_container


def test_setting_survives_new_container(db_url):
    c1 = build_container(db_url=db_url)
    assert c1.settings.theme == "dark"  # varsayılan

    c1.settings.set("theme", "light")
    c1.settings.set("day_start_hour", 6)

    c2 = build_container(db_url=db_url)
    assert c2.settings.theme == "light"
    assert c2.settings.day_start_hour == 6


def test_defaults_when_unset(db_url):
    c = build_container(db_url=db_url)
    assert c.settings.day_start_hour == 4
    assert c.settings.minimize_to_tray is True
