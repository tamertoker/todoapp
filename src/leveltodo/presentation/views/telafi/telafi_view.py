"""Telafi (catchup) menüsü.

Kaçırdığın tekrarlı görevleri (son 3 hafta) geç de olsa yapıp ödülünü almak
için ayrı bir ekran. "Ceza yok, telafi var." Bir telafi yapınca o günün ödülü
yazılır; ekran kendini tazeler ve ana ekrana haber verir.
"""

from __future__ import annotations

from datetime import date

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from leveltodo.bootstrap import Container


class TelafiView(QWidget):
    degisti = pyqtSignal()

    def __init__(self, container: Container) -> None:
        super().__init__()
        self._container = container

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

        self.yenile()

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.yenile()  # ekrana her gelişte güncel telafi listesi

    def yenile(self) -> None:
        while self._liste_layout.count():
            item = self._liste_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

        telafiler = self._container.gorevler.telafi_listesi()
        if not telafiler:
            bos = QLabel("Telafi edilecek bir şey yok. Temiz!")
            bos.setObjectName("Subtitle")
            self._liste_layout.addWidget(bos)
        else:
            for telafi in telafiler:
                self._liste_layout.addWidget(self._satir(telafi))
        self._liste_layout.addStretch(1)

    def _satir(self, telafi) -> QFrame:
        frame = QFrame()
        frame.setObjectName("TaskRow")
        h = QHBoxLayout(frame)
        h.setContentsMargins(12, 8, 12, 8)
        h.setSpacing(8)

        baslik = QLabel(telafi.baslik)
        gun = QLabel(f"Kaçırıldı: {telafi.gun}")
        gun.setObjectName("Tag")
        btn = QPushButton("Telafi Et")
        btn.clicked.connect(
            lambda _c, tid=telafi.task_id, g=telafi.gun: self._telafi_et(tid, g)
        )
        h.addWidget(baslik, stretch=1)
        h.addWidget(gun)
        h.addWidget(btn)
        return frame

    def _telafi_et(self, task_id: str, gun: date) -> None:
        self._container.gorevler.telafi_yap(task_id, gun)
        self.yenile()
        self.degisti.emit()
