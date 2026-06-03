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

from leveltodo.application.gorev_servisi import GorevSatiri
from leveltodo.bootstrap import Container
from leveltodo.domain.events import AppStarted, DomainEvent, TaskCompleted
from leveltodo.domain.time.gun import Gun
from leveltodo.infrastructure.eventbus.qt_bridge import QtEventBridge
from leveltodo.presentation.views.dashboard.add_task_dialog import AddTaskDialog
from leveltodo.presentation.views.dashboard.dashboard_viewmodel import DashboardViewModel


class DashboardView(QWidget):
    def __init__(self, container: Container, bridge: QtEventBridge) -> None:
        super().__init__()
        self._container = container
        self._vm = DashboardViewModel(container.gorevler)

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
        gun = Gun.olustur(self._container.saat.simdi(), self._container.settings.day_start_hour)
        self._day_label.setText(f"Bugün (mantıksal gün): {gun}")
        self._render()

    def _render(self) -> None:
        xp, puan = self._vm.toplamlar()
        self._xp_label.setText(f"XP  {xp}")
        self._points_label.setText(f"Puan  {puan}")

        while self._tasks_layout.count():
            item = self._tasks_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        satirlar = self._vm.satirlar()
        if not satirlar:
            empty = QLabel("Bugün için görev yok. Başlamak için bir görev ekle.")
            empty.setObjectName("Subtitle")
            self._tasks_layout.addWidget(empty)
        else:
            for satir in satirlar:
                self._tasks_layout.addWidget(self._build_row(satir))
        self._tasks_layout.addStretch(1)

    def _build_row(self, satir: GorevSatiri) -> QFrame:
        frame = QFrame()
        frame.setObjectName("TaskRow")
        h = QHBoxLayout(frame)
        h.setContentsMargins(12, 8, 12, 8)
        h.setSpacing(8)

        title = QLabel(satir.baslik)
        tag = QLabel("Her gün" if satir.tekrar == "daily" else "Tek seferlik")
        tag.setObjectName("Tag")
        h.addWidget(title, stretch=1)
        h.addWidget(tag)

        if satir.durum == "pending":
            done_btn = QPushButton("Bitir")
            done_btn.clicked.connect(lambda _checked, i=satir.kayit_id: self._vm.tamamla(i))
            del_btn = QPushButton("Sil")
            del_btn.clicked.connect(lambda _checked, i=satir.kayit_id: self._vm.sil(i))
            h.addWidget(done_btn)
            h.addWidget(del_btn)
        else:
            done = QLabel(f"✓ +{satir.odul_xp} XP")
            done.setObjectName("Counter")
            h.addWidget(done)

        return frame

    def _on_add(self) -> None:
        dialog = AddTaskDialog(self)
        if dialog.exec():
            baslik, tekrar, ozel_odul = dialog.result_values()
            if baslik:
                self._vm.gorev_ekle(baslik, tekrar, ozel_odul)

    def _on_event(self, event: DomainEvent) -> None:
        if isinstance(event, AppStarted):
            self._status_label.setText("Yine buradasın. Çoğu insan dönmez; sen döndün.")
        elif isinstance(event, TaskCompleted):
            self._status_label.setText(f"+{event.xp} XP kazandın. Sırada ne var?")
            self._render()
