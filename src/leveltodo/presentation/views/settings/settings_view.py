"""Ayarlar ekranı (View).

Üç ayar sunar:
- Tema: koyu (dark) / açık (light).
- Gün başlangıç saati: 0–23. "Gün" bu saatte başlar (varsayılan 04:00).
- Pencereyi kapatınca sistem tepsisine insin mi?

"Kaydet"e basınca değerler ViewModel üzerinden saklanır ve ilgili sinyaller
yayılır (tema canlı değişir, dashboard tazelenir).
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from leveltodo.application.bildirim_servisi import BildirimServisi
from leveltodo.domain.bildirim.bildirim import BildirimKategori
from leveltodo.infrastructure.backup.yedekleme import Yedekleyici
from leveltodo.presentation.theme.fonts import mevcut_fontlar
from leveltodo.presentation.views.settings.settings_viewmodel import SettingsViewModel

_KATEGORI_ETIKET = {
    BildirimKategori.HATIRLATMA: "Hatırlatmalar",
    BildirimKategori.KUTLAMA: "Kutlamalar",
    BildirimKategori.UYARI: "Uyarılar",
    BildirimKategori.DURTME: "Dürtmeler",
}

_THEME_LABELS = {
    "dark": "Koyu (gece)",
    "light": "Açık (gündüz)",
    "midnight": "Gece Mavisi",
    "forest": "Orman",
    "sunset": "Gün Batımı",
    "arcane": "Mor Büyü",
    "kadim": "Kadim Meşe",
}


class SettingsView(QWidget):
    def __init__(
        self,
        view_model: SettingsViewModel,
        yedekleyici: Yedekleyici | None = None,
        bildirim: BildirimServisi | None = None,
        ses=None,
    ) -> None:
        super().__init__()
        self.view_model = view_model
        self._yedekleyici = yedekleyici
        self._bildirim = bildirim
        self._ses = ses

        panel = QFrame()
        panel.setObjectName("Panel")
        form = QFormLayout(panel)
        form.setContentsMargins(24, 24, 24, 24)
        form.setSpacing(14)

        title = QLabel("Ayarlar")
        title.setObjectName("Title")
        form.addRow(title)

        self._theme = QComboBox()
        for key, label in _THEME_LABELS.items():
            self._theme.addItem(label, key)

        self._font = QComboBox()
        for aile in mevcut_fontlar():
            self._font.addItem(aile, aile)

        self._day_start = QSpinBox()
        self._day_start.setRange(0, 23)
        self._day_start.setSuffix(":00")

        self._minimize = QCheckBox("Pencereyi kapatınca tepsiye insin")

        form.addRow("Tema:", self._theme)
        form.addRow("Yazı tipi:", self._font)
        form.addRow("Gün başlangıcı:", self._day_start)
        form.addRow("", self._minimize)

        self._save_btn = QPushButton("Kaydet")
        self._save_btn.clicked.connect(self._on_save)
        form.addRow(self._save_btn)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.addWidget(panel)
        if self._ses is not None:
            outer.addWidget(self._ses_panel())
        if self._bildirim is not None:
            outer.addWidget(self._bildirim_panel())
        if self._yedekleyici is not None:
            outer.addWidget(self._veri_panel())
        outer.addStretch(1)

        self._load()

    def _ses_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("Panel")
        form = QFormLayout(panel)
        form.setContentsMargins(24, 20, 24, 20)
        form.setSpacing(10)
        baslik = QLabel("Ses")
        baslik.setObjectName("Title")
        form.addRow(baslik)

        self._ses_acik = QCheckBox("Ses efektleri açık")
        self._ses_acik.setChecked(self._ses.acik)
        self._ses_acik.toggled.connect(self._ses.acik_ayarla)
        self._ses_duzey = QSpinBox()
        self._ses_duzey.setRange(0, 100)
        self._ses_duzey.setSuffix("%")
        self._ses_duzey.setValue(self._ses.duzey)
        self._ses_duzey.valueChanged.connect(self._ses.duzey_ayarla)
        form.addRow("", self._ses_acik)
        form.addRow("Ses düzeyi:", self._ses_duzey)
        return panel

    def _bildirim_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("Panel")
        form = QFormLayout(panel)
        form.setContentsMargins(24, 20, 24, 20)
        form.setSpacing(10)

        baslik = QLabel("Bildirimler")
        baslik.setObjectName("Title")
        form.addRow(baslik)

        for kategori, etiket in _KATEGORI_ETIKET.items():
            kutu = QCheckBox(etiket)
            kutu.setChecked(self._bildirim.kategori_acik(kategori))
            kutu.toggled.connect(
                lambda acik, k=kategori: self._bildirim.kategori_ayarla(k, acik)
            )
            form.addRow("", kutu)

        self._sessiz = QCheckBox("Gece sessizliği")
        self._sessiz.setChecked(self._bildirim.sessiz_acik)
        self._sessiz.toggled.connect(self._sessiz_kaydet)
        self._sessiz_bas = QSpinBox()
        self._sessiz_bas.setRange(0, 23)
        self._sessiz_bas.setSuffix(":00")
        self._sessiz_bas.setValue(self._bildirim.sessiz_baslangic)
        self._sessiz_bas.valueChanged.connect(self._sessiz_kaydet)
        self._sessiz_bit = QSpinBox()
        self._sessiz_bit.setRange(0, 23)
        self._sessiz_bit.setSuffix(":00")
        self._sessiz_bit.setValue(self._bildirim.sessiz_bitis)
        self._sessiz_bit.valueChanged.connect(self._sessiz_kaydet)

        form.addRow("", self._sessiz)
        form.addRow("Sessizlik başlangıcı:", self._sessiz_bas)
        form.addRow("Sessizlik bitişi:", self._sessiz_bit)
        return panel

    def _sessiz_kaydet(self) -> None:
        self._bildirim.sessiz_ayarla(
            self._sessiz.isChecked(), self._sessiz_bas.value(), self._sessiz_bit.value()
        )

    def _veri_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("Panel")
        v = QVBoxLayout(panel)
        v.setContentsMargins(24, 20, 24, 20)
        v.setSpacing(10)

        baslik = QLabel("Veri")
        baslik.setObjectName("Title")
        bilgi = QLabel("Verini yedekle ya da bir yedekten geri yükle.")
        bilgi.setObjectName("Subtitle")
        v.addWidget(baslik)
        v.addWidget(bilgi)

        yedek_btn = QPushButton("Yedek al (.db)")
        yedek_btn.clicked.connect(self._yedek_al)
        json_btn = QPushButton("JSON dışa aktar")
        json_btn.clicked.connect(self._json_disa_aktar)
        geri_btn = QPushButton("Geri yükle (.db)")
        geri_btn.clicked.connect(self._geri_yukle)
        butonlar = QHBoxLayout()
        butonlar.addWidget(yedek_btn)
        butonlar.addWidget(json_btn)
        butonlar.addWidget(geri_btn)
        butonlar.addStretch(1)
        v.addLayout(butonlar)
        return panel

    def _yedek_al(self) -> None:
        yol, _ = QFileDialog.getSaveFileName(
            self, "Yedeği kaydet", "leveltodo-yedek.db", "Veritabanı (*.db)"
        )
        if yol:
            self._yedekleyici.sqlite_yedek_al(yol)
            QMessageBox.information(self, "Yedek", "Yedek kaydedildi.")

    def _json_disa_aktar(self) -> None:
        yol, _ = QFileDialog.getSaveFileName(
            self, "JSON dışa aktar", "leveltodo-yedek.json", "JSON (*.json)"
        )
        if yol:
            self._yedekleyici.json_disa_aktar(yol)
            QMessageBox.information(self, "Dışa aktarıldı", "JSON dosyası kaydedildi.")

    def _geri_yukle(self) -> None:
        yol, _ = QFileDialog.getOpenFileName(self, "Yedek seç", "", "Veritabanı (*.db)")
        if not yol:
            return
        try:
            self._yedekleyici.geri_yukle_isaretle(yol)
        except ValueError as hata:
            if self._ses is not None:
                self._ses.cal("hata")
            QMessageBox.warning(self, "Geri yükleme", str(hata))
            return
        QMessageBox.information(
            self,
            "Geri yükleme",
            "Yedek hazırlandı. Değişiklikler uygulamayı yeniden başlatınca yüklenecek.",
        )

    def _load(self) -> None:
        idx = self._theme.findData(self.view_model.theme)
        self._theme.setCurrentIndex(max(idx, 0))
        font_idx = self._font.findData(self.view_model.font)
        self._font.setCurrentIndex(max(font_idx, 0))
        self._day_start.setValue(self.view_model.day_start_hour)
        self._minimize.setChecked(self.view_model.minimize_to_tray)

    def _on_save(self) -> None:
        self.view_model.save(
            theme=self._theme.currentData(),
            day_start_hour=self._day_start.value(),
            minimize_to_tray=self._minimize.isChecked(),
            font=self._font.currentData(),
        )
