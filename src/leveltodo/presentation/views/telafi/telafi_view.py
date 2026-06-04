"""Telafi (catchup) menüsü.

Kaçırdığın tekrarlı görevleri (son 3 hafta) geç de olsa yapmak için ayrı ekran.
Satırlar ana ekrandaki gibi kronometrelidir (Başlat/Duraklat/Bitir): istersen
süre tutarak yaparsın. Bitirince o günün ödülü yazılır ve listeden düşer.
"""

from __future__ import annotations

from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import QFrame, QLabel, QScrollArea, QVBoxLayout, QWidget

from leveltodo.application.gorev_servisi import GorevSatiri
from leveltodo.bootstrap import Container
from leveltodo.presentation.views.dashboard.bitir_dialog import BitirDialog
from leveltodo.presentation.views.dashboard.gorev_satir_widget import (
    format_sure,
    kronometreli_satir,
    satir_canli_saniye,
)


class TelafiView(QWidget):
    degisti = pyqtSignal()

    def __init__(self, container: Container) -> None:
        super().__init__()
        self._container = container
        self._sure_etiketleri: dict[str, tuple[QLabel, GorevSatiri]] = {}

        title = QLabel("Telafi")
        title.setObjectName("Title")
        bilgi = QLabel("Kaçırdığın tekrarlı görevleri geç de olsa yap, ödülünü al.")
        bilgi.setObjectName("Subtitle")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        liste_container = QWidget()
        self._liste_layout = QVBoxLayout(liste_container)
        self._liste_layout.setContentsMargins(0, 0, 0, 0)
        self._liste_layout.setSpacing(8)
        scroll.setWidget(liste_container)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(bilgi)
        layout.addWidget(scroll, stretch=1)

        self._tick_timer = QTimer(self)
        self._tick_timer.timeout.connect(self._tick)
        self._tick_timer.start(1000)

        self.yenile()

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.yenile()  # ekrana her gelişte güncel telafi listesi

    def yenile(self) -> None:
        self._sure_etiketleri = {}
        while self._liste_layout.count():
            item = self._liste_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

        satirlar = self._container.gorevler.telafi_gorevleri()
        if not satirlar:
            bos = QLabel("Telafi edilecek bir şey yok. Temiz!")
            bos.setObjectName("Subtitle")
            self._liste_layout.addWidget(bos)
        else:
            for satir in satirlar:
                frame = kronometreli_satir(
                    satir,
                    simdi=self._container.saat.simdi(),
                    sure_etiketleri=self._sure_etiketleri,
                    baslat=self._baslat,
                    duraklat=self._duraklat,
                    bitir=self._bitir,
                    sil=None,
                    etiket_metni=f"Kaçırıldı: {satir.gun}",
                )
                self._liste_layout.addWidget(frame)
        self._liste_layout.addStretch(1)

    def _tick(self) -> None:
        simdi = self._container.saat.simdi()
        for _kayit_id, (etiket, satir) in self._sure_etiketleri.items():
            if satir.calisiyor:
                etiket.setText(format_sure(satir_canli_saniye(satir, simdi)))

    def _baslat(self, kayit_id: str) -> None:
        self._container.kronometre.baslat(kayit_id)
        self.yenile()

    def _duraklat(self, kayit_id: str) -> None:
        self._container.kronometre.duraklat(kayit_id)
        self.yenile()

    def _bitir(self, satir: GorevSatiri) -> None:
        on_dakika = round(satir_canli_saniye(satir, self._container.saat.simdi()) / 60)
        dialog = BitirDialog(on_dakika, self)
        if dialog.exec():
            self._container.gorevler.tamamla(satir.kayit_id, dialog.dakika())
            self.yenile()
            self.degisti.emit()
