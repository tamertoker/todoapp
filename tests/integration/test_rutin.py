"""Rutin alanları: tanım/sil, günlük değer (üzerine yazma + doğru gün), hedef
tutunca gün-başına-tek ödül ve geri alınmama."""

from datetime import date, datetime

from sqlalchemy import func, select

from leveltodo.bootstrap import build_container
from leveltodo.domain.rutinler.rutinler import RutinTuru, Yon, hedef_tuttu_mu
from leveltodo.domain.stats.statlar import Stat
from leveltodo.infrastructure.persistence.sqlite.models import RoutineEntry
from leveltodo.infrastructure.saat import SahteSaat


# — Saf kural —
def test_hedef_tuttu_mu_kurallari():
    assert hedef_tuttu_mu(RutinTuru.SAYI, 8, Yon.EN_AZ, 8) is True
    assert hedef_tuttu_mu(RutinTuru.SAYI, 7, Yon.EN_AZ, 8) is False
    assert hedef_tuttu_mu(RutinTuru.SAYI, 0, Yon.EN_FAZLA, 1) is True
    assert hedef_tuttu_mu(RutinTuru.SAYI, 2, Yon.EN_FAZLA, 1) is False
    assert hedef_tuttu_mu(RutinTuru.EVET_HAYIR, 1) is True
    assert hedef_tuttu_mu(RutinTuru.EVET_HAYIR, 0) is False


def _beden_xp(c) -> int:
    return c.gorevler.stat_durumlari()[Stat.BEDEN].bu_seviyedeki_xp


def test_alan_ekle_ve_pasife_al_kayitlari_korur(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.rutin.alan_ekle("su", RutinTuru.SAYI, Stat.BEDEN, 30, yon=Yon.EN_AZ, hedef=8)
    alanlar = c.rutin.bugunku_alanlar()
    assert len(alanlar) == 1 and alanlar[0].ad == "su"

    field_id = alanlar[0].field_id
    c.rutin.deger_gir(field_id, 8)  # hedef tuttu → 30 XP
    assert _beden_xp(c) == 30

    c.rutin.alan_sil(field_id)
    assert c.rutin.bugunku_alanlar() == []  # listeden kalktı
    assert _beden_xp(c) == 30  # ama kazanılan XP duruyor


def test_deger_uzerine_yazilir_ikinci_satir_olusmaz(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.rutin.alan_ekle("sayfa", RutinTuru.SAYI, Stat.ENTELEKTUELLIK, 20, yon=Yon.EN_AZ, hedef=10)
    field_id = c.rutin.bugunku_alanlar()[0].field_id

    c.rutin.deger_gir(field_id, 5)
    c.rutin.deger_gir(field_id, 12)
    assert c.rutin.bugunku_alanlar()[0].bugun_deger == 12

    with c.session_factory() as s:
        adet = s.scalar(select(func.count()).select_from(RoutineEntry))
    assert adet == 1


def test_hedef_odulu_gun_basina_bir_kez_ve_dusunce_geri_alinir(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.rutin.alan_ekle("su", RutinTuru.SAYI, Stat.BEDEN, 30, yon=Yon.EN_AZ, hedef=8)
    field_id = c.rutin.bugunku_alanlar()[0].field_id

    assert c.rutin.deger_gir(field_id, 5) is False  # hedefin altı → ödül yok
    assert _beden_xp(c) == 0
    assert c.rutin.deger_gir(field_id, 9) is True  # hedef tuttu → ödül
    assert _beden_xp(c) == 30
    assert c.rutin.deger_gir(field_id, 12) is False  # tekrar tuttu ama gün başına tek
    assert _beden_xp(c) == 30
    assert c.rutin.deger_gir(field_id, 2) is False  # hedefin altına düştü → ödül geri alınır
    assert _beden_xp(c) == 0
    assert c.rutin.bugunku_alanlar()[0].odul_verildi is False
    assert c.rutin.deger_gir(field_id, 8) is True  # tekrar tuttu → yeniden ödül
    assert _beden_xp(c) == 30


def test_evet_hayir_isaretleyince_odul(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.rutin.alan_ekle("spor", RutinTuru.EVET_HAYIR, Stat.BEDEN, 40)
    field_id = c.rutin.bugunku_alanlar()[0].field_id

    assert c.rutin.deger_gir(field_id, 0) is False
    assert _beden_xp(c) == 0
    assert c.rutin.deger_gir(field_id, 1) is True
    assert _beden_xp(c) == 40
    assert c.rutin.deger_gir(field_id, 0) is False  # işaret kalktı → ödül geri alınır
    assert _beden_xp(c) == 0


def test_metin_alani_not_saklar_odul_vermez(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.rutin.alan_ekle("ruh hali", RutinTuru.METIN)
    alan = c.rutin.bugunku_alanlar()[0]
    assert alan.tur is RutinTuru.METIN and alan.odul_xp == 0

    c.rutin.metin_gir(alan.field_id, "bugün iyiyim")
    g = c.rutin.bugunku_alanlar()[0]
    assert g.bugun_metin == "bugün iyiyim"
    assert c.gorevler.toplamlar()[0] == 0  # metin alanı XP vermez

    c.rutin.metin_gir(alan.field_id, "düzeltme")  # üzerine yazılır
    assert c.rutin.bugunku_alanlar()[0].bugun_metin == "düzeltme"


def test_deger_dogru_mantiksal_gune_yazilir(db_url):
    # Gün başlangıcı varsayılan 04:00; 02:00 hâlâ önceki güne sayılır.
    saat = SahteSaat(datetime(2026, 6, 2, 2, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.rutin.alan_ekle("su", RutinTuru.SAYI, Stat.BEDEN, 30, yon=Yon.EN_AZ, hedef=8)
    field_id = c.rutin.bugunku_alanlar()[0].field_id
    c.rutin.deger_gir(field_id, 8)

    with c.session_factory() as s:
        kayit = s.scalar(select(RoutineEntry))
    assert kayit.day == date(2026, 6, 1)
