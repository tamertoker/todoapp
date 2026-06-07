"""Özel stat: ekle → görev statı olur, profil seviyesine katılır, istatistik
dağılımında görünür, silinebilir."""

from datetime import datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.stats.statlar import _seviye_esigi
from leveltodo.domain.tasks.kurallar import Tekrar
from leveltodo.infrastructure.saat import SahteSaat


def test_ozel_stat_eklenir_ve_gorev_stati_olur(db_url):
    c = build_container(db_url=db_url, saat=SahteSaat(datetime(2026, 6, 1, 10, 0)))
    sid = c.stat.stat_ekle("Yazılım")
    assert sid is not None
    assert any(b.anahtar == sid and b.etiket == "Yazılım" for b in c.stat.tum_statlar())
    assert any(b.anahtar == sid for b in c.stat.gorev_statlari())
    # göreve atanabilir (str anahtar)
    c.gorevler.gorev_olustur("Kod yaz", Tekrar.YOK, stat=sid)


def test_ozel_stat_profile_katilir_ve_istatistikte(db_url):
    c = build_container(db_url=db_url, saat=SahteSaat(datetime(2026, 6, 1, 10, 0)))
    sid = c.stat.stat_ekle("Yazılım")
    p0 = c.gorevler.profil_durumu()[0]
    c.gorevler.gelistirme_xp_ekle(sid, _seviye_esigi(1))  # özel stat Sv 0→1
    assert c.gorevler.profil_durumu()[0] == p0 + 1  # profile katkı
    assert "Yazılım" in c.istatistik.stat_dagilimi()
    assert c.istatistik.stat_dagilimi()["Yazılım"] == _seviye_esigi(1)


def test_ozel_stat_silinir(db_url):
    c = build_container(db_url=db_url, saat=SahteSaat(datetime(2026, 6, 1, 10, 0)))
    sid = c.stat.stat_ekle("Geçici")
    c.stat.stat_sil(sid)
    assert not any(b.anahtar == sid for b in c.stat.tum_statlar())
