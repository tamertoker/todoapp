"""Pano: etiket başına çalışma süresi dağılımı (büyükten küçüğe, etiketsiz dahil)."""

from datetime import datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.tasks.kurallar import Tekrar
from leveltodo.infrastructure.saat import SahteSaat


def test_etiket_sure_dagilimi(db_url):
    c = build_container(db_url=db_url, saat=SahteSaat(datetime(2026, 6, 10, 12, 0)))
    tid = c.etiket.etiket_ekle("İslam")
    c.gorevler.gorev_olustur("Dua", Tekrar.YOK, tag_id=tid)
    s = c.gorevler.bugunku_gorevler()[0]
    c.gorevler.tamamla(s.kayit_id, elle_dakika=30)  # 1800 sn

    c.gorevler.gorev_olustur("Etiketsiz iş", Tekrar.YOK)
    s2 = next(x for x in c.gorevler.bugunku_gorevler() if x.baslik == "Etiketsiz iş")
    c.gorevler.tamamla(s2.kayit_id, elle_dakika=10)  # 600 sn

    bas, bit = c.istatistik.gun_araligi("ay")
    dagilim = c.istatistik.etiket_sure_dagilimi(bas, bit)
    sure = {ad: sn for ad, _renk, sn in dagilim}
    assert sure["İslam"] == 1800
    assert sure["(Etiketsiz)"] == 600
    assert dagilim[0][0] == "İslam"  # en uzun süre başta
