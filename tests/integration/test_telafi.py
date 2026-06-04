"""Telafi (catchup): kaçırılan tekrarlı oluşumlar listelenir ve geç yapılınca
ödül verilip listeden çıkar."""

from datetime import date, datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.tasks.kurallar import Tekrar
from leveltodo.infrastructure.saat import SahteSaat


def _svc(db_url, saat):
    return build_container(db_url=db_url, saat=saat).gorevler


def test_telafi_listesi_kacirilanlari_gosterir(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    svc = _svc(db_url, saat)
    svc.gorev_olustur("Her gün", Tekrar.GUNLUK)

    saat.ilerlet(days=3)  # hiç tamamlamadan 3 gün ilerle → bugün 4 Haziran
    gunler = {t.gun for t in svc.telafi_listesi()}
    assert gunler == {date(2026, 6, 1), date(2026, 6, 2), date(2026, 6, 3)}


def test_telafi_yap_odul_verir_ve_listeden_cikar(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    svc = _svc(db_url, saat)
    svc.gorev_olustur("Her gün", Tekrar.GUNLUK, ozel_odul=10)

    saat.ilerlet(days=2)  # bugün 3 Haziran; 1 ve 2 Haziran kaçtı
    telafiler = svc.telafi_listesi()
    assert len(telafiler) == 2

    hedef = telafiler[0]  # en yeni kaçırılan
    odul = svc.telafi_yap(hedef.task_id, hedef.gun)
    assert odul is not None and odul.xp == 10  # özel ödül
    assert svc.toplamlar()[0] == 10

    kalan = {t.gun for t in svc.telafi_listesi()}
    assert hedef.gun not in kalan
    assert len(kalan) == 1
