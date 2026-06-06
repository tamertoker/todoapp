"""Mağaza ekranı.

Oyun-içi Puan'ını gerçek-hayat ödüllerine (dizi, buluşma, oyun…) DAKİKA cinsinden
harcarsın. Her ödülde süreyi bir kutu + kaydırma çubuğuyla seçersin; fiyat anında
hesaplanır (dakika × dk-maliyeti). Puanın yeterse "Satın al" aktif olur. Her ödülün
dk-maliyetini buradan değiştirebilirsin (bir tabanın altına inemez).
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from leveltodo.bootstrap import Container
from leveltodo.domain.magaza.magaza import MIN_DK_MALIYET
from leveltodo.presentation.common.autofill import AutoFill

_SURE_MAKS = 300  # kaydırma çubuğu üst sınırı (dk)


class MagazaView(QWidget):
    degisti = pyqtSignal()

    def __init__(self, container: Container) -> None:
        super().__init__()
        self._container = container

        title = QLabel("Mağaza")
        title.setObjectName("Title")
        bilgi = QLabel("Puanını dakika cinsinden gerçek-hayat ödüllerine harca.")
        bilgi.setObjectName("Subtitle")
        self._bakiye_label = QLabel()
        self._bakiye_label.setObjectName("ProfileBar")

        ic = QWidget()
        self._kok = QVBoxLayout(ic)
        self._kok.setContentsMargins(0, 0, 0, 0)
        self._kok.setSpacing(10)
        self._kok.addWidget(self._ekle_formu())
        self._odul_liste = QVBoxLayout()
        self._odul_liste.setSpacing(10)
        self._kok.addLayout(self._odul_liste)
        self._kok.addWidget(QLabel("Satın alma geçmişi"))
        self._gecmis_liste = QVBoxLayout()
        self._gecmis_liste.setSpacing(6)
        self._kok.addLayout(self._gecmis_liste)
        self._kok.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(ic)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)
        layout.addWidget(title)
        layout.addWidget(bilgi)
        layout.addWidget(self._bakiye_label)
        layout.addWidget(scroll, stretch=1)

        self.yenile()

    def _ekle_formu(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("TaskRow")
        h = QHBoxLayout(frame)
        h.setContentsMargins(12, 8, 12, 8)
        h.setSpacing(8)
        self._yeni_ad = QLineEdit()
        self._yeni_ad.setPlaceholderText("Yeni ödül (ör. Kahve molası)")
        self._ad_af = AutoFill(
            self._yeni_ad, self._container.magaza.ad_onerileri, self._ad_secildi
        )
        self._yeni_maliyet = QSpinBox()
        self._yeni_maliyet.setRange(MIN_DK_MALIYET, 1000)
        self._yeni_maliyet.setValue(3)
        ekle = QPushButton("Ödül ekle")
        ekle.clicked.connect(self._odul_ekle)
        h.addWidget(self._yeni_ad, stretch=1)
        h.addWidget(QLabel("puan/dk:"))
        h.addWidget(self._yeni_maliyet)
        h.addWidget(ekle)
        return frame

    # — Tazeleme —
    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.yenile()

    def _ad_secildi(self, metin: str) -> None:
        maliyet = self._container.magaza.maliyet_oneri(metin)
        if maliyet is not None:
            self._yeni_maliyet.setValue(maliyet)

    def yenile(self) -> None:
        bakiye = self._container.magaza.bakiye_puan()
        self._bakiye_label.setText(f"Puan: {bakiye}")
        self._ad_af.yenile()
        self._odulleri_ciz(bakiye)
        self._gecmisi_ciz()

    def _temizle(self, layout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

    def _odulleri_ciz(self, bakiye: int) -> None:
        self._temizle(self._odul_liste)
        for odul in self._container.magaza.oduller():
            self._odul_liste.addWidget(self._odul_karti(odul, bakiye))

    def _odul_karti(self, odul, bakiye: int) -> QFrame:
        frame = QFrame()
        frame.setObjectName("TaskRow")
        v = QVBoxLayout(frame)
        v.setContentsMargins(12, 8, 12, 8)
        v.setSpacing(6)

        ust = QHBoxLayout()
        ad = QLabel(odul.name)
        maliyet = QSpinBox()
        maliyet.setRange(MIN_DK_MALIYET, 1000)
        maliyet.setValue(odul.cost_per_min)
        sil = QPushButton("Sil")
        sil.clicked.connect(lambda _c, oid=odul.id: self._odul_sil(oid))
        ust.addWidget(ad, stretch=1)
        ust.addWidget(QLabel("Maliyet:"))
        ust.addWidget(maliyet)
        ust.addWidget(QLabel("puan/dk"))
        ust.addWidget(sil)
        v.addLayout(ust)

        orta = QHBoxLayout()
        sure = QSpinBox()
        sure.setRange(0, 600)
        sure.setSuffix(" dk")
        sure.setValue(30)
        cubuk = QSlider(Qt.Orientation.Horizontal)
        cubuk.setRange(0, _SURE_MAKS)
        cubuk.setValue(30)
        orta.addWidget(QLabel("Süre:"))
        orta.addWidget(sure)
        orta.addWidget(cubuk, stretch=1)
        v.addLayout(orta)

        alt = QHBoxLayout()
        fiyat_label = QLabel()
        fiyat_label.setObjectName("Counter")
        satin_al = QPushButton("Satın al")
        alt.addWidget(fiyat_label, stretch=1)
        alt.addWidget(satin_al)
        v.addLayout(alt)

        def fiyat_guncelle() -> None:
            fiyat = self._container.magaza.fiyat(maliyet.value(), sure.value())
            fiyat_label.setText(f"Fiyat: {fiyat} puan  ({sure.value()} dk × {maliyet.value()})")
            satin_al.setEnabled(0 < fiyat <= bakiye)

        def sure_degisti(deger: int) -> None:
            cubuk.blockSignals(True)
            cubuk.setValue(min(deger, _SURE_MAKS))
            cubuk.blockSignals(False)
            fiyat_guncelle()

        def cubuk_degisti(deger: int) -> None:
            sure.blockSignals(True)
            sure.setValue(deger)
            sure.blockSignals(False)
            fiyat_guncelle()

        def maliyet_degisti(deger: int) -> None:
            self._container.magaza.maliyet_ayarla(odul.id, deger)
            fiyat_guncelle()

        sure.valueChanged.connect(sure_degisti)
        cubuk.valueChanged.connect(cubuk_degisti)
        maliyet.valueChanged.connect(maliyet_degisti)
        satin_al.clicked.connect(lambda: self._satin_al(odul.id, sure.value()))
        fiyat_guncelle()
        return frame

    def _gecmisi_ciz(self) -> None:
        self._temizle(self._gecmis_liste)
        gecmis = self._container.magaza.gecmis()
        if not gecmis:
            bos = QLabel("Henüz bir şey almadın.")
            bos.setObjectName("Subtitle")
            self._gecmis_liste.addWidget(bos)
            return
        for satin in gecmis:
            satir = QLabel(
                f"{satin.day} · {satin.reward_name} · {satin.minutes} dk · {satin.cost} puan"
            )
            satir.setObjectName("Tag")
            self._gecmis_liste.addWidget(satir)

    # — Eylemler —
    def _odul_ekle(self) -> None:
        ad = self._yeni_ad.text().strip()
        if not ad:
            return
        self._container.magaza.odul_ekle(ad, self._yeni_maliyet.value())
        self._yeni_ad.clear()
        self.yenile()

    def _odul_sil(self, odul_id: str) -> None:
        self._container.magaza.odul_sil(odul_id)
        self.yenile()

    def _satin_al(self, odul_id: str, dakika: int) -> None:
        if self._container.magaza.satin_al(odul_id, dakika):
            self.yenile()
            self.degisti.emit()
