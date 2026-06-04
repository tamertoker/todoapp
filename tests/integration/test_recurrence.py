"""Esnek tekrar: görevler doğru günlerde listede belirir (FakeClock ile)."""

from datetime import date, datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.tasks.kurallar import Tekrar
from leveltodo.infrastructure.saat import SahteSaat


def _svc(db_url, saat):
    return build_container(db_url=db_url, saat=saat).gorevler


def _var_mi(svc, baslik):
    return any(s.baslik == baslik for s in svc.bugunku_gorevler())


def test_her_x_gun_dogru_gunlerde(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    svc = _svc(db_url, saat)
    svc.gorev_olustur("Her 3 günde", Tekrar.HER_X_GUN, parametre="3")

    assert _var_mi(svc, "Her 3 günde")       # gün 0
    saat.ilerlet(days=1)
    assert not _var_mi(svc, "Her 3 günde")   # gün 1
    saat.ilerlet(days=2)
    assert _var_mi(svc, "Her 3 günde")       # gün 3


def test_haftalik_secili_gunlerde(db_url):
    baslangic = datetime(2026, 6, 1, 10, 0)
    saat = SahteSaat(baslangic)
    svc = _svc(db_url, saat)
    bugun_wd = baslangic.date().weekday()
    svc.gorev_olustur("Haftalık iş", Tekrar.HAFTALIK, parametre=str(bugun_wd))

    assert _var_mi(svc, "Haftalık iş")       # bugün (seçili gün)
    saat.ilerlet(days=1)
    assert not _var_mi(svc, "Haftalık iş")   # ertesi gün (farklı haftagünü)
    saat.ilerlet(days=6)
    assert _var_mi(svc, "Haftalık iş")       # +7 gün = aynı haftagünü


def test_tum_tekrarli_gorevler_ve_sonraki_tarih(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    svc = _svc(db_url, saat)
    svc.gorev_olustur("Her 3 günde", Tekrar.HER_X_GUN, parametre="3")
    svc.gorev_olustur("Ayın 15'i", Tekrar.AYLIK, parametre="15")
    svc.gorev_olustur("Tek seferlik", Tekrar.YOK)  # tekrarlı değil

    ozetler = svc.tum_tekrarli_gorevler()
    assert {o.baslik for o in ozetler} == {"Her 3 günde", "Ayın 15'i"}  # YOK listede değil
    aylik = next(o for o in ozetler if o.baslik == "Ayın 15'i")
    assert aylik.sonraki == date(2026, 6, 15)


def test_her_x_gun_gece_eklenince_bugun_gorunur(db_url):
    # Gün başlangıcı 4; saat 02:00 → mantıksal bugün önceki gün. Görev yine de bugün görünmeli.
    saat = SahteSaat(datetime(2026, 6, 4, 2, 0))
    svc = _svc(db_url, saat)
    svc.gorev_olustur("Gece her 2", Tekrar.HER_X_GUN, parametre="2")
    assert _var_mi(svc, "Gece her 2")


def test_aylik_belirli_gun(db_url):
    saat = SahteSaat(datetime(2026, 6, 14, 10, 0))
    svc = _svc(db_url, saat)
    svc.gorev_olustur("Ayın 15'i", Tekrar.AYLIK, parametre="15")

    assert not _var_mi(svc, "Ayın 15'i")     # 14'ü
    saat.ilerlet(days=1)
    assert _var_mi(svc, "Ayın 15'i")         # 15'i
