"""Gün sonu günlüğü: dönüşümlü soru, artan ödül eğrisi, kaydet+ödül (gün başına
tek), boşaltınca geri alma, doğru gün, geçmiş listesi, kendi soruları."""

from datetime import date, datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.gunluk.gunluk import HAVUZ, gunluk_odulu, gunun_sorusu
from leveltodo.domain.stats.statlar import Stat
from leveltodo.infrastructure.saat import SahteSaat


# — Saf kurallar —
def test_gunun_sorusu_donusumlu_ve_deterministik():
    sorular = ["A", "B", "C"]
    g = date(2026, 6, 1)
    assert gunun_sorusu(sorular, g) == sorular[g.toordinal() % 3]
    # Ardışık günler farklı soru verir (havuz > 1 olduğunda).
    assert gunun_sorusu(sorular, date(2026, 6, 1)) != gunun_sorusu(sorular, date(2026, 6, 2))
    # Aynı gün hep aynı soruyu verir.
    assert gunun_sorusu(sorular, g) == gunun_sorusu(sorular, g)
    assert gunun_sorusu([], g) is None


def test_gunluk_odulu_artar():
    assert gunluk_odulu(0) == 40
    assert gunluk_odulu(1) == 41
    assert gunluk_odulu(5) == 45


def _farkindalik_xp(c) -> int:
    return c.gorevler.stat_durumlari()[Stat.FARKINDALIK].bu_seviyedeki_xp


def test_kaydet_odul_gun_basina_tek_ve_dogru_stat(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)

    assert c.gunluk.kaydet("Bugün iyiydi.") is True
    assert _farkindalik_xp(c) == 40
    # Aynı gün tekrar kaydetmek ikinci ödül vermez.
    assert c.gunluk.kaydet("Bugün iyiydi. (düzeltme)") is False
    assert _farkindalik_xp(c) == 40
    assert c.gunluk.bugunku_gunluk().odul_verildi is True


def test_bosaltinca_odul_geri_alinir(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.gunluk.kaydet("dolu")
    assert _farkindalik_xp(c) == 40
    assert c.gunluk.kaydet("   ") is False  # boşaltıldı → geri alınır
    assert _farkindalik_xp(c) == 0
    assert c.gunluk.bugunku_gunluk().odul_verildi is False
    # Tekrar doldurunca aynı ödül geri gelir (gün ödülü sabitlenmişti).
    assert c.gunluk.kaydet("yine dolu") is True
    assert _farkindalik_xp(c) == 40


def test_odul_her_dolu_gunle_bir_tik_artar(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.gunluk.kaydet("ilk gün")  # +40
    saat.ilerlet(days=1)
    c.gunluk.kaydet("ikinci gün")  # +41
    assert _farkindalik_xp(c) == 81  # 40 + 41


def test_dogru_mantiksal_gune_yazilir_ve_gecmis(db_url):
    # Gün başlangıcı 04:00; 02:00 hâlâ önceki güne sayılır.
    saat = SahteSaat(datetime(2026, 6, 2, 2, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.gunluk.kaydet("gece yazısı")
    gecmis = c.gunluk.gecmis()
    assert len(gecmis) == 1
    assert gecmis[0].gun == "2026-06-01"
    assert gecmis[0].metin == "gece yazısı"


def test_kendi_sorusu_havuza_katilir(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.gunluk.soru_ekle("Kendi sorum?")
    sorular = c.gunluk.kullanici_sorulari()
    assert len(sorular) == 1 and sorular[0].text == "Kendi sorum?"

    c.gunluk.soru_sil(sorular[0].id)
    assert c.gunluk.kullanici_sorulari() == []
    # Havuz değişmeden duruyor.
    assert len(HAVUZ) >= 1
