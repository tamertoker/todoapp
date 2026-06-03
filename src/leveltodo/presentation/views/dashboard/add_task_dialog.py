"""Yeni görev ekleme penceresi.

Başlık, görevin tek seferlik mi her gün mü olduğu ve (istenirse) özel bir ödül
değeri sorulur. 'Özel ödül' işaretlenmezse ödül süreye göre (kronometre Adım
2'de) ya da kronometresiz tamamlamada sabit küçük bir değer olur.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from leveltodo.domain.tasks.kurallar import Tekrar


class AddTaskDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Yeni Görev")
        self.setMinimumWidth(360)

        self._title = QLineEdit()
        self._title.setPlaceholderText("Görev başlığı")

        self._once = QRadioButton("Tek seferlik")
        self._daily = QRadioButton("Her gün")
        self._once.setChecked(True)

        self._override_check = QCheckBox("Özel ödül belirle")
        self._override = QSpinBox()
        self._override.setRange(1, 1000)
        self._override.setValue(10)
        self._override.setEnabled(False)
        self._override_check.toggled.connect(self._override.setEnabled)

        self._warning = QLabel("Lütfen bir görev başlığı gir.")
        self._warning.setStyleSheet("color: #ff6b6b;")
        self._warning.setVisible(False)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(QLabel("Başlık"))
        layout.addWidget(self._title)
        layout.addWidget(QLabel("Tekrar"))
        layout.addWidget(self._once)
        layout.addWidget(self._daily)
        layout.addWidget(self._override_check)
        layout.addWidget(self._override)
        layout.addWidget(self._warning)
        layout.addWidget(buttons)

    def accept(self) -> None:
        if not self._title.text().strip():
            self._warning.setVisible(True)
            return
        super().accept()

    def result_values(self) -> tuple[str, Tekrar, int | None]:
        tekrar = Tekrar.GUNLUK if self._daily.isChecked() else Tekrar.YOK
        ozel_odul = self._override.value() if self._override_check.isChecked() else None
        return self._title.text().strip(), tekrar, ozel_odul
