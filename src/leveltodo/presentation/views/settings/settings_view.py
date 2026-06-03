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
    QFormLayout,
    QFrame,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from leveltodo.presentation.views.settings.settings_viewmodel import SettingsViewModel

_THEME_LABELS = {"dark": "Koyu (gece)", "light": "Açık (gündüz)"}


class SettingsView(QWidget):
    def __init__(self, view_model: SettingsViewModel) -> None:
        super().__init__()
        self.view_model = view_model

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

        self._day_start = QSpinBox()
        self._day_start.setRange(0, 23)
        self._day_start.setSuffix(":00")

        self._minimize = QCheckBox("Pencereyi kapatınca tepsiye insin")

        form.addRow("Tema:", self._theme)
        form.addRow("Gün başlangıcı:", self._day_start)
        form.addRow("", self._minimize)

        self._save_btn = QPushButton("Kaydet")
        self._save_btn.clicked.connect(self._on_save)
        form.addRow(self._save_btn)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.addWidget(panel)
        outer.addStretch(1)

        self._load()

    def _load(self) -> None:
        idx = self._theme.findData(self.view_model.theme)
        self._theme.setCurrentIndex(max(idx, 0))
        self._day_start.setValue(self.view_model.day_start_hour)
        self._minimize.setChecked(self.view_model.minimize_to_tray)

    def _on_save(self) -> None:
        self.view_model.save(
            theme=self._theme.currentData(),
            day_start_hour=self._day_start.value(),
            minimize_to_tray=self._minimize.isChecked(),
        )
