"""İstatistik ekranı.

Tek bir metrik seçersin (XP, çalışma süresi, tamamlanan görev ya da herhangi bir
sayısal/evet-hayır rutin alanı) ve onu seçtiğin aralıkta (hafta/ay/yıl) ya **ısı
haritası** ya da **çizgi grafiği** olarak görürsün. Altta stat XP dağılımı ve
kişisel rekorlar var.
"""

from __future__ import annotations

from datetime import timedelta

import pyqtgraph as pg
from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from leveltodo.bootstrap import Container
from leveltodo.presentation.common.heatmap import IsiHaritasi
from leveltodo.presentation.common.ikonlar import ikon

pg.setConfigOption("background", None)  # tema arka planını kullan
pg.setConfigOption("foreground", "#8a8a8a")

_ARALIK = (("Hafta", "hafta"), ("Ay", "ay"), ("Yıl", "yil"))
_GORUNUM = (("Isı haritası", "isi"), ("Çizgi grafiği", "cizgi"))
_CIZGI_RENK = "#39d353"


class IstatistikView(QWidget):
    def __init__(self, container: Container) -> None:
        super().__init__()
        self._container = container
        self._birimler: dict[str, str] = {}

        title = QLabel("İstatistik")
        title.setObjectName("Title")

        self._metrik = QComboBox()
        self._metrik.currentIndexChanged.connect(self._yenile)
        self._aralik = QComboBox()
        for etiket, kip in _ARALIK:
            self._aralik.addItem(etiket, kip)
        self._aralik.setCurrentIndex(2)  # Yıl
        self._aralik.currentIndexChanged.connect(self._yenile)
        self._gorunum = QComboBox()
        for etiket, kip in _GORUNUM:
            self._gorunum.addItem(etiket, kip)
        self._gorunum.currentIndexChanged.connect(self._yenile)

        secici = QHBoxLayout()
        secici.addWidget(QLabel("Metrik:"))
        secici.addWidget(self._metrik)
        secici.addWidget(QLabel("Aralık:"))
        secici.addWidget(self._aralik)
        secici.addWidget(QLabel("Görünüm:"))
        secici.addWidget(self._gorunum)
        secici.addStretch(1)

        # — İçerik: ısı haritası (kaydırmalı) ↔ çizgi —
        self._heatmap = IsiHaritasi()
        isi_scroll = QScrollArea()
        isi_scroll.setWidgetResizable(True)
        isi_scroll.setFrameShape(QFrame.Shape.NoFrame)
        isi_scroll.setWidget(self._heatmap)
        self._plot = pg.PlotWidget()
        self._plot.showGrid(x=False, y=True, alpha=0.2)
        self._content = QStackedWidget()
        self._content.addWidget(isi_scroll)
        self._content.addWidget(self._plot)
        self._content.setMinimumHeight(180)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addLayout(secici)
        layout.addWidget(self._content, stretch=1)
        layout.addWidget(self._stat_paneli())
        layout.addWidget(self._rekor_paneli())

        self._metrikleri_yukle()

    # — Kurulum yardımcıları —
    def _stat_paneli(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Panel")
        v = QVBoxLayout(frame)
        v.setContentsMargins(16, 12, 16, 12)
        v.setSpacing(6)
        baslik = QLabel("Stat XP dağılımı")
        baslik.setObjectName("Tag")
        v.addWidget(baslik)
        self._stat_barlar: dict[str, QProgressBar] = {}
        for etiket in self._container.istatistik.stat_dagilimi():
            bar = QProgressBar()
            bar.setTextVisible(True)
            v.addWidget(bar)
            self._stat_barlar[etiket] = bar
        return frame

    def _rekor_paneli(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Panel")
        v = QVBoxLayout(frame)
        v.setContentsMargins(16, 12, 16, 12)
        v.setSpacing(4)
        baslik = QLabel("Kişisel rekorlar")
        baslik.setObjectName("Tag")
        rekor_px = ikon("rekor_sure", 18)
        if rekor_px is not None:
            baslik_satiri = QHBoxLayout()
            baslik_satiri.setContentsMargins(0, 0, 0, 0)
            baslik_satiri.setSpacing(6)
            ik = QLabel()
            ik.setPixmap(rekor_px)
            baslik_satiri.addWidget(ik)
            baslik_satiri.addWidget(baslik)
            baslik_satiri.addStretch(1)
            v.addLayout(baslik_satiri)
        else:
            v.addWidget(baslik)
        self._rekor_label = QLabel()
        self._rekor_label.setWordWrap(True)
        v.addWidget(self._rekor_label)
        return frame

    def _metrikleri_yukle(self) -> None:
        onceki = self._metrik.currentData()
        self._metrik.blockSignals(True)
        self._metrik.clear()
        self._birimler = {}
        for m in self._container.istatistik.metrik_secenekleri():
            self._metrik.addItem(m.etiket, m.anahtar)
            self._birimler[m.anahtar] = m.birim
        if onceki is not None:
            idx = self._metrik.findData(onceki)
            if idx >= 0:
                self._metrik.setCurrentIndex(idx)
        self._metrik.blockSignals(False)

    # — Tazeleme —
    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self._metrikleri_yukle()
        self._yenile()

    def _yenile(self) -> None:
        metrik = self._metrik.currentData()
        if metrik is None:
            return
        kip = self._aralik.currentData()
        bas, bit = self._container.istatistik.gun_araligi(kip)
        seri = self._container.istatistik.gunluk_seri(metrik, bas, bit)
        birim = self._birimler.get(metrik, "")

        self._heatmap.setVeri(seri, bas, bit, birim)
        self._cizgi_ciz(seri, bas, bit, birim)
        self._content.setCurrentIndex(0 if self._gorunum.currentData() == "isi" else 1)

        self._stat_yenile()
        self._rekor_yenile()

    def _cizgi_ciz(self, seri, bas, bit, birim) -> None:
        gunler = [bas + timedelta(days=i) for i in range((bit - bas).days + 1)]
        x = list(range(len(gunler)))
        y = [seri.get(g, 0) for g in gunler]
        self._plot.clear()
        self._plot.plot(
            x,
            y,
            pen=pg.mkPen(_CIZGI_RENK, width=2),
            symbol="o",
            symbolSize=4,
            symbolBrush=_CIZGI_RENK,
        )
        self._plot.setLabel("left", birim)
        adim = max(1, len(gunler) // 6)
        etiketler = [(i, gunler[i].strftime("%d.%m")) for i in range(0, len(gunler), adim)]
        self._plot.getAxis("bottom").setTicks([etiketler])

    def _stat_yenile(self) -> None:
        dagilim = self._container.istatistik.stat_dagilimi()
        maks = max(dagilim.values(), default=0) or 1
        for etiket, bar in self._stat_barlar.items():
            deger = dagilim.get(etiket, 0)
            bar.setMaximum(maks)
            bar.setValue(deger)
            bar.setFormat(f"{etiket}: {deger} XP")

    def _rekor_yenile(self) -> None:
        r = self._container.istatistik.rekorlar()
        uretken_gun = r.en_uretken_gun[0].strftime("%d.%m.%Y") if r.en_uretken_gun[0] else "—"
        cok_gun = r.en_cok_gorev_gun[0].strftime("%d.%m.%Y") if r.en_cok_gorev_gun[0] else "—"
        dk = r.en_uzun_kronometre_sn // 60
        self._rekor_label.setText(
            f"🔥 En uzun seri: {r.en_uzun_seri} gün\n"
            f"⭐ En üretken gün: {r.en_uretken_gun[1]} XP ({uretken_gun})\n"
            f"⏱ En uzun kronometre: {dk} dk\n"
            f"✅ En çok görev biten gün: {r.en_cok_gorev_gun[1]} görev ({cok_gun})"
        )
