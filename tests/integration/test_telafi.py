"""Telafi (catchup): kaçırılan tekrarlı oluşumlar bekleyen kayıt olarak listelenir;
geç yapılınca (tamamla) ödül verilir, listeden çıkar ve seriyi etkilemez."""

from datetime import date, datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.tasks.kurallar import Tekrar
from leveltodo.infrastructure.saat import SahteSaat


def _svc(db_url, saat):
    return build_container(db_url=db_url, saat=saat).gorevler


def test_telafi_gorevleri_kacirilanlari_gosterir(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    svc = _svc(db_url, saat)
    svc.gorev_olustur("Her gün", Tekrar.GUNLUK)

    saat.ilerlet(days=3)  # bugün 4 Haziran; 1, 2, 3 kaçtı
    satirlar = svc.telafi_gorevleri()
    assert {s.gun for s in satirlar} == {date(2026, 6, 1), date(2026, 6, 2), date(2026, 6, 3)}
    assert all(s.durum == "pending" for s in satirlar)  # kronometreyle yapılabilir


def test_telafi_tamamla_odul_listeden_cikar_seri_etkilenmez(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    svc = _svc(db_url, saat)
    svc.gorev_olustur("Her gün", Tekrar.GUNLUK, ozel_odul=10)

    saat.ilerlet(days=2)  # bugün 3 Haziran; 1, 2 kaçtı
    satirlar = svc.telafi_gorevleri()
    assert len(satirlar) == 2

    hedef = satirlar[0]  # en yeni kaçırılan (2 Haziran)
    odul = svc.tamamla(hedef.kayit_id)
    assert odul is not None and odul.xp == 20  # özel ödül 10 × telafi 2x
    assert svc.toplamlar()[0] == 20

    kalan = {s.gun for s in svc.telafi_gorevleri()}
    assert hedef.gun not in kalan and len(kalan) == 1

    # Telafi geçmiş günü tamamladı; bugünkü seri etkilenmemeli.
    assert svc.bugunku_gorevler()[0].seri == 0


def test_telafi_2x_bugun_1x(db_url):
    """Geçmiş gün telafisi 2x ödül; aynı görevin bugünkü tamamlanması 1x."""
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    svc = _svc(db_url, saat)
    svc.gorev_olustur("Her gün", Tekrar.GUNLUK, ozel_odul=10)

    saat.ilerlet(days=1)  # bugün 2 Haziran; 1 Haziran kaçtı
    telafi = svc.telafi_gorevleri()[0]  # 1 Haziran (geçmiş)
    assert svc.tamamla(telafi.kayit_id).xp == 20  # 10 × 2

    bugunku = svc.bugunku_gorevler()[0]  # 2 Haziran (bugün)
    assert svc.tamamla(bugunku.kayit_id).xp == 10  # 1x
