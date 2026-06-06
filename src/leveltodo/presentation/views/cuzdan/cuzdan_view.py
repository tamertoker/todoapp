"""Cüzdan ekranı.

Gerçek paranı (uygulama-içi Puan'dan ayrı) takip edersin: gelir/gider ekle,
bakiyeni gör, bu ayın tasarruf hedefi ve harcama bütçesi çubuklarını izle. Altta
istek listen (wishlist): her öğe, biriken paran fiyatına yaklaştıkça görseli
soldan sağa açılır.
"""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QPixmap, QShowEvent
from PyQt6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
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
from leveltodo.presentation.common.resim_acilma import ResimAcilma


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
        self._secili_resim: str | None = None

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
        self._kok.addWidget(self._wishlist_formu())
        self._kok.addWidget(QLabel("İstek listesi"))
        self._wishlist_liste = QVBoxLayout()
        self._wishlist_liste.setSpacing(10)
        self._kok.addLayout(self._wishlist_liste)
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

    def _wishlist_formu(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("TaskRow")
        h = QHBoxLayout(frame)
        h.setContentsMargins(12, 8, 12, 8)
        h.setSpacing(8)
        self._wl_ad = QLineEdit()
        self._wl_ad.setPlaceholderText("İstediğin şey (ör. Kulaklık)")
        self._wl_af = AutoFill(
            self._wl_ad, self._container.cuzdan.wishlist_ad_onerileri, self._wl_secildi
        )
        self._wl_fiyat = _para_kutusu()
        self._resim_btn = QPushButton("Resim seç")
        self._resim_btn.clicked.connect(self._resim_sec)
        self._resim_label = QLabel("(resim yok)")
        self._resim_label.setObjectName("Tag")
        ekle = QPushButton("Listeye ekle")
        ekle.clicked.connect(self._wishlist_ekle)
        h.addWidget(self._wl_ad, stretch=1)
        h.addWidget(self._wl_fiyat)
        h.addWidget(self._resim_btn)
        h.addWidget(self._resim_label)
        h.addWidget(ekle)
        return frame

    # — Tazeleme —
    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.yenile()

    def yenile(self) -> None:
        self._bakiye_label.setText(f"Bakiye: {kurus_tl(self._container.cuzdan.bakiye())}")
        self._aciklama_af.yenile()
        self._wl_af.yenile()
        self._hedef_yenile()
        self._islemleri_ciz()
        self._wishlisti_ciz()

    def _aciklama_secildi(self, metin: str) -> None:
        islem = self._container.cuzdan.islem_oneri(metin)
        if islem is not None:
            self._miktar.setValue(islem.amount / 100)
            idx = self._tur.findData(islem.tur)
            if idx >= 0:
                self._tur.setCurrentIndex(idx)

    def _wl_secildi(self, metin: str) -> None:
        oge = self._container.cuzdan.wishlist_oneri(metin)
        if oge is not None:
            self._wl_fiyat.setValue(oge.price / 100)

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

    def _wishlisti_ciz(self) -> None:
        self._temizle(self._wishlist_liste)
        ogeler = self._container.cuzdan.wishlist()
        if not ogeler:
            bos = QLabel("İstek listen boş. Yukarıdan bir şey ekle.")
            bos.setObjectName("Subtitle")
            self._wishlist_liste.addWidget(bos)
            return
        for oge in ogeler:
            self._wishlist_liste.addWidget(self._wishlist_karti(oge))

    def _wishlist_karti(self, oge) -> QFrame:
        frame = QFrame()
        frame.setObjectName("TaskRow")
        v = QVBoxLayout(frame)
        v.setContentsMargins(12, 8, 12, 8)
        v.setSpacing(6)

        reveal = ResimAcilma()
        pixmap = QPixmap(oge.resim_yolu) if oge.resim_yolu else None
        reveal.setVeri(pixmap, oge.oran)
        v.addWidget(reveal)

        h = QHBoxLayout()
        ad = QLabel(oge.ad)
        fiyat = QLabel(kurus_tl(oge.fiyat))
        fiyat.setObjectName("Counter")
        yuzde = QLabel(f"%{int(oge.oran * 100)}")
        yuzde.setObjectName("Tag")
        sil = QPushButton("Sil")
        sil.clicked.connect(lambda _c, oid=oge.id: self._wishlist_sil(oid))
        h.addWidget(ad, stretch=1)
        h.addWidget(yuzde)
        h.addWidget(fiyat)
        h.addWidget(sil)
        v.addLayout(h)
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

    def _resim_sec(self) -> None:
        yol, _ = QFileDialog.getOpenFileName(
            self, "Resim seç", "", "Resimler (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if yol:
            self._secili_resim = yol
            self._resim_label.setText("✓ resim seçildi")

    def _wishlist_ekle(self) -> None:
        ad = self._wl_ad.text().strip()
        kurus = round(self._wl_fiyat.value() * 100)
        if not ad or kurus <= 0:
            return
        self._container.cuzdan.wishlist_ekle(ad, kurus, self._secili_resim)
        self._wl_ad.clear()
        self._wl_fiyat.setValue(0)
        self._secili_resim = None
        self._resim_label.setText("(resim yok)")
        self.yenile()

    def _wishlist_sil(self, oge_id: str) -> None:
        self._container.cuzdan.wishlist_sil(oge_id)
        self.yenile()
