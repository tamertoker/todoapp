"""Yeni görev ekleme penceresi.

Başlık, tekrar düzeni (tek seferlik / her gün / her X günde / haftanın günleri /
ayda bir), hangi alanı (stat) geliştirdiği ve istenirse özel ödül sorulur.
Tekrar düzenine göre ilgili ayar (kaç günde bir, hangi günler, ayın kaçı) çıkar.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from leveltodo.domain.stats.statlar import GOREV_STATLARI, STAT_ETIKET
from leveltodo.domain.tasks.kurallar import Tekrar
from leveltodo.presentation.common.autofill import AutoFill

_TEKRAR_SECENEKLERI = [
    ("Tek seferlik", Tekrar.YOK),
    ("Her gün", Tekrar.GUNLUK),
    ("Her X günde bir", Tekrar.HER_X_GUN),
    ("Haftanın günleri", Tekrar.HAFTALIK),
    ("Ayda bir (ayın günü)", Tekrar.AYLIK),
]
_GUN_KISA = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]


class AddTaskDialog(QDialog):
    def __init__(
        self,
        parent: QWidget | None = None,
        oneri_getir=None,
        sablon_getir=None,
        etiket=None,
        stat_servisi=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Yeni Görev")
        self.setMinimumWidth(420)
        self._sablon_getir = sablon_getir
        self._etiket = etiket
        self._stat_servisi = stat_servisi

        self._title = QLineEdit()
        self._title.setPlaceholderText("Görev başlığı")
        if oneri_getir is not None:
            self._autofill = AutoFill(self._title, oneri_getir, self._baslik_secildi)

        self._tekrar = QComboBox()
        for etiket, tekrar in _TEKRAR_SECENEKLERI:
            self._tekrar.addItem(etiket, tekrar)
        self._tekrar.currentIndexChanged.connect(self._param_goster)

        self._x_widget, self._x_spin = self._build_x_widget()
        self._hafta_widget, self._gun_kutulari = self._build_hafta_widget()
        self._ay_widget, self._ay_spin = self._build_ay_widget()

        self._stat = QComboBox()
        self._stat.currentIndexChanged.connect(self._stat_secildi)
        self._stat_doldur()

        self._etiket_combo = QComboBox()
        self._etiket_combo.currentIndexChanged.connect(self._etiket_secildi)
        self._etiket_doldur()

        self._hatirlatma_check = QCheckBox("Hatırlatma kur")
        self._hatirlatma = QTimeEdit()
        self._hatirlatma.setDisplayFormat("HH:mm")
        self._hatirlatma.setEnabled(False)
        self._hatirlatma_check.toggled.connect(self._hatirlatma.setEnabled)

        self._warning = QLabel()
        self._warning.setStyleSheet("color: #ff6b6b;")
        self._warning.setVisible(False)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)
        layout.addWidget(QLabel("Başlık"))
        layout.addWidget(self._title)
        layout.addWidget(QLabel("Tekrar"))
        layout.addWidget(self._tekrar)
        layout.addWidget(self._x_widget)
        layout.addWidget(self._hafta_widget)
        layout.addWidget(self._ay_widget)
        layout.addWidget(QLabel("Hangi alanı geliştirir?"))
        layout.addWidget(self._stat)
        layout.addWidget(QLabel("Proje / etiket"))
        layout.addWidget(self._etiket_combo)
        layout.addWidget(self._hatirlatma_check)
        layout.addWidget(self._hatirlatma)
        layout.addWidget(self._warning)
        layout.addWidget(buttons)

        self._param_goster()

    def _build_x_widget(self) -> tuple[QWidget, QSpinBox]:
        widget = QWidget()
        h = QHBoxLayout(widget)
        h.setContentsMargins(0, 0, 0, 0)
        spin = QSpinBox()
        spin.setRange(1, 365)
        spin.setValue(2)
        h.addWidget(QLabel("Kaç günde bir:"))
        h.addWidget(spin)
        h.addStretch(1)
        return widget, spin

    def _build_hafta_widget(self) -> tuple[QWidget, list[QCheckBox]]:
        widget = QWidget()
        h = QHBoxLayout(widget)
        h.setContentsMargins(0, 0, 0, 0)
        kutular = []
        for ad in _GUN_KISA:
            kutu = QCheckBox(ad)
            kutular.append(kutu)
            h.addWidget(kutu)
        return widget, kutular

    def _build_ay_widget(self) -> tuple[QWidget, QSpinBox]:
        widget = QWidget()
        h = QHBoxLayout(widget)
        h.setContentsMargins(0, 0, 0, 0)
        spin = QSpinBox()
        spin.setRange(1, 31)
        spin.setValue(1)
        h.addWidget(QLabel("Ayın kaçında:"))
        h.addWidget(spin)
        h.addStretch(1)
        return widget, spin

    def _param_goster(self) -> None:
        tekrar = self._tekrar.currentData()
        self._x_widget.setVisible(tekrar is Tekrar.HER_X_GUN)
        self._hafta_widget.setVisible(tekrar is Tekrar.HAFTALIK)
        self._ay_widget.setVisible(tekrar is Tekrar.AYLIK)

    def _stat_doldur(self, secili: str | None = None) -> None:
        self._stat.blockSignals(True)
        self._stat.clear()
        if self._stat_servisi is not None:
            for b in self._stat_servisi.gorev_statlari():
                self._stat.addItem(b.etiket, b.anahtar)
            self._stat.addItem("+ Yeni alan…", "__yeni_stat__")
        else:
            for stat in GOREV_STATLARI:
                self._stat.addItem(STAT_ETIKET[stat], stat.value)
        idx = self._stat.findData(secili) if secili else 0
        self._stat.setCurrentIndex(max(0, idx))
        self._stat.blockSignals(False)

    def _stat_secildi(self) -> None:
        if self._stat.currentData() != "__yeni_stat__":
            return
        ad, ok = QInputDialog.getText(self, "Yeni gelişim alanı", "Alan adı (ör. Yazılım):")
        if ok and ad.strip() and self._stat_servisi is not None:
            yeni = self._stat_servisi.stat_ekle(ad.strip())
            self._stat_doldur(yeni)
        else:
            self._stat_doldur()

    def _etiket_doldur(self, secili_id: str | None = None) -> None:
        self._etiket_combo.blockSignals(True)
        self._etiket_combo.clear()
        self._etiket_combo.addItem("(Etiketsiz)", None)
        if self._etiket is not None:
            for tag in self._etiket.etiketler():
                self._etiket_combo.addItem(f"● {tag.name}", tag.id)
            self._etiket_combo.addItem("+ Yeni etiket…", "__yeni__")
        idx = self._etiket_combo.findData(secili_id) if secili_id else 0
        self._etiket_combo.setCurrentIndex(max(0, idx))
        self._etiket_combo.blockSignals(False)

    def _etiket_secildi(self) -> None:
        if self._etiket_combo.currentData() != "__yeni__":
            return
        ad, ok = QInputDialog.getText(self, "Yeni etiket", "Etiket adı:")
        if ok and ad.strip() and self._etiket is not None:
            renk = QColorDialog.getColor(parent=self, title="Etiket rengi (iptal = otomatik)")
            renk_hex = renk.name() if renk.isValid() else None
            yeni_id = self._etiket.etiket_ekle(ad.strip(), renk_hex)
            self._etiket_doldur(yeni_id)
        else:
            self._etiket_doldur()  # iptal → etiketsiz

    def _baslik_secildi(self, baslik: str) -> None:
        """Öneri seçilince o başlıklı son görevin ayarlarını forma doldur."""
        sablon = self._sablon_getir(baslik) if self._sablon_getir else None
        if sablon is None:
            return
        tekrar = Tekrar(sablon.recurrence)
        idx = self._tekrar.findData(tekrar)
        if idx >= 0:
            self._tekrar.setCurrentIndex(idx)
        param = sablon.recurrence_param or ""
        if tekrar is Tekrar.HER_X_GUN and param:
            self._x_spin.setValue(int(param))
        elif tekrar is Tekrar.HAFTALIK:
            gunler = {int(g) for g in param.split(",") if g != ""}
            for i, kutu in enumerate(self._gun_kutulari):
                kutu.setChecked(i in gunler)
        elif tekrar is Tekrar.AYLIK and param:
            self._ay_spin.setValue(int(param))
        if sablon.stat:
            sidx = self._stat.findData(sablon.stat)
            if sidx >= 0:
                self._stat.setCurrentIndex(sidx)
        if sablon.tag_id:
            tidx = self._etiket_combo.findData(sablon.tag_id)
            if tidx >= 0:
                self._etiket_combo.setCurrentIndex(tidx)
        self._param_goster()

    def accept(self) -> None:
        if not self._title.text().strip():
            self._uyari("Lütfen bir görev başlığı gir.")
            return
        if self._tekrar.currentData() is Tekrar.HAFTALIK and not self._secili_gunler():
            self._uyari("En az bir gün seç.")
            return
        super().accept()

    def _uyari(self, metin: str) -> None:
        self._warning.setText(metin)
        self._warning.setVisible(True)

    def _secili_gunler(self) -> list[int]:
        return [i for i, kutu in enumerate(self._gun_kutulari) if kutu.isChecked()]

    def result_values(
        self,
    ) -> tuple[str, Tekrar, str, int | None, str | None, str | None, str | None]:
        tekrar = self._tekrar.currentData()
        if tekrar is Tekrar.HER_X_GUN:
            parametre = str(self._x_spin.value())
        elif tekrar is Tekrar.HAFTALIK:
            parametre = ",".join(str(g) for g in self._secili_gunler())
        elif tekrar is Tekrar.AYLIK:
            parametre = str(self._ay_spin.value())
        else:
            parametre = ""
        ozel_odul = None  # özel ödül kaldırıldı (seans ödülü süre-temelli)
        stat_key = self._stat.currentData()
        if stat_key == "__yeni_stat__":
            stat_key = None
        tag_data = self._etiket_combo.currentData()
        tag_id = tag_data if isinstance(tag_data, str) and tag_data != "__yeni__" else None
        hatirlatma = None
        if self._hatirlatma_check.isChecked():
            hatirlatma = self._hatirlatma.time().toString("HH:mm")
        return (
            self._title.text().strip(),
            tekrar,
            parametre,
            ozel_odul,
            stat_key,
            tag_id,
            hatirlatma,
        )
