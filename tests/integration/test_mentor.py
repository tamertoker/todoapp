"""Mentor servisi: ihmal edilen stat dürtmesi (gün başına tek), düşman kışkırtması
(şansla), telafi amnesti uyarısı + yükü affetme."""

from datetime import datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.bildirim.bildirim import BildirimKategori
from leveltodo.domain.stats.statlar import Stat
from leveltodo.domain.tasks.kurallar import Tekrar
from leveltodo.infrastructure.saat import SahteSaat


class _HepSans:
    def kritik_mi(self, olasilik: float) -> bool:
        return True


def test_mentor_ihmal_edilen_stati_durter_gun_basina_tek(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    gelen = []
    c.bildirim.kanal_ekle(gelen.append)

    c.gorevler.gorev_olustur("Spor", Tekrar.YOK, stat=Stat.BEDEN)
    c.gorevler.tamamla(c.gorevler.bugunku_gorevler()[0].kayit_id, 10)  # Beden bugün

    saat.ilerlet(days=3)  # 3 gündür Beden sessiz
    c.mentor.periyodik_kontrol()
    durtmeler = [b for b in gelen if b.kategori is BildirimKategori.DURTME and b.baslik == "Mentor"]
    assert len(durtmeler) == 1
    assert "Beden" in durtmeler[0].govde

    c.mentor.periyodik_kontrol()  # aynı gün ikinci kez → tekrar yok
    assert len([b for b in gelen if b.baslik == "Mentor"]) == 1


def test_dusman_kiskirtmasi_sansla_cikar(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat, sans=_HepSans())
    gelen = []
    c.bildirim.kanal_ekle(gelen.append)

    c.mentor.periyodik_kontrol()
    kiskirtmalar = [b for b in gelen if b.kategori is BildirimKategori.DURTME]
    assert len(kiskirtmalar) == 1  # stat aktivitesi yok → sadece düşman kışkırtması
    assert kiskirtmalar[0].baslik == c.dusman.durum()[0].ad


def test_amnesti_uyarisi_ve_yuku_affet(db_url):
    saat = SahteSaat(datetime(2026, 6, 1, 10, 0))
    c = build_container(db_url=db_url, saat=saat)
    gelen = []
    c.bildirim.kanal_ekle(gelen.append)

    c.gorevler.gorev_olustur("Her gün", Tekrar.GUNLUK)
    saat.ilerlet(days=12)  # 12 gün kaçtı (>= 10 eşiği)
    assert c.gorevler.telafi_sayisi() >= 10

    c.mentor.periyodik_kontrol()
    uyarilar = [b for b in gelen if b.kategori is BildirimKategori.UYARI]
    assert len(uyarilar) == 1

    affedilen = c.gorevler.telafi_amnesti_uygula()
    assert affedilen >= 10
    assert c.gorevler.telafi_sayisi() == 0
