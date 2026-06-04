"""Seri dondurma: jeton varsa boşlukta seri korunur, yoksa sıfırlanır;
her 7 günlük giriş serisinde +1 jeton kazanılır."""

from datetime import datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.stats.statlar import Stat
from leveltodo.domain.tasks.kurallar import Tekrar
from leveltodo.infrastructure.saat import SahteSaat


def test_dondurma_seriyi_korur(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.gorevler.gorev_olustur("Her gün", Tekrar.GUNLUK)

    def seri():
        return c.gorevler.bugunku_gorevler()[0].seri

    c.gorevler.tamamla(c.gorevler.bugunku_gorevler()[0].kayit_id)  # seri 1
    c.dondurma.ekle(1)
    assert c.dondurma.stok() == 1

    saat.ilerlet(days=2)  # araya boşluk (1 gün kaçtı)
    c.gorevler.tamamla(c.gorevler.bugunku_gorevler()[0].kayit_id)
    assert seri() == 2            # dondurma sayesinde korundu
    assert c.dondurma.stok() == 0  # jeton harcandı


def test_dondurma_yoksa_seri_sifirlanir(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    c.gorevler.gorev_olustur("Her gün", Tekrar.GUNLUK)
    c.gorevler.tamamla(c.gorevler.bugunku_gorevler()[0].kayit_id)  # seri 1

    saat.ilerlet(days=2)  # boşluk, jeton yok
    c.gorevler.tamamla(c.gorevler.bugunku_gorevler()[0].kayit_id)
    assert c.gorevler.bugunku_gorevler()[0].seri == 1  # sıfırlandı


def test_3_levelde_bir_dondurma_verir(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    # Bir statı profil seviye 3'e çıkar (eşik 504+528+552 = 1584 XP).
    c.gorevler.gelistirme_xp_ekle(Stat.ENTELEKTUELLIK, 1584)
    assert c.gorevler.profil_durumu()[0] == 3
    assert c.dondurma.stok() == 1  # 3 levelde bir → +1


def test_giris_serisi_7de_dondurma_verir(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    for _ in range(7):
        c.seri.giris_kaydet()
        saat.ilerlet(days=1)
    assert c.dondurma.stok() == 1  # 7. günde +1
