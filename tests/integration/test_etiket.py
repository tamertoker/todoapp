"""Etiket (proje): ekle + göreve bağla; görev satırında etiket adı+rengi görünür."""

from datetime import datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.etiket.etiket import renk_sec
from leveltodo.domain.tasks.kurallar import Tekrar
from leveltodo.infrastructure.saat import SahteSaat


def test_renk_palet_dongusel():
    assert renk_sec(0) == renk_sec(10)  # palet 10 renk → döngü
    assert renk_sec(0) != renk_sec(1)


def test_etiket_ekle_ve_goreve_bagla(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    tid = c.etiket.etiket_ekle("İlişki Mühendisi")
    assert tid is not None
    assert any(t.name == "İlişki Mühendisi" for t in c.etiket.etiketler())

    c.gorevler.gorev_olustur("Logo düzenle", Tekrar.YOK, tag_id=tid)
    satir = c.gorevler.bugunku_gorevler()[0]
    assert satir.etiket_ad == "İlişki Mühendisi"
    assert satir.etiket_renk  # bir renk atandı

    c.gorevler.gorev_olustur("Etiketsiz iş", Tekrar.YOK)
    satirlar = {s.baslik: s for s in c.gorevler.bugunku_gorevler()}
    assert satirlar["Etiketsiz iş"].etiket_ad is None


def test_etiket_sil(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    tid = c.etiket.etiket_ekle("Geçici")
    c.etiket.etiket_sil(tid)
    assert c.etiket.etiketler() == []
