"""Görevi bitirme penceresi.

Çalışılan süreyi dakika olarak gösterir/girdirir. Kronometre kullanıldıysa o
süre hazır gelir; kullanıcı kronometresiz çalıştıysa elle değiştirebilir.
Ödül bu süreye göre hesaplanır (görevin özel ödülü varsa o geçerli kalır).
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class BitirDialog(QDialog):
    def __init__(self, on_dakika: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Görevi Bitir")
        self.setMinimumWidth(320)

        self._dakika = QSpinBox()
        self._dakika.setRange(0, 100000)
        self._dakika.setValue(on_dakika)
        self._dakika.setSuffix(" dk")

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(QLabel("Çalıştığın süre (kronometre kullandıysan hazır geldi):"))
        layout.addWidget(self._dakika)
        layout.addWidget(buttons)

    def dakika(self) -> int:
        return self._dakika.value()
