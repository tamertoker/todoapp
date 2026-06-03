"""Dashboard'un ViewModel'i.

Ekran ile görev servisi arasındaki aracı. Görev ekleme/bitirme/silme
isteklerini servise iletir ve "veri değişti" sinyali yayar; ekran bu sinyali
duyup listeyi yeniden çizer.
"""

from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal

from leveltodo.application.gorev_servisi import GorevSatiri, GorevServisi
from leveltodo.domain.tasks.kurallar import Tekrar


class DashboardViewModel(QObject):
    changed = pyqtSignal()

    def __init__(self, gorevler: GorevServisi) -> None:
        super().__init__()
        self._gorevler = gorevler

    def satirlar(self) -> list[GorevSatiri]:
        return self._gorevler.bugunku_gorevler()

    def toplamlar(self) -> tuple[int, int]:
        return self._gorevler.toplamlar()

    def gorev_ekle(self, baslik: str, tekrar: Tekrar, ozel_odul: int | None) -> None:
        self._gorevler.gorev_olustur(baslik, tekrar, ozel_odul)
        self.changed.emit()

    def tamamla(self, kayit_id: str) -> None:
        self._gorevler.tamamla(kayit_id)
        self.changed.emit()

    def sil(self, kayit_id: str) -> None:
        self._gorevler.gorev_sil(kayit_id)
        self.changed.emit()
