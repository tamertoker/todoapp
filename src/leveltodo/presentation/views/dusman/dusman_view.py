"""Düşman sayfası — biriken hasarı tek darbede indir, hazineyi topla.

Görev yaptıkça "biriken hasar" toplanır (Anasayfa değil, burada görünür). "VUR!"
butonuna basınca hasarın tamamı düşmana iner: can barı düşer, düşman bir lanet
okur, devrilirse arkada bir hazine bırakır. Hazineye tıklayınca tier'a göre artan
bir ödül (puan/XP/combo) açılır. Arkaplan düşmanın inini gösterir.
"""

from __future__ import annotations

from PyQt6.QtCore import (
    QEasingCurve,
    QPoint,
    QPropertyAnimation,
    QSize,
    Qt,
    pyqtSignal,
)
from PyQt6.QtGui import QIcon, QShowEvent
from PyQt6.QtWidgets import (
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from leveltodo.bootstrap import Container
from leveltodo.domain.dusman.dusman import boyut_carpani
from leveltodo.infrastructure.assets.dusman import dusman_resmi
from leveltodo.infrastructure.assets.hazine import hazine_resmi
from leveltodo.infrastructure.config import paths
from leveltodo.presentation.common.arkaplan import ArkaplanCerceve, arkaplan_pixmap

_SAYDAM = "background: transparent;"
_TABAN_BOYUT = 150  # tier 0 düşman sprite kenarı (px); boyut çarpanıyla büyür


class DusmanView(QWidget):
    degisti = pyqtSignal()  # ödül/can değişti → Anasayfa tazelensin

    def __init__(self, container: Container) -> None:
        super().__init__()
        self._container = container
        self._assets = paths.assets_dir()
        self._hp_anim: QPropertyAnimation | None = None
        self._odul_efekt: QGraphicsOpacityEffect | None = None
        self._odul_anim: QPropertyAnimation | None = None
        self._son_anahtar: str | None = None

        title = QLabel("Düşman")
        title.setObjectName("Title")
        bilgi = QLabel("İradenle biriktirdiğin hasarı tek darbede indir.")
        bilgi.setObjectName("Subtitle")

        # — Arena (arkaplan + sprite + baloncuk) —
        self._arena = ArkaplanCerceve(radius=18)
        self._arena.setMinimumHeight(380)
        arena_l = QVBoxLayout(self._arena)
        arena_l.setContentsMargins(20, 16, 20, 16)

        self._balon = QLabel()
        self._balon.setWordWrap(True)
        self._balon.setMaximumWidth(420)
        self._balon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._balon.setStyleSheet(
            "background: rgba(18,10,28,0.86); color: #f2e9ff;"
            "border: 2px solid #6a4d8c; border-radius: 12px; padding: 8px 14px;"
        )
        balon_satir = QHBoxLayout()
        balon_satir.addStretch(1)
        balon_satir.addWidget(self._balon)
        balon_satir.addStretch(1)

        self._sprite = QLabel()
        self._sprite.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._sprite.setStyleSheet(_SAYDAM)

        # Uçan hasar sayısı (vuruşta beliren "−N") — arena'nın serbest çocuğu.
        self._hasar_etiketi = QLabel("", self._arena)
        self._hasar_etiketi.setStyleSheet(
            "background: transparent; color: #ff5d5d; font-size: 30px; font-weight: bold;"
        )
        self._hasar_etiketi.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._hasar_etiketi.hide()

        arena_l.addLayout(balon_satir)
        arena_l.addStretch(1)
        arena_l.addWidget(self._sprite, alignment=Qt.AlignmentFlag.AlignHCenter)
        arena_l.addStretch(1)

        # — Ad + tier + can —
        self._ad_label = QLabel()
        self._ad_label.setObjectName("ProfileBar")
        self._ad_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._hp_bar = QProgressBar()
        self._hp_bar.setObjectName("DusmanHpBar")

        # — Biriken hasar + VUR —
        self._biriken_label = QLabel()
        self._biriken_label.setObjectName("Counter")
        self._vur_btn = QPushButton("⚔  VUR!")
        self._vur_btn.setMinimumHeight(48)
        self._vur_btn.setStyleSheet(
            "QPushButton { font-size: 17px; font-weight: bold; }"
        )
        self._vur_btn.clicked.connect(self._vur)
        vur_satir = QHBoxLayout()
        vur_satir.addWidget(self._biriken_label)
        vur_satir.addStretch(1)
        vur_satir.addWidget(self._vur_btn)

        # — Hazine (sandık görseli + tıkla-aç) —
        self._hazine_btn = QPushButton()
        self._hazine_btn.setMinimumHeight(52)
        self._hazine_btn.setIcon(QIcon(hazine_resmi(self._assets, acik=False, hedef=44)))
        self._hazine_btn.setIconSize(QSize(40, 40))
        self._hazine_btn.clicked.connect(self._hazine_ac)
        self._odul_label = QLabel()
        self._odul_label.setObjectName("Counter")
        self._odul_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._odul_label.setWordWrap(True)
        hazine_satir = QHBoxLayout()
        hazine_satir.addStretch(1)
        hazine_satir.addWidget(self._hazine_btn)
        hazine_satir.addStretch(1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(bilgi)
        layout.addWidget(self._arena, stretch=1)
        layout.addWidget(self._ad_label)
        layout.addWidget(self._hp_bar)
        layout.addLayout(vur_satir)
        layout.addLayout(hazine_satir)
        layout.addWidget(self._odul_label)

        self.yenile()

    # — Tazeleme —
    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.yenile()

    def yenile(self) -> None:
        self._arena.arkaplan_ayarla(arkaplan_pixmap(self._assets, "dusman_arena"))
        self._yenile_dusman(animasyonsuz=True)
        self._biriken_guncelle()
        self._hazine_guncelle()
        if not self._balon.text():
            self._balon.setText("Hadi bakalım, gücün varsa göster kendini...")

    def _yenile_dusman(self, *, animasyonsuz: bool = False) -> None:
        dusman, hp, maks, tier = self._container.dusman.durum()
        hedef = round(_TABAN_BOYUT * boyut_carpani(tier))
        if self._son_anahtar != dusman.anahtar or animasyonsuz:
            self._son_anahtar = dusman.anahtar
        self._sprite.setPixmap(dusman_resmi(self._assets, dusman.anahtar, hedef))
        self._ad_label.setText(f"🗡  {dusman.ad}  ·  Seviye {tier + 1}")
        self._hp_bar.setMaximum(max(1, maks))
        if animasyonsuz:
            self._hp_bar.setValue(max(0, hp))
        self._hp_bar.setFormat(f"Can: {max(0, hp)} / {maks}")

    def _biriken_guncelle(self) -> None:
        biriken = self._container.dusman.biriken_hasar()
        self._biriken_label.setText(f"⚡ Biriken hasar: {biriken}")
        self._vur_btn.setEnabled(biriken > 0)
        if biriken <= 0:
            self._vur_btn.setToolTip("Görev yaptıkça hasar birikir, sonra buradan vurursun.")

    def _hazine_guncelle(self) -> None:
        adet = self._container.dusman.bekleyen_hazine_sayisi()
        self._hazine_btn.setVisible(adet > 0)
        if adet > 0:
            self._hazine_btn.setText(f"🎁  Hazineyi Aç{f'  (×{adet})' if adet > 1 else ''}")

    # — Vuruş —
    def _vur(self) -> None:
        if self._container.dusman.biriken_hasar() <= 0:
            return
        eski_hp = self._hp_bar.value()
        sonuc = self._container.dusman.vur()
        self._balon.setText(sonuc.konusma)
        self._hasar_goster(sonuc.verilen_hasar)
        self._vur_btn.setEnabled(False)

        if sonuc.devrilen:
            self._anim_calistir(eski_hp, 0, bitince=self._devrilme_sonrasi)
        else:
            self._hp_bar.setFormat(f"Can: {sonuc.kalan_hp} / {sonuc.maks_hp}")
            self._anim_calistir(eski_hp, sonuc.kalan_hp)

        self._biriken_guncelle()
        self.degisti.emit()

    def _devrilme_sonrasi(self) -> None:
        self._yenile_dusman(animasyonsuz=True)
        self._hazine_guncelle()
        self._vur_btn.setEnabled(self._container.dusman.biriken_hasar() > 0)

    def _anim_calistir(self, bas: int, son: int, bitince=None) -> None:
        anim = QPropertyAnimation(self._hp_bar, b"value", self)
        anim.setDuration(480)
        anim.setStartValue(bas)
        anim.setEndValue(son)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        def _bitti() -> None:
            if bitince is not None:
                bitince()
            else:
                self._vur_btn.setEnabled(self._container.dusman.biriken_hasar() > 0)

        anim.finished.connect(_bitti)
        self._hp_anim = anim  # GC'ye gitmesin
        anim.start()

    def _hasar_goster(self, miktar: int) -> None:
        if miktar <= 0:
            return
        self._hasar_etiketi.setText(f"−{miktar}")
        self._hasar_etiketi.adjustSize()
        merkez = self._arena.rect().center()
        bas = QPoint(merkez.x() - self._hasar_etiketi.width() // 2, merkez.y())
        self._hasar_etiketi.move(bas)
        self._hasar_etiketi.show()
        self._hasar_etiketi.raise_()

        efekt = QGraphicsOpacityEffect(self._hasar_etiketi)
        self._hasar_etiketi.setGraphicsEffect(efekt)
        op = QPropertyAnimation(efekt, b"opacity", self)
        op.setDuration(800)
        op.setStartValue(1.0)
        op.setEndValue(0.0)
        op.setEasingCurve(QEasingCurve.Type.InCubic)

        yukari = QPropertyAnimation(self._hasar_etiketi, b"pos", self)
        yukari.setDuration(800)
        yukari.setStartValue(bas)
        yukari.setEndValue(QPoint(bas.x(), bas.y() - 40))
        yukari.finished.connect(self._hasar_etiketi.hide)

        self._odul_efekt = efekt
        self._odul_anim = op
        self._hasar_yukari = yukari  # ref
        op.start()
        yukari.start()

    # — Hazine aç —
    def _hazine_ac(self) -> None:
        odul = self._container.dusman.hazine_ac()
        if odul is None:
            return
        self._odul_label.setText(odul.mesaj)
        self._odul_parlat()
        self._hazine_guncelle()
        self.degisti.emit()

    def _odul_parlat(self) -> None:
        efekt = QGraphicsOpacityEffect(self._odul_label)
        self._odul_label.setGraphicsEffect(efekt)
        anim = QPropertyAnimation(efekt, b"opacity", self)
        anim.setDuration(450)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._parlama_anim = anim  # ref
        anim.start()
