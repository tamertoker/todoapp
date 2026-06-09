"""Dashboard'un ViewModel'i.

Ekran ile servisler arasındaki aracı. Görev ve kronometre isteklerini ilgili
servise iletir ve "veri değişti" sinyali yayar; ekran bu sinyali duyup listeyi
yeniden çizer.
"""

from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal

from leveltodo.application.gorev_servisi import GorevSatiri, GorevServisi, TekrarliGorevOzeti
from leveltodo.application.kronometre_servisi import KronometreServisi
from leveltodo.domain.stats.statlar import SeviyeDurumu, Stat, UnvanDurumu
from leveltodo.domain.tasks.kurallar import Tekrar


class DashboardViewModel(QObject):
    changed = pyqtSignal()

    def __init__(self, gorevler: GorevServisi, kronometre: KronometreServisi) -> None:
        super().__init__()
        self._gorevler = gorevler
        self._kronometre = kronometre

    def satirlar(self) -> list[GorevSatiri]:
        return self._gorevler.bugunku_gorevler()

    def tum_tekrarli_gorevler(self) -> list[TekrarliGorevOzeti]:
        return self._gorevler.tum_tekrarli_gorevler()

    def toplamlar(self) -> tuple[int, int]:
        return self._gorevler.toplamlar()

    def gun_gorev_ilerleme(self) -> tuple[int, int]:
        return self._gorevler.gun_gorev_ilerleme()

    def tamamlanan_satirlar(self) -> list[GorevSatiri]:
        return self._gorevler.bugun_tamamlanan_gorevler()

    def gorev_ekle(
        self,
        baslik: str,
        tekrar: Tekrar,
        ozel_odul: int | None,
        stat: str | Stat | None = None,
        parametre: str = "",
        tag_id: str | None = None,
        reminder: str | None = None,
        hedef_sure: int | None = None,
    ) -> None:
        self._gorevler.gorev_olustur(
            baslik, tekrar, ozel_odul, stat, parametre, tag_id, reminder, hedef_sure
        )
        self.changed.emit()

    def stat_durumlari(self) -> dict[Stat, SeviyeDurumu]:
        return self._gorevler.stat_durumlari()

    def stat_durumlari_anahtar(self, anahtarlar: list[str]) -> dict[str, SeviyeDurumu]:
        return self._gorevler.stat_durumlari_anahtar(anahtarlar)

    def profil_durumu(self) -> tuple[int, UnvanDurumu]:
        return self._gorevler.profil_durumu()

    def tamamla(self, kayit_id: str, elle_dakika: int | None = None) -> None:
        self._gorevler.tamamla(kayit_id, elle_dakika)
        self.changed.emit()

    def sil(self, kayit_id: str) -> None:
        self._gorevler.gorev_sil(kayit_id)
        self.changed.emit()

    def sablon_sil(self, task_id: str) -> None:
        self._gorevler.sablon_sil(task_id)
        self.changed.emit()

    # — Seanslar (kronometre = ardışık seanslar) —
    def seans_baslat(self, kayit_id: str) -> None:
        self._gorevler.seans_baslat(kayit_id)
        self.changed.emit()

    def seans_durdur(self, kayit_id: str) -> None:
        self._gorevler.seans_durdur(kayit_id)
        self.changed.emit()

    def seanslar(self, kayit_id: str):
        return self._gorevler.seanslar(kayit_id)

    def seans_sil(self, seans_id: str) -> None:
        self._gorevler.seans_sil(seans_id)
        self.changed.emit()

    def seans_guncelle(self, seans_id: str, baslangic: str, bitis: str) -> None:
        self._gorevler.seans_guncelle(seans_id, baslangic, bitis)
        self.changed.emit()

    def seans_manuel_ekle(self, kayit_id: str, baslangic: str, bitis: str) -> None:
        self._gorevler.seans_manuel_ekle(kayit_id, baslangic, bitis)
        self.changed.emit()

    def checkpoint(self) -> None:
        self._kronometre.checkpoint()

    def kurtar(self) -> int:
        return self._kronometre.kurtar()
