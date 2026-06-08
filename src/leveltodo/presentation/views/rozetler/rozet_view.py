"""Rozetler ekranı (raf).

Tüm rozetler bir ızgarada: kazandıkların renkli/dolu, kilitliler silik ve 🔒.
Ekran açıldığında o anki duruma göre yeni kazanılanlar otomatik işaretlenir.
"""

from __future__ import annotations

from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from leveltodo.bootstrap import Container
from leveltodo.domain.rozetler.rozetler import Rozet, RozetDurumu
from leveltodo.domain.streaks.seriler import SeriTipi
from leveltodo.presentation.common.ikonlar import ikon, ikonlu_baslik

_SUTUN = 3


class RozetView(QWidget):
    def __init__(self, container: Container, ses=None) -> None:
        super().__init__()
        self._container = container
        self._ses = ses

        title = ikonlu_baslik("Rozetler", "rozet")
        bilgi = QLabel("Kazandıkların renkli; kilitliler silik. Başardıkça açılır.")
        bilgi.setObjectName("Subtitle")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        ic = QWidget()
        self._grid = QGridLayout(ic)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSpacing(10)
        scroll.setWidget(ic)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(bilgi)
        layout.addWidget(scroll, stretch=1)

        self.yenile()

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.yenile()  # ekrana her gelişte yeni kazanılanları işaretle

    def yenile(self) -> None:
        profil, _ = self._container.gorevler.profil_durumu()
        _, en_iyi_giris = self._container.seri.durumlar()[SeriTipi.GIRIS]
        durum = RozetDurumu(
            tamamlama=self._container.rozet.tamamlama(),
            en_iyi_giris_serisi=en_iyi_giris,
            profil_seviye=profil,
            kritik_yasandi=self._container.rozet.kritik_yasandi_mi(),
            combo_yasandi=self._container.rozet.combo_yasandi_mi(),
        )
        yeni = self._container.rozet.degerlendir(durum)
        if yeni and self._ses is not None:
            self._ses.cal("rozet")

        while self._grid.count():
            item = self._grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

        for i, (rozet, kazanildi) in enumerate(self._container.rozet.tum_rozetler()):
            self._grid.addWidget(self._kart(rozet, kazanildi), i // _SUTUN, i % _SUTUN)

    def _kart(self, rozet: Rozet, kazanildi: bool) -> QFrame:
        frame = QFrame()
        frame.setObjectName("RozetKartAcik" if kazanildi else "RozetKartKilitli")
        v = QVBoxLayout(frame)
        v.setContentsMargins(12, 10, 12, 10)
        v.setSpacing(4)

        rozet_px = ikon("rozet", 24) if kazanildi else None
        ad_kap = QWidget()
        ad_h = QHBoxLayout(ad_kap)
        ad_h.setContentsMargins(0, 0, 0, 0)
        ad_h.setSpacing(6)
        if rozet_px is not None:
            ik = QLabel()
            ik.setPixmap(rozet_px)
            ad_h.addWidget(ik)
        if rozet_px is not None:
            ad = QLabel(rozet.ad)
        else:
            ad = QLabel(("🏅 " if kazanildi else "🔒 ") + rozet.ad)
        ad.setObjectName("Counter" if kazanildi else "Subtitle")
        ad_h.addWidget(ad)
        ad_h.addStretch(1)
        aciklama = QLabel(rozet.aciklama)
        aciklama.setObjectName("Subtitle")
        aciklama.setWordWrap(True)

        v.addWidget(ad_kap)
        v.addWidget(aciklama)
        return frame
