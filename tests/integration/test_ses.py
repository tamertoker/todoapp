"""Ses: tamamlama ses seçimi (saf) + seviye/düşman olaylarının yayınlanması
(ses motoru bu olaylara bağlanır)."""

from datetime import datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.events import DusmanDevrildi, SeviyeAtlandi
from leveltodo.domain.stats.statlar import Stat, _seviye_esigi
from leveltodo.infrastructure.saat import SahteSaat
from leveltodo.infrastructure.sound.secim import tamamlama_sesi


def test_tamamlama_sesi_secimi():
    assert tamamlama_sesi(kritik=True, combo_tetik=False) == "kritik"
    assert tamamlama_sesi(kritik=False, combo_tetik=True) == "combo"
    assert tamamlama_sesi(kritik=False, combo_tetik=False) == "tamamla"
    assert tamamlama_sesi(kritik=True, combo_tetik=True) == "kritik"  # kritik önce


def test_seviye_atlayinca_olay_yayinlanir(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    olaylar = []
    c.olay_hatti.subscribe(SeviyeAtlandi, olaylar.append)

    c.gorevler.gelistirme_xp_ekle(Stat.BEDEN, _seviye_esigi(1))  # profil 0 → 1
    assert len(olaylar) == 1
    assert olaylar[0].yeni_seviye == 1


def test_dusman_devrilince_olay_yayinlanir(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    olaylar = []
    c.olay_hatti.subscribe(DusmanDevrildi, olaylar.append)

    c.dusman.hasar_biriktir(100)  # biriktir
    c.dusman.vur()  # 100 can → 0 → devrildi (tier 0)
    assert len(olaylar) == 1
    assert olaylar[0].tier == 0
