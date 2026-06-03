"""Dashboard (ana ekran) — Faz 0 iskeleti.

Şu an sadece üç şeyi gösterir, ama bunlar mimarinin uçtan uca çalıştığını
kanıtlar:
- Başlık/alt başlık (tema buradan görünür).
- "Bugün" = mantıksal gün (DayId). Ayarlardan gün-başlangıç saati değişince
  refresh_day() ile güncellenir → IClock + DayId çalışıyor demektir.
- Açılışta gelen AppStarted olayını yakalayıp bir karşılama satırı gösterir →
  domain olayı → blinker bus → Qt köprüsü zinciri çalışıyor demektir.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from leveltodo.bootstrap import Container
from leveltodo.domain.events import AppStarted, DomainEvent
from leveltodo.domain.time.day import DayId
from leveltodo.infrastructure.eventbus.qt_bridge import QtEventBridge


class DashboardView(QWidget):
    def __init__(self, container: Container, bridge: QtEventBridge) -> None:
        super().__init__()
        self._container = container

        panel = QFrame()
        panel.setObjectName("Panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(24, 24, 24, 24)
        panel_layout.setSpacing(12)

        title = QLabel("LevelTodo")
        title.setObjectName("Title")

        subtitle = QLabel("Faz 0 — İskelet hazır. Macera birazdan başlıyor.")
        subtitle.setObjectName("Subtitle")

        self._day_label = QLabel()
        self._status_label = QLabel("…")
        self._status_label.setObjectName("Subtitle")

        for w in (title, subtitle, self._day_label, self._status_label):
            w.setAlignment(Qt.AlignmentFlag.AlignLeft)
            panel_layout.addWidget(w)
        panel_layout.addStretch(1)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.addWidget(panel)

        bridge.domain_event.connect(self._on_event)
        self.refresh_day()

    def refresh_day(self) -> None:
        day = DayId.of(self._container.clock.now(), self._container.settings.day_start_hour)
        self._day_label.setText(f"Bugün (mantıksal gün): {day}")

    def _on_event(self, event: DomainEvent) -> None:
        if isinstance(event, AppStarted):
            self._status_label.setText("Hoş geldin, maceracı. Sistem ayakta. ⚔")
