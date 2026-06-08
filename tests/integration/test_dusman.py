"""Düşman: can eğrisi, biriken hasar → vur, tier yenileme, hazine; görev tamamlama
biriken hasara eklenir (anında inmez)."""

from datetime import datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.dusman.dusman import (
    DUSMANLAR,
    KADEME,
    boyut_carpani,
    dusman_getir,
    gunluk_iyilesme,
    hasar,
    max_hp,
)
from leveltodo.domain.tasks.kurallar import Tekrar
from leveltodo.infrastructure.saat import SahteSaat


def test_max_hp_tier_ile_dogrusal_artar():
    assert max_hp(0) == 100
    assert max_hp(1) == 135  # round(100 * 1.35)
    assert max_hp(2) == 170  # round(100 * 1.70)


def test_hasar_katsayisi_ve_gunluk_iyilesme():
    assert hasar(50) == 50  # katsayı 1.0
    assert gunluk_iyilesme(100) == 3  # %3


def test_dusman_3_tier_ayni_karakter_sonra_doner():
    # İlk karakter 3 tier (0-1-2) boyunca aynı; sadece boyutu büyür.
    assert dusman_getir(0).anahtar == "erteleyici"
    assert dusman_getir(2).anahtar == "erteleyici"
    assert dusman_getir(KADEME).anahtar == "dagilan_golge"  # 4. tier → sıradaki
    # Dört karakter döngüsü bitince başa döner.
    assert dusman_getir(KADEME * len(DUSMANLAR)).anahtar == DUSMANLAR[0].anahtar


def test_boyut_kademe_icinde_artar():
    assert boyut_carpani(0) < boyut_carpani(1) < boyut_carpani(2)
    assert boyut_carpani(KADEME) == boyut_carpani(0)  # yeni karakter, baştan


def test_biriken_hasar_vurunca_iner(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    _, hp, maks, tier = c.dusman.durum()
    assert (tier, hp, maks) == (0, 100, 100)

    c.dusman.hasar_biriktir(30)
    assert c.dusman.biriken_hasar() == 30
    assert c.dusman.durum()[1] == 100  # vurmadan can değişmez

    sonuc = c.dusman.vur()
    assert sonuc.verilen_hasar == 30
    assert sonuc.devrilen == 0
    assert c.dusman.durum()[1] == 70
    assert c.dusman.biriken_hasar() == 0


def test_vurus_dusmani_devirir_ve_hazine_birakir(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.dusman.hasar_biriktir(120)  # 100 can → devrilir, 20 taşar
    sonuc = c.dusman.vur()
    assert sonuc.devrilen == 1
    assert sonuc.konusma  # son söz söyler

    dusman2, hp2, maks2, tier2 = c.dusman.durum()
    assert tier2 == 1
    assert maks2 == 135  # yeni tier'ın canı
    assert hp2 == 135 - 20  # taşan 20 hasar yeni düşmana iner
    assert dusman2.anahtar == "erteleyici"  # 0-1-2 hâlâ aynı karakter

    assert c.dusman.bekleyen_hazine_sayisi() == 1
    odul = c.dusman.hazine_ac()
    assert odul is not None
    assert odul.tur in ("puan", "xp", "combo")
    assert odul.miktar > 0
    assert c.dusman.bekleyen_hazine_sayisi() == 0
    assert c.dusman.hazine_ac() is None


def test_dusman_hasarsiz_gunlerde_iyilesir(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.dusman.hasar_biriktir(30)
    c.dusman.vur()  # 100 - 30 = 70
    assert c.dusman.durum()[1] == 70

    saat.ilerlet(days=2)  # 2 hasarsız gün → 2 × round(100*0.03)=3 = 6 iyileşme
    assert c.dusman.durum()[1] == 76

    saat.ilerlet(days=100)  # uzun tembellik → maks cana kadar, taşmaz
    assert c.dusman.durum()[1] == 100


def test_gorev_tamamlama_biriken_hasara_eklenir(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.gorevler.gorev_olustur("İş", Tekrar.YOK, ozel_odul=20)
    satir = c.gorevler.bugunku_gorevler()[0]
    c.gorevler.tamamla(satir.kayit_id)  # 20 XP → 20 biriken hasar (anında inmez)
    assert c.dusman.durum()[1] == 100  # düşman canı değişmedi
    assert c.dusman.biriken_hasar() == 20

    c.dusman.vur()
    assert c.dusman.durum()[1] == 80  # 100 - 20
