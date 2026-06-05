"""İrade ekranı.

İradeni zorlayan eylemleri (erken kalkmak, ertelediğini bitirmek, kendine
sözünü tutmak) buradan kaydedersin; her biri özel **Disiplin** statına XP yazar.
Altta son eylemlerin listesi görünür.
"""

from __future__ import annotations

from PyQt6.QtCore import QTime, pyqtSignal
from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from leveltodo.bootstrap import Container


class IradeView(QWidget):
    degisti = pyqtSignal()

    def __init__(self, container: Container) -> None:
        super().__init__()
        self._container = container

        title = QLabel("İrade")
        title.setObjectName("Title")
        bilgi = QLabel("İradeni zorlayan eylemleri kaydet — Disiplin'i bunlar büyütür.")
        bilgi.setObjectName("Subtitle")

        self._baslik = QLineEdit()
        self._baslik.setPlaceholderText("Ne yaptın? (ör. erken kalktım, ertelediğimi bitirdim)")
        self._baslik.returnPressed.connect(self._ekle)
        self._xp = QSpinBox()
        self._xp.setRange(1, 1000)
        self._xp.setValue(60)
        ekle_btn = QPushButton("Ekle (+Disiplin)")
        ekle_btn.clicked.connect(self._ekle)
        form = QHBoxLayout()
        form.addWidget(self._baslik, stretch=1)
        form.addWidget(QLabel("XP"))
        form.addWidget(self._xp)
        form.addWidget(ekle_btn)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        ic = QWidget()
        self._liste_layout = QVBoxLayout(ic)
        self._liste_layout.setContentsMargins(0, 0, 0, 0)
        self._liste_layout.setSpacing(8)
        scroll.setWidget(ic)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(bilgi)
        layout.addWidget(self._uyandirma_karti())
        layout.addLayout(form)
        layout.addWidget(QLabel("Son irade eylemlerin"))
        layout.addWidget(scroll, stretch=1)

        self.yenile()

    def _uyandirma_karti(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("TaskRow")
        h = QHBoxLayout(frame)
        h.setContentsMargins(12, 8, 12, 8)
        h.setSpacing(8)
        h.addWidget(QLabel("Uyandırma disiplini"))
        h.addWidget(QLabel("Hedef:"))
        self._hedef_edit = QTimeEdit()
        self._hedef_edit.setDisplayFormat("HH:mm")
        self._hedef_edit.setTime(self._saat_parse(self._container.uyandirma.hedef))
        self._hedef_edit.timeChanged.connect(self._hedef_kaydet)
        h.addWidget(self._hedef_edit)
        kalktim_btn = QPushButton("Kalktım")
        kalktim_btn.clicked.connect(self._kalktim)
        h.addWidget(kalktim_btn)
        self._uyanma_sonuc = QLabel()
        self._uyanma_sonuc.setObjectName("Tag")
        h.addWidget(self._uyanma_sonuc, stretch=1)
        return frame

    def _saat_parse(self, hhmm: str) -> QTime:
        try:
            saat, dakika = hhmm.split(":")
            return QTime(int(saat), int(dakika))
        except (ValueError, AttributeError):
            return QTime(7, 0)

    def _hedef_kaydet(self, t: QTime) -> None:
        self._container.uyandirma.hedef_ayarla(t.toString("HH:mm"))

    def _kalktim(self) -> None:
        self._container.uyandirma.kalktim()
        self._uyanma_yenile()
        self.degisti.emit()

    def _uyanma_yenile(self) -> None:
        kayit = self._container.uyandirma.bugun_kaydi()
        if kayit is None:
            self._uyanma_sonuc.setText("Bugün henüz kalkmadın.")
        elif kayit.basarili:
            self._uyanma_sonuc.setText(f"Bugün {kayit.gercek} — zamanında ✓ (+Disiplin)")
        else:
            self._uyanma_sonuc.setText(f"Bugün {kayit.gercek} — geç kalkıldı")

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.yenile()

    def yenile(self) -> None:
        self._uyanma_yenile()
        while self._liste_layout.count():
            item = self._liste_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

        eylemler = self._container.irade.son_eylemler()
        if not eylemler:
            bos = QLabel("Henüz irade eylemi yok. İlk adımı at.")
            bos.setObjectName("Subtitle")
            self._liste_layout.addWidget(bos)
        else:
            for eylem in eylemler:
                self._liste_layout.addWidget(self._satir(eylem))
        self._liste_layout.addStretch(1)

    def _satir(self, eylem) -> QFrame:
        frame = QFrame()
        frame.setObjectName("TaskRow")
        h = QHBoxLayout(frame)
        h.setContentsMargins(12, 8, 12, 8)
        h.setSpacing(8)
        baslik = QLabel(eylem.title)
        gun = QLabel(str(eylem.day))
        gun.setObjectName("Tag")
        xp = QLabel(f"+{eylem.xp} Disiplin")
        xp.setObjectName("Counter")
        h.addWidget(baslik, stretch=1)
        h.addWidget(gun)
        h.addWidget(xp)
        return frame

    def _ekle(self) -> None:
        baslik = self._baslik.text().strip()
        if not baslik:
            return
        self._container.irade.ekle(baslik, self._xp.value())
        self._baslik.clear()
        self.yenile()
        self.degisti.emit()
