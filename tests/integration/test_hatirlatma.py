"""Görev hatırlatma: hedef saat gelince HATIRLATMA bildirimi (gün başına tek);
görev bugün geçerli değilse hatırlatmaz."""

from datetime import datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.bildirim.bildirim import BildirimKategori
from leveltodo.domain.tasks.kurallar import Tekrar
from leveltodo.infrastructure.saat import SahteSaat


def test_hatirlatma_saat_gelince_gun_basina_tek(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 8, 0))
    c = build_container(db_url=db_url, saat=saat)
    gelen = []
    c.bildirim.kanal_ekle(gelen.append)
    c.gorevler.gorev_olustur("İlaç al", Tekrar.GUNLUK, reminder="09:00")

    c.hatirlatma.kontrol()
    assert gelen == []  # 08:00 < 09:00 → henüz yok

    saat.ayarla(datetime(2026, 6, 1, 9, 30))
    c.hatirlatma.kontrol()
    hatirlatmalar = [b for b in gelen if b.kategori is BildirimKategori.HATIRLATMA]
    assert len(hatirlatmalar) == 1 and "İlaç al" in hatirlatmalar[0].govde

    c.hatirlatma.kontrol()  # aynı gün ikinci kez → tekrar yok
    assert len([b for b in gelen if b.kategori is BildirimKategori.HATIRLATMA]) == 1


def test_hatirlatma_bugun_gecerli_degilse_yok(db_url):
    # Pazartesi (2026-06-01) ama görev yalnız Salı (1) günü → bugün hatırlatmaz.
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    gelen = []
    c.bildirim.kanal_ekle(gelen.append)
    c.gorevler.gorev_olustur("Spor", Tekrar.HAFTALIK, parametre="1", reminder="09:00")
    c.hatirlatma.kontrol()
    assert gelen == []
