"""Görev → stat → seviye → profil/unvan zincirinin uçtan uca testi."""

from datetime import datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.stats.statlar import Stat
from leveltodo.domain.tasks.kurallar import Tekrar
from leveltodo.infrastructure.saat import SahteSaat


def _svc(db_url):
    return build_container(db_url=db_url, saat=SahteSaat(datetime(2026, 6, 3, 10, 0))).gorevler


def test_gorev_stata_xp_yazar_ve_seviye_olusur(db_url):
    svc = _svc(db_url)
    # Özel ödül 600 (kronometresiz hızlı test): Entelektüellik'e 600 XP → seviye 1.
    svc.gorev_olustur("Kitap oku", Tekrar.YOK, ozel_odul=600, stat=Stat.ENTELEKTUELLIK)
    svc.tamamla(svc.bugunku_gorevler()[0].kayit_id)

    durumlar = svc.stat_durumlari()
    assert durumlar[Stat.ENTELEKTUELLIK].seviye == 1  # 600 >= 504
    assert durumlar[Stat.BEDEN].seviye == 0

    profil, unvan = svc.profil_durumu()
    assert profil == 1  # 1 + 0 + 0 + 0
    assert unvan.unvan == "Çırak"
    assert unvan.sonraki_unvan == "Yolcu"
    assert unvan.sonraki_unvana_kalan == 3  # 3 + 1 - 1


def test_statsiz_gorev_stata_yazmaz_ama_genel_xp_artar(db_url):
    svc = _svc(db_url)
    svc.gorev_olustur("Genel iş", Tekrar.YOK, ozel_odul=600)  # stat seçilmedi
    svc.tamamla(svc.bugunku_gorevler()[0].kayit_id)

    profil, _ = svc.profil_durumu()
    assert profil == 0  # hiçbir stata yazılmadı
    assert svc.toplamlar()[0] == 600  # genel XP yine birikti
