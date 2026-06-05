"""Veri yedekleme/geri yükleme: SQLite kopyası + JSON dışa aktarma + açılışta
geri yükleme uygulanması + geçersiz dosya reddi."""

import json
from datetime import datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.tasks.kurallar import Tekrar
from leveltodo.infrastructure.backup.yedekleme import Yedekleyici, db_dosya_yolu
from leveltodo.infrastructure.saat import SahteSaat


def test_sqlite_yedek_ve_json_disa_aktarma(db_url, tmp_path):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.gorevler.gorev_olustur("Oku", Tekrar.YOK)

    yedek = c.yedekleyici.sqlite_yedek_al(str(tmp_path / "yedek.db"))
    assert yedek.is_file()

    js = c.yedekleyici.json_disa_aktar(str(tmp_path / "yedek.json"))
    veri = json.loads(js.read_text(encoding="utf-8"))
    assert "tasks" in veri and len(veri["tasks"]) == 1
    assert veri["tasks"][0]["title"] == "Oku"


def test_gecersiz_yedek_reddedilir(db_url, tmp_path):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    sahte = tmp_path / "sahte.db"
    sahte.write_text("bu bir veritabanı değil", encoding="utf-8")
    try:
        c.yedekleyici.geri_yukle_isaretle(str(sahte))
        raise AssertionError("geçersiz dosya kabul edilmemeliydi")
    except ValueError:
        pass


def test_geri_yukleme_acilista_uygulanir(db_url, tmp_path):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.gorevler.gorev_olustur("Eski", Tekrar.YOK)
    yedek = str(c.yedekleyici.sqlite_yedek_al(str(tmp_path / "y.db")))

    # Yedekten sonra veri değişir (yeni görev).
    c.gorevler.gorev_olustur("Yeni", Tekrar.YOK)
    assert len(c.gorevler.bugunku_gorevler()) == 2

    # Geri yüklemeyi işaretle; motoru kapat (yeniden başlatma benzetimi); uygula.
    c.yedekleyici.geri_yukle_isaretle(yedek)
    c.engine.dispose()
    assert Yedekleyici.bekleyen_geri_yukleme_uygula(db_dosya_yolu(db_url)) is True

    # Yeniden aç → yedek anındaki tek görev geri gelir.
    c2 = build_container(db_url=db_url, saat=saat)
    basliklar = [g.baslik for g in c2.gorevler.bugunku_gorevler()]
    assert basliklar == ["Eski"]
