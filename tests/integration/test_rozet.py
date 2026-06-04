"""Rozet servisi: tamamlama sayacı artar; değerlendir yeni kazanılanları kaydeder
(tekrar etmez); raf doğru kazanıldı/kilitli durumunu verir."""

from datetime import datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.rozetler.rozetler import RozetDurumu
from leveltodo.domain.tasks.kurallar import Tekrar
from leveltodo.infrastructure.saat import SahteSaat


def test_tamamlama_sayaci_ve_ilk_adim(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    assert c.rozet.tamamlama() == 0

    c.gorevler.gorev_olustur("İş", Tekrar.YOK)
    c.gorevler.tamamla(c.gorevler.bugunku_gorevler()[0].kayit_id)
    assert c.rozet.tamamlama() == 1

    durum = RozetDurumu(
        tamamlama=c.rozet.tamamlama(),
        en_iyi_giris_serisi=0,
        profil_seviye=0,
        kritik_yasandi=False,
        combo_yasandi=False,
    )
    yeni = c.rozet.degerlendir(durum)
    assert "ilk_adim" in {r.id for r in yeni}
    # ikinci kez değerlendir → ilk_adim tekrar verilmez
    assert "ilk_adim" not in {r.id for r in c.rozet.degerlendir(durum)}

    raf = {r.id: kazanildi for r, kazanildi in c.rozet.tum_rozetler()}
    assert raf["ilk_adim"] is True
    assert raf["caliskan"] is False
