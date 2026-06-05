"""Günlük ekranı.

Günün sonunda kısa bir günlük yazarsın. Üstte o güne düşen bir yansıtma sorusu
gösterilir (her gün değişir). Dolu bir günlük kaydedince Farkındalık'a XP
kazanırsın (gün başına bir kez; her dolu günlük günüyle ödül bir tık artar).
İstersen kendi yansıtma sorularını ekleyebilir, altta geçmiş günlüklerini
okuyabilirsin.
"""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from leveltodo.bootstrap import Container


class GunlukView(QWidget):
    degisti = pyqtSignal()

    def __init__(self, container: Container) -> None:
        super().__init__()
        self._container = container

        title = QLabel("Günlük")
        title.setObjectName("Title")
        bilgi = QLabel("Günü kapat — kısa bir yansıma, küçük bir XP. Her gün biraz daha.")
        bilgi.setObjectName("Subtitle")

        self._soru = QLabel()
        self._soru.setObjectName("Subtitle")
        self._soru.setWordWrap(True)

        self._metin = QTextEdit()
        self._metin.setPlaceholderText("Bugünü buraya yaz…")
        self._metin.setMinimumHeight(140)

        self._kaydet_btn = QPushButton("Kaydet")
        self._kaydet_btn.clicked.connect(self._kaydet)
        self._durum = QLabel()
        self._durum.setObjectName("Tag")
        kaydet_satiri = QHBoxLayout()
        kaydet_satiri.addWidget(self._kaydet_btn)
        kaydet_satiri.addWidget(self._durum)
        kaydet_satiri.addStretch(1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(bilgi)
        layout.addWidget(self._soru)
        layout.addWidget(self._metin)
        layout.addLayout(kaydet_satiri)
        layout.addWidget(self._kendi_sorular_bolumu())

        layout.addWidget(QLabel("Geçmiş günlükler"))
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        ic = QWidget()
        self._gecmis_layout = QVBoxLayout(ic)
        self._gecmis_layout.setContentsMargins(0, 0, 0, 0)
        self._gecmis_layout.setSpacing(8)
        scroll.setWidget(ic)
        layout.addWidget(scroll, stretch=1)

        self.yenile()

    # — Kendi yansıtma soruları —
    def _kendi_sorular_bolumu(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("TaskRow")
        v = QVBoxLayout(frame)
        v.setContentsMargins(12, 8, 12, 8)
        v.setSpacing(6)

        baslik = QLabel("Kendi yansıtma soruların")
        baslik.setObjectName("Tag")
        self._yeni_soru = QLineEdit()
        self._yeni_soru.setPlaceholderText("Kendine sormak istediğin bir soru ekle…")
        self._yeni_soru.returnPressed.connect(self._soru_ekle)
        ekle_btn = QPushButton("Soru ekle")
        ekle_btn.clicked.connect(self._soru_ekle)
        ekle_satiri = QHBoxLayout()
        ekle_satiri.addWidget(self._yeni_soru, stretch=1)
        ekle_satiri.addWidget(ekle_btn)

        v.addWidget(baslik)
        v.addLayout(ekle_satiri)
        self._sorular_layout = QVBoxLayout()
        self._sorular_layout.setContentsMargins(0, 0, 0, 0)
        self._sorular_layout.setSpacing(4)
        v.addLayout(self._sorular_layout)
        return frame

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.yenile()

    def yenile(self) -> None:
        durum = self._container.gunluk.bugunku_gunluk()
        self._soru.setText(f"🪶 {durum.soru}" if durum.soru else "")
        if self._metin.toPlainText() != durum.metin:
            self._metin.setPlainText(durum.metin)
        self._durum.setText("✓ bugün ödül alındı" if durum.odul_verildi else "")
        self._sorulari_ciz()
        self._gecmisi_ciz()

    def _sorulari_ciz(self) -> None:
        while self._sorular_layout.count():
            item = self._sorular_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()
        for soru in self._container.gunluk.kullanici_sorulari():
            satir = QHBoxLayout()
            etiket = QLabel(soru.text)
            etiket.setWordWrap(True)
            sil = QPushButton("Sil")
            sil.clicked.connect(lambda _c, sid=soru.id: self._soru_sil(sid))
            satir.addWidget(etiket, stretch=1)
            satir.addWidget(sil)
            kap = QWidget()
            kap.setLayout(satir)
            self._sorular_layout.addWidget(kap)

    def _gecmisi_ciz(self) -> None:
        while self._gecmis_layout.count():
            item = self._gecmis_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()
        gecmis = self._container.gunluk.gecmis()
        if not gecmis:
            bos = QLabel("Henüz günlük yok. Bugünü yazarak başla.")
            bos.setObjectName("Subtitle")
            self._gecmis_layout.addWidget(bos)
        else:
            for ozet in gecmis:
                self._gecmis_layout.addWidget(self._gecmis_satiri(ozet))
        self._gecmis_layout.addStretch(1)

    def _gecmis_satiri(self, ozet) -> QFrame:
        frame = QFrame()
        frame.setObjectName("TaskRow")
        v = QVBoxLayout(frame)
        v.setContentsMargins(12, 8, 12, 8)
        v.setSpacing(2)
        gun = QLabel(ozet.gun)
        gun.setObjectName("Tag")
        metin = QLabel(ozet.metin)
        metin.setWordWrap(True)
        v.addWidget(gun)
        v.addWidget(metin)
        return frame

    # — Eylemler —
    def _kaydet(self) -> None:
        self._container.gunluk.kaydet(self._metin.toPlainText())
        self.yenile()
        self.degisti.emit()

    def _soru_ekle(self) -> None:
        metin = self._yeni_soru.text().strip()
        if not metin:
            return
        self._container.gunluk.soru_ekle(metin)
        self._yeni_soru.clear()
        self.yenile()

    def _soru_sil(self, soru_id: str) -> None:
        self._container.gunluk.soru_sil(soru_id)
        self.yenile()
