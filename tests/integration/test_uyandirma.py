"""Uyandırma disiplini: zamanında kalkış Disiplin'e XP (gün başına tek), geç
kalışta ceza yok, hedef toleransı."""

from datetime import datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.stats.statlar import Stat
from leveltodo.domain.uyandirma.uyandirma import dakikaya, uyanma_basarili_mi
from leveltodo.infrastructure.saat import SahteSaat


def test_uyanma_kurallari():
    assert dakikaya("07:30") == 450
    assert dakikaya("bozuk") == 0
    assert uyanma_basarili_mi(420, 420) is True  # tam hedef
    assert uyanma_basarili_mi(420, 300) is True  # erken
    assert uyanma_basarili_mi(420, 435) is True  # +15 tolerans sınırı
    assert uyanma_basarili_mi(420, 436) is False  # tolerans dışı


def _disiplin_xp(c) -> int:
    return c.gorevler.stat_durumlari()[Stat.DISIPLIN].bu_seviyedeki_xp


def test_zamaninda_kalkis_disipline_xp_gun_basina_tek(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 6, 50))  # hedef 07:00, erken
    c = build_container(db_url=db_url, saat=saat)
    assert c.uyandirma.kalktim() is True
    assert _disiplin_xp(c) == 50
    # Aynı gün tekrar → ek ödül yok
    assert c.uyandirma.kalktim() is True
    assert _disiplin_xp(c) == 50
    assert c.uyandirma.bugun_kaydi().gercek == "06:50"


def test_gec_kalkis_odul_yok_ceza_yok(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 9, 30))  # hedef 07:00, geç
    c = build_container(db_url=db_url, saat=saat)
    assert c.uyandirma.kalktim() is False
    assert _disiplin_xp(c) == 0  # ödül yok
    assert c.gorevler.toplamlar()[0] == 0  # ceza da yok (XP eksiye düşmedi)
    assert c.uyandirma.bugun_kaydi().basarili is False


def test_hedef_degistirilince_kalici(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 8, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.uyandirma.hedef_ayarla("08:30")
    assert c.uyandirma.hedef == "08:30"
    assert c.uyandirma.kalktim() is True  # 08:00 <= 08:30 → başarılı
    assert _disiplin_xp(c) == 50
