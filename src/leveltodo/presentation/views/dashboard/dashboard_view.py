"""Dashboard (ana ekran) — Faz 1.

Üstte karşılama + mantıksal gün, ardından iki kasa (XP / Puan), sonra "Görev
Ekle" düğmesi ve bugünün görev listesi. Her görev satırında 'Bitir' (ödülü
kazandırır) ve 'Sil' düğmeleri var; tamamlananlar kazanılan XP ile işaretlenir.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from leveltodo.application.task_service import TaskRow
from leveltodo.bootstrap import Container
from leveltodo.domain.events import AppStarted, DomainEvent, TaskCompleted
from leveltodo.domain.time.day import DayId
from leveltodo.infrastructure.eventbus.qt_bridge import QtEventBridge
from leveltodo.presentation.views.dashboard.add_task_dialog import AddTaskDialog
from leveltodo.presentation.views.dashboard.dashboard_viewmodel import DashboardViewModel


class DashboardView(QWidget):
    def __init__(self, container: Container, bridge: QtEventBridge) -> None:
        super().__init__()
        self._container = container
        self._vm = DashboardViewModel(container.tasks)

        title = QLabel("LevelTodo")
        title.setObjectName("Title")
        subtitle = QLabel("Burada güç, gösterdiğin iradeyle ölçülür.")
        subtitle.setObjectName("Subtitle")
        self._day_label = QLabel()
        self._status_label = QLabel("…")
        self._status_label.setObjectName("Subtitle")

        self._xp_label = QLabel()
        self._xp_label.setObjectName("Counter")
        self._points_label = QLabel()
        self._points_label.setObjectName("Counter")
        counters = QHBoxLayout()
        counters.addWidget(self._xp_label)
        counters.addSpacing(24)
        counters.addWidget(self._points_label)
        counters.addStretch(1)

        add_btn = QPushButton("+ Görev Ekle")
        add_btn.clicked.connect(self._on_add)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        tasks_container = QWidget()
        self._tasks_layout = QVBoxLayout(tasks_container)
        self._tasks_layout.setContentsMargins(0, 0, 0, 0)
        self._tasks_layout.setSpacing(8)
        scroll.setWidget(tasks_container)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self._day_label)
        layout.addWidget(self._status_label)
        layout.addLayout(counters)
        layout.addWidget(add_btn)
        layout.addWidget(scroll, stretch=1)

        self._vm.changed.connect(self._render)
        bridge.domain_event.connect(self._on_event)

        self.refresh_day()
        self._render()

    def refresh_day(self) -> None:
        day = DayId.of(self._container.clock.now(), self._container.settings.day_start_hour)
        self._day_label.setText(f"Bugün (mantıksal gün): {day}")
        self._render()

    def _render(self) -> None:
        xp, points = self._vm.totals()
        self._xp_label.setText(f"XP  {xp}")
        self._points_label.setText(f"Puan  {points}")

        while self._tasks_layout.count():
            item = self._tasks_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        rows = self._vm.rows()
        if not rows:
            empty = QLabel("Bugün için görev yok. Başlamak için bir görev ekle.")
            empty.setObjectName("Subtitle")
            self._tasks_layout.addWidget(empty)
        else:
            for row in rows:
                self._tasks_layout.addWidget(self._build_row(row))
        self._tasks_layout.addStretch(1)

    def _build_row(self, row: TaskRow) -> QFrame:
        frame = QFrame()
        frame.setObjectName("TaskRow")
        h = QHBoxLayout(frame)
        h.setContentsMargins(12, 8, 12, 8)
        h.setSpacing(8)

        title = QLabel(row.title)
        tag = QLabel("Her gün" if row.recurrence == "daily" else "Tek seferlik")
        tag.setObjectName("Tag")
        h.addWidget(title, stretch=1)
        h.addWidget(tag)

        if row.status == "pending":
            done_btn = QPushButton("Bitir")
            done_btn.clicked.connect(lambda _checked, i=row.instance_id: self._vm.complete(i))
            del_btn = QPushButton("Sil")
            del_btn.clicked.connect(lambda _checked, i=row.instance_id: self._vm.delete(i))
            h.addWidget(done_btn)
            h.addWidget(del_btn)
        else:
            done = QLabel(f"✓ +{row.reward_xp} XP")
            done.setObjectName("Counter")
            h.addWidget(done)

        return frame

    def _on_add(self) -> None:
        dialog = AddTaskDialog(self)
        if dialog.exec():
            title, recurrence, override = dialog.result_values()
            if title:
                self._vm.add_task(title, recurrence, override)

    def _on_event(self, event: DomainEvent) -> None:
        if isinstance(event, AppStarted):
            self._status_label.setText("Yine buradasın. Çoğu insan dönmez; sen döndün.")
        elif isinstance(event, TaskCompleted):
            self._status_label.setText(f"+{event.xp} XP kazandın. Sırada ne var?")
            self._render()
