"""Debug / Admin menüsü — yalnızca geliştirme ve test için.

Tarihi ileri/geri kaydırarak tekrarlı görevleri, ve statlara doğrudan XP
ekleyerek seviye/avatar/unvan evrimini elle deneyebilirsin. Değişiklikten sonra
'degisti' sinyali yayılır; ana ekran kendini tazeler.
"""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from leveltodo.bootstrap import Container
from leveltodo.domain.stats.statlar import STAT_ETIKET, Stat
from leveltodo.domain.time.gun import Gun


class AdminView(QWidget):
    degisti = pyqtSignal()

    def __init__(self, container: Container) -> None:
        super().__init__()
        self._container = container

        title = QLabel("Debug / Admin")
        title.setObjectName("Title")
        uyari = QLabel("Sadece geliştirme/test için: tarihi ve stat XP'sini elle değiştir.")
        uyari.setObjectName("Subtitle")

        self._gun_label = QLabel()
        self._gun_label.setObjectName("Counter")
        geri = QPushButton("◀ -1 gün")
        geri.clicked.connect(lambda: self._gun_kaydir(-1))
        ileri = QPushButton("+1 gün ▶")
        ileri.clicked.connect(lambda: self._gun_kaydir(+1))
        sifirla = QPushButton("Bugüne dön")
        sifirla.clicked.connect(self._gun_sifirla)
        tarih_satiri = QHBoxLayout()
        tarih_satiri.addWidget(geri)
        tarih_satiri.addWidget(ileri)
        tarih_satiri.addWidget(sifirla)
        tarih_satiri.addStretch(1)

        self._stat_combo = QComboBox()
        for stat in Stat:
            self._stat_combo.addItem(STAT_ETIKET[stat], stat.value)
        self._xp_spin = QSpinBox()
        self._xp_spin.setRange(1, 100000)
        self._xp_spin.setValue(600)
        xp_btn = QPushButton("XP Ekle")
        xp_btn.clicked.connect(self._xp_ekle)
        xp_satiri = QHBoxLayout()
        xp_satiri.addWidget(self._stat_combo)
        xp_satiri.addWidget(self._xp_spin)
        xp_satiri.addWidget(xp_btn)
        xp_satiri.addStretch(1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(uyari)
        layout.addWidget(QLabel("Tarih"))
        layout.addWidget(self._gun_label)
        layout.addLayout(tarih_satiri)
        layout.addWidget(QLabel("Stat XP ekle (seviye/avatar/unvan testi)"))
        layout.addLayout(xp_satiri)
        layout.addStretch(1)

        self._gun_guncelle()

    def _gun_guncelle(self) -> None:
        gun = Gun.olustur(self._container.saat.simdi(), self._container.settings.day_start_hour)
        ofset = 0
        if hasattr(self._container.saat, "ofset_gun"):
            ofset = self._container.saat.ofset_gun()
        self._gun_label.setText(f"Mantıksal gün: {gun}   (kaydırma: {ofset:+d} gün)")

    def _gun_kaydir(self, n: int) -> None:
        if hasattr(self._container.saat, "gun_kaydir"):
            self._container.saat.gun_kaydir(n)
        self._gun_guncelle()
        self.degisti.emit()

    def _gun_sifirla(self) -> None:
        if hasattr(self._container.saat, "sifirla"):
            self._container.saat.sifirla()
        self._gun_guncelle()
        self.degisti.emit()

    def _xp_ekle(self) -> None:
        stat = Stat(self._stat_combo.currentData())
        self._container.gorevler.gelistirme_xp_ekle(stat, self._xp_spin.value())
        self.degisti.emit()
