"""Cüzdan ekranı.

Gerçek paranı (uygulama-içi Puan'dan ayrı) takip edersin: gelir/gider ekle,
bakiyeni gör, bu ayın tasarruf hedefi ve harcama bütçesi çubuklarını izle.
(İstek listesi artık ayrı "İstek Listesi" sekmesindedir.)
"""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from leveltodo.bootstrap import Container
from leveltodo.domain.cuzdan.cuzdan import kurus_tl
from leveltodo.presentation.common.autofill import AutoFill


def _para_kutusu() -> QDoubleSpinBox:
    kutu = QDoubleSpinBox()
    kutu.setRange(0, 100_000_000)
    kutu.setDecimals(2)
    kutu.setSuffix(" ₺")
    kutu.setGroupSeparatorShown(True)
    return kutu


class CuzdanView(QWidget):
    degisti = pyqtSignal()

    def __init__(self, container: Container) -> None:
        super().__init__()
        self._container = container

        title = QLabel("Cüzdan")
        title.setObjectName("Title")
        self._bakiye_label = QLabel()
        self._bakiye_label.setObjectName("ProfileBar")

        ic = QWidget()
        self._kok = QVBoxLayout(ic)
        self._kok.setContentsMargins(0, 0, 0, 0)
        self._kok.setSpacing(12)
        self._kok.addWidget(self._hedef_paneli())
        self._kok.addWidget(self._islem_formu())
        self._kok.addWidget(QLabel("Son işlemler"))
        self._islem_liste = QVBoxLayout()
        self._islem_liste.setSpacing(6)
        self._kok.addLayout(self._islem_liste)
        self._kok.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(ic)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(self._bakiye_label)
        layout.addWidget(scroll, stretch=1)

        self.yenile()

    # — Paneller —
    def _hedef_paneli(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Panel")
        v = QVBoxLayout(frame)
        v.setContentsMargins(16, 12, 16, 12)
        v.setSpacing(8)
        v.addWidget(QLabel("Bu ayın hedefleri"))
        self._tasarruf_bar = QProgressBar()
        self._harcama_bar = QProgressBar()
        v.addWidget(self._tasarruf_bar)
        v.addWidget(self._harcama_bar)

        self._tasarruf_giris = _para_kutusu()
        self._butce_giris = _para_kutusu()
        kaydet = QPushButton("Hedefleri kaydet")
        kaydet.clicked.connect(self._hedefler_kaydet)
        ayar = QHBoxLayout()
        ayar.addWidget(QLabel("Tasarruf hedefi:"))
        ayar.addWidget(self._tasarruf_giris)
        ayar.addWidget(QLabel("Harcama bütçesi:"))
        ayar.addWidget(self._butce_giris)
        ayar.addWidget(kaydet)
        ayar.addStretch(1)
        v.addLayout(ayar)
        return frame

    def _islem_formu(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("TaskRow")
        h = QHBoxLayout(frame)
        h.setContentsMargins(12, 8, 12, 8)
        h.setSpacing(8)
        self._miktar = _para_kutusu()
        self._tur = QComboBox()
        self._tur.addItem("Gelir", "gelir")
        self._tur.addItem("Gider", "gider")
        self._aciklama = QLineEdit()
        self._aciklama.setPlaceholderText("Açıklama (ör. maaş, market)")
        self._aciklama_af = AutoFill(
            self._aciklama, self._container.cuzdan.aciklama_onerileri, self._aciklama_secildi
        )
        ekle = QPushButton("Ekle")
        ekle.clicked.connect(self._islem_ekle)
        h.addWidget(self._miktar)
        h.addWidget(self._tur)
        h.addWidget(self._aciklama, stretch=1)
        h.addWidget(ekle)
        return frame

    # — Tazeleme —
    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.yenile()

    def yenile(self) -> None:
        self._bakiye_label.setText(f"Bakiye: {kurus_tl(self._container.cuzdan.bakiye())}")
        self._aciklama_af.yenile()
        self._hedef_yenile()
        self._islemleri_ciz()

    def _aciklama_secildi(self, metin: str) -> None:
        islem = self._container.cuzdan.islem_oneri(metin)
        if islem is not None:
            self._miktar.setValue(islem.amount / 100)
            idx = self._tur.findData(islem.tur)
            if idx >= 0:
                self._tur.setCurrentIndex(idx)

    def _hedef_yenile(self) -> None:
        ozet = self._container.cuzdan.aylik_ozet()
        self._tasarruf_giris.setValue(ozet.tasarruf_hedefi / 100)
        self._butce_giris.setValue(ozet.harcama_butcesi / 100)

        if ozet.tasarruf_hedefi > 0:
            self._tasarruf_bar.setMaximum(ozet.tasarruf_hedefi // 100)
            self._tasarruf_bar.setValue(max(0, min(ozet.tasarruf, ozet.tasarruf_hedefi)) // 100)
            self._tasarruf_bar.setFormat(
                f"Tasarruf: {kurus_tl(ozet.tasarruf)} / {kurus_tl(ozet.tasarruf_hedefi)}"
            )
        else:
            self._tasarruf_bar.setMaximum(1)
            self._tasarruf_bar.setValue(0)
            self._tasarruf_bar.setFormat(f"Tasarruf: {kurus_tl(ozet.tasarruf)} (hedef ayarla)")

        if ozet.harcama_butcesi > 0:
            self._harcama_bar.setMaximum(ozet.harcama_butcesi // 100)
            self._harcama_bar.setValue(min(ozet.bu_ay_gider, ozet.harcama_butcesi) // 100)
            asti = " — aşıldı!" if ozet.bu_ay_gider > ozet.harcama_butcesi else ""
            self._harcama_bar.setFormat(
                f"Harcama: {kurus_tl(ozet.bu_ay_gider)} / {kurus_tl(ozet.harcama_butcesi)}{asti}"
            )
        else:
            self._harcama_bar.setMaximum(1)
            self._harcama_bar.setValue(0)
            self._harcama_bar.setFormat(f"Harcama: {kurus_tl(ozet.bu_ay_gider)} (bütçe ayarla)")

    def _temizle(self, layout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

    def _islemleri_ciz(self) -> None:
        self._temizle(self._islem_liste)
        islemler = self._container.cuzdan.son_islemler()
        if not islemler:
            bos = QLabel("Henüz işlem yok.")
            bos.setObjectName("Subtitle")
            self._islem_liste.addWidget(bos)
            return
        for islem in islemler:
            self._islem_liste.addWidget(self._islem_satiri(islem))

    def _islem_satiri(self, islem) -> QFrame:
        frame = QFrame()
        frame.setObjectName("TaskRow")
        h = QHBoxLayout(frame)
        h.setContentsMargins(12, 6, 12, 6)
        h.setSpacing(8)
        isaret = "+" if islem.tur == "gelir" else "−"
        tutar = QLabel(f"{isaret}{kurus_tl(islem.amount)}")
        tutar.setObjectName("Counter")
        gun = QLabel(str(islem.day))
        gun.setObjectName("Tag")
        aciklama = QLabel(islem.aciklama or islem.tur)
        sil = QPushButton("Sil")
        sil.clicked.connect(lambda _c, iid=islem.id: self._islem_sil(iid))
        h.addWidget(tutar)
        h.addWidget(gun)
        h.addWidget(aciklama, stretch=1)
        h.addWidget(sil)
        return frame

    # — Eylemler —
    def _islem_ekle(self) -> None:
        kurus = round(self._miktar.value() * 100)
        if kurus <= 0:
            return
        self._container.cuzdan.islem_ekle(kurus, self._tur.currentData(), self._aciklama.text())
        self._miktar.setValue(0)
        self._aciklama.clear()
        self.yenile()
        self.degisti.emit()

    def _islem_sil(self, islem_id: str) -> None:
        self._container.cuzdan.islem_sil(islem_id)
        self.yenile()
        self.degisti.emit()

    def _hedefler_kaydet(self) -> None:
        self._container.cuzdan.hedefler_ayarla(
            round(self._tasarruf_giris.value() * 100),
            round(self._butce_giris.value() * 100),
        )
        self.yenile()
