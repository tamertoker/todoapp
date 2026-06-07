"""Pano — etiketlere (projelere) göre çalışma süresi dağılımı.

Seçtiğin aralıkta (bugün / bu hafta / bu ay / takvimden özel) her etikete ne kadar
süre harcadığını halka grafiği + kırılım çubuklarıyla gösterir.
"""

from __future__ import annotations

from datetime import date, timedelta

from PyQt6.QtCore import QDate
from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from leveltodo.bootstrap import Container
from leveltodo.presentation.common.halka import Halka


def _sure_metni(saniye: int) -> str:
    saat, kalan = divmod(max(0, saniye), 3600)
    dakika = kalan // 60
    if saat:
        return f"{saat}s {dakika:02d}dk"
    return f"{dakika}dk"


class PanoView(QWidget):
    def __init__(self, container: Container) -> None:
        super().__init__()
        self._container = container

        title = QLabel("Pano")
        title.setObjectName("Title")
        bilgi = QLabel("Etiketlere göre çalışma süresi dağılımı.")
        bilgi.setObjectName("Subtitle")

        self._aralik = QComboBox()
        for etiket, kip in (
            ("Bugün", "bugun"),
            ("Bu hafta", "hafta"),
            ("Bu ay", "ay"),
            ("Özel", "ozel"),
        ):
            self._aralik.addItem(etiket, kip)
        self._aralik.currentIndexChanged.connect(self._aralik_degisti)
        self._bas_tarih = QDateEdit()
        self._bas_tarih.setCalendarPopup(True)
        self._bas_tarih.setDisplayFormat("dd.MM.yyyy")
        self._bas_tarih.dateChanged.connect(self.yenile)
        self._bit_tarih = QDateEdit()
        self._bit_tarih.setCalendarPopup(True)
        self._bit_tarih.setDisplayFormat("dd.MM.yyyy")
        self._bit_tarih.dateChanged.connect(self.yenile)
        self._bas_tarih.setVisible(False)
        self._bit_tarih.setVisible(False)

        secici = QHBoxLayout()
        secici.addWidget(QLabel("Aralık:"))
        secici.addWidget(self._aralik)
        secici.addWidget(self._bas_tarih)
        secici.addWidget(QLabel("–"))
        secici.addWidget(self._bit_tarih)
        self._toplam_label = QLabel()
        self._toplam_label.setObjectName("ProfileBar")
        secici.addStretch(1)
        secici.addWidget(self._toplam_label)

        self._halka = Halka()
        self._kirilim = QVBoxLayout()
        self._kirilim.setSpacing(8)
        kirilim_ic = QWidget()
        kirilim_ic.setLayout(self._kirilim)
        kirilim_scroll = QScrollArea()
        kirilim_scroll.setWidgetResizable(True)
        kirilim_scroll.setFrameShape(QFrame.Shape.NoFrame)
        kirilim_scroll.setWidget(kirilim_ic)

        govde = QHBoxLayout()
        govde.addWidget(self._halka, stretch=1)
        govde.addWidget(kirilim_scroll, stretch=2)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(bilgi)
        layout.addLayout(secici)
        layout.addLayout(govde, stretch=1)

        self._tarihleri_baslat()
        self.yenile()

    def _tarihleri_baslat(self) -> None:
        bugun = self._container.istatistik.bugun()
        self._bas_tarih.blockSignals(True)
        self._bit_tarih.blockSignals(True)
        self._bas_tarih.setDate(QDate(bugun.year, bugun.month, 1))
        self._bit_tarih.setDate(QDate(bugun.year, bugun.month, bugun.day))
        self._bas_tarih.blockSignals(False)
        self._bit_tarih.blockSignals(False)

    def _aralik_degisti(self) -> None:
        ozel = self._aralik.currentData() == "ozel"
        self._bas_tarih.setVisible(ozel)
        self._bit_tarih.setVisible(ozel)
        self.yenile()

    def _aralik_hesapla(self) -> tuple[date, date]:
        bugun = self._container.istatistik.bugun()
        kip = self._aralik.currentData()
        if kip == "bugun":
            return bugun, bugun
        if kip == "hafta":
            return bugun - timedelta(days=6), bugun
        if kip == "ay":
            return bugun.replace(day=1), bugun
        bas = self._bas_tarih.date().toPyDate()
        bit = self._bit_tarih.date().toPyDate()
        return (bas, bit) if bas <= bit else (bit, bas)

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.yenile()

    def yenile(self) -> None:
        bas, bit = self._aralik_hesapla()
        dagilim = self._container.istatistik.etiket_sure_dagilimi(bas, bit)
        toplam = sum(sn for _, _, sn in dagilim)
        self._halka.setVeri(dagilim)
        self._toplam_label.setText(f"Toplam: {_sure_metni(toplam)}")

        while self._kirilim.count():
            item = self._kirilim.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()
        if not dagilim:
            bos = QLabel("Bu aralıkta kayıtlı çalışma süresi yok.")
            bos.setObjectName("Subtitle")
            self._kirilim.addWidget(bos)
        else:
            for etiket, renk, sn in dagilim:
                self._kirilim.addWidget(self._kirilim_satiri(etiket, renk, sn, toplam))
        self._kirilim.addStretch(1)

    def _kirilim_satiri(self, etiket: str, renk: str, saniye: int, toplam: int) -> QFrame:
        frame = QFrame()
        h = QHBoxLayout(frame)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(8)
        nokta = QLabel()
        nokta.setFixedSize(12, 12)
        nokta.setStyleSheet(f"background-color: {renk}; border-radius: 6px;")
        ad = QLabel(etiket)
        sure = QLabel(_sure_metni(saniye))
        sure.setObjectName("Counter")
        bar = QProgressBar()
        bar.setMaximum(max(1, toplam))
        bar.setValue(saniye)
        yuzde = (saniye / toplam * 100) if toplam else 0
        bar.setFormat(f"%{yuzde:.0f}")
        bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {renk}; }}")
        h.addWidget(nokta)
        h.addWidget(ad, stretch=1)
        h.addWidget(sure)
        h.addWidget(bar, stretch=2)
        return frame
