"""İstek listesi (wishlist) ekranı — kendi sekmesi.

İstediğin şeyleri (ad + fiyat + resim) buraya eklersin. Her öğenin resmi büyük ve
tam görünür; cüzdan bakiyen fiyatına yaklaştıkça resim soldan sağa açılır. İlerleme
cüzdan bakiyesi / fiyat oranıdır.
"""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QPixmap, QShowEvent
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from leveltodo.bootstrap import Container
from leveltodo.domain.cuzdan.cuzdan import kurus_tl
from leveltodo.presentation.common.autofill import AutoFill
from leveltodo.presentation.common.resim_acilma import ResimAcilma


class WishlistView(QWidget):
    degisti = pyqtSignal()

    def __init__(self, container: Container) -> None:
        super().__init__()
        self._container = container
        self._secili_resim: str | None = None

        title = QLabel("İstek Listesi")
        title.setObjectName("Title")
        bilgi = QLabel("İstediklerini ekle; cüzdan bakiyen fiyatına yaklaştıkça resim açılır.")
        bilgi.setObjectName("Subtitle")

        ic = QWidget()
        self._kok = QVBoxLayout(ic)
        self._kok.setContentsMargins(0, 0, 0, 0)
        self._kok.setSpacing(14)
        self._kart_liste = self._kok  # kartlar doğrudan köke

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(ic)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(bilgi)
        layout.addWidget(self._ekle_formu())
        layout.addWidget(scroll, stretch=1)

        self.yenile()

    def _ekle_formu(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("TaskRow")
        h = QHBoxLayout(frame)
        h.setContentsMargins(12, 8, 12, 8)
        h.setSpacing(8)
        self._ad = QLineEdit()
        self._ad.setPlaceholderText("İstediğin şey (ör. Motor, Kulaklık)")
        self._af = AutoFill(
            self._ad, self._container.cuzdan.wishlist_ad_onerileri, self._ad_secildi
        )
        self._fiyat = QDoubleSpinBox()
        self._fiyat.setRange(0, 100_000_000)
        self._fiyat.setDecimals(2)
        self._fiyat.setSuffix(" ₺")
        self._fiyat.setGroupSeparatorShown(True)
        self._resim_btn = QPushButton("Resim seç")
        self._resim_btn.clicked.connect(self._resim_sec)
        self._resim_label = QLabel("(resim yok)")
        self._resim_label.setObjectName("Tag")
        ekle = QPushButton("Listeye ekle")
        ekle.clicked.connect(self._ekle)
        h.addWidget(self._ad, stretch=1)
        h.addWidget(self._fiyat)
        h.addWidget(self._resim_btn)
        h.addWidget(self._resim_label)
        h.addWidget(ekle)
        return frame

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.yenile()

    def yenile(self) -> None:
        self._af.yenile()
        # Eski kartları temizle (form layout'ta değil; köke eklenen kartlar).
        while self._kart_liste.count():
            item = self._kart_liste.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()
        ogeler = self._container.cuzdan.wishlist()
        if not ogeler:
            bos = QLabel("İstek listen boş. Yukarıdan bir şey ekle.")
            bos.setObjectName("Subtitle")
            self._kart_liste.addWidget(bos)
        else:
            for oge in ogeler:
                self._kart_liste.addWidget(self._kart(oge))
        self._kart_liste.addStretch(1)

    def _kart(self, oge) -> QFrame:
        frame = QFrame()
        frame.setObjectName("TaskRow")
        v = QVBoxLayout(frame)
        v.setContentsMargins(12, 10, 12, 10)
        v.setSpacing(8)

        reveal = ResimAcilma()
        pixmap = QPixmap(oge.resim_yolu) if oge.resim_yolu else None
        reveal.setVeri(pixmap, oge.oran)
        resim_satiri = QHBoxLayout()
        resim_satiri.addStretch(1)
        resim_satiri.addWidget(reveal)
        resim_satiri.addStretch(1)
        v.addLayout(resim_satiri)

        alt = QHBoxLayout()
        ad = QLabel(oge.ad)
        ad.setObjectName("ProfileBar")
        yuzde = QLabel(f"%{int(oge.oran * 100)}")
        yuzde.setObjectName("Tag")
        fiyat = QLabel(kurus_tl(oge.fiyat))
        fiyat.setObjectName("Counter")
        sil = QPushButton("Sil")
        sil.clicked.connect(lambda _c, oid=oge.id: self._sil(oid))
        alt.addWidget(ad, stretch=1)
        alt.addWidget(yuzde)
        alt.addWidget(fiyat)
        alt.addWidget(sil)
        v.addLayout(alt)
        return frame

    # — Eylemler —
    def _ad_secildi(self, metin: str) -> None:
        oge = self._container.cuzdan.wishlist_oneri(metin)
        if oge is not None:
            self._fiyat.setValue(oge.price / 100)

    def _resim_sec(self) -> None:
        yol, _ = QFileDialog.getOpenFileName(
            self, "Resim seç", "", "Resimler (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if yol:
            self._secili_resim = yol
            self._resim_label.setText("✓ resim seçildi")

    def _ekle(self) -> None:
        ad = self._ad.text().strip()
        kurus = round(self._fiyat.value() * 100)
        if not ad or kurus <= 0:
            return
        self._container.cuzdan.wishlist_ekle(ad, kurus, self._secili_resim)
        self._ad.clear()
        self._fiyat.setValue(0)
        self._secili_resim = None
        self._resim_label.setText("(resim yok)")
        self.yenile()
        self.degisti.emit()

    def _sil(self, oge_id: str) -> None:
        self._container.cuzdan.wishlist_sil(oge_id)
        self.yenile()
        self.degisti.emit()
