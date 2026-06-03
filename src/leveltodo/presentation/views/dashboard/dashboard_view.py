"""Dashboard (ana ekran) — Faz 1.

Üstte karşılama + mantıksal gün, ardından iki kasa (XP / Puan), sonra "Görev
Ekle" düğmesi ve bugünün görev listesi. Her bekleyen görev satırında bir
kronometre (Başlat/Duraklat), canlı süre, 'Bitir' ve 'Sil' vardır.

Canlı sayaç saniyede bir tazelenir; çalışan kronometre her 30 saniyede bir
veritabanına yazılır (checkpoint), böylece bir çökmede en fazla ~30 sn kaybolur.
"""

from __future__ import annotations

from PyQt6.QtCore import QTimer
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
from leveltodo.domain.tasks.kurallar import canli_sure
from leveltodo.domain.time.gun import Gun
from leveltodo.infrastructure.eventbus.qt_bridge import QtEventBridge
from leveltodo.presentation.views.dashboard.add_task_dialog import AddTaskDialog
from leveltodo.presentation.views.dashboard.bitir_dialog import BitirDialog
from leveltodo.presentation.views.dashboard.dashboard_viewmodel import DashboardViewModel


def _format_sure(saniye: int) -> str:
    saniye = max(0, saniye)
    saat, kalan = divmod(saniye, 3600)
    dakika, sn = divmod(kalan, 60)
    if saat:
        return f"{saat:02d}:{dakika:02d}:{sn:02d}"
    return f"{dakika:02d}:{sn:02d}"


class DashboardView(QWidget):
    def __init__(self, container: Container, bridge: QtEventBridge) -> None:
        super().__init__()
        self._container = container
        self._vm = DashboardViewModel(container.gorevler, container.kronometre)
        # Çalışan kronometre etiketlerini saniyede bir tazelemek için tutulur.
        self._sure_etiketleri: dict[str, tuple[QLabel, GorevSatiri]] = {}

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

        # Açılışta yarım kalmış kronometre varsa durdur (kaydedilen süre korunur).
        self._kurtarma_sayisi = self._vm.kurtar()

        # Canlı sayaç (1 sn) ve periyodik DB kaydı (30 sn) zamanlayıcıları.
        self._tick_timer = QTimer(self)
        self._tick_timer.timeout.connect(self._tick)
        self._tick_timer.start(1000)
        self._checkpoint_timer = QTimer(self)
        self._checkpoint_timer.timeout.connect(self._vm.checkpoint)
        self._checkpoint_timer.start(30000)

        self.refresh_day()
        self._render()

    def refresh_day(self) -> None:
        gun = Gun.olustur(self._container.saat.simdi(), self._container.settings.day_start_hour)
        self._day_label.setText(f"Bugün: {gun}")
        self._day_label.setToolTip(
            "Gün, senin belirlediğin 'gün başlangıcı' saatine göre sayılır (varsayılan 04:00). "
            "Örneğin gece 02:00 hâlâ dünkü güne sayılır."
        )
        self._render()

    def _render(self) -> None:
        xp, puan = self._vm.toplamlar()
        self._xp_label.setText(f"XP  {xp}")
        self._points_label.setText(f"Puan  {puan}")

        self._sure_etiketleri = {}
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
        frame.setObjectName("TaskRowActive" if satir.calisiyor else "TaskRow")
        h = QHBoxLayout(frame)
        h.setContentsMargins(12, 8, 12, 8)
        h.setSpacing(8)

        title = QLabel(satir.baslik)
        tag = QLabel("Her gün" if satir.tekrar == "daily" else "Tek seferlik")
        tag.setObjectName("Tag")
        h.addWidget(title, stretch=1)
        h.addWidget(tag)

        if satir.durum == "pending":
            sure_etiketi = QLabel(_format_sure(self._canli_saniye(satir)))
            sure_etiketi.setObjectName("Timer")
            h.addWidget(sure_etiketi)
            self._sure_etiketleri[satir.kayit_id] = (sure_etiketi, satir)

            if satir.calisiyor:
                toggle = QPushButton("Duraklat")
                toggle.clicked.connect(lambda _c, i=satir.kayit_id: self._vm.duraklat(i))
            else:
                toggle = QPushButton("Başlat")
                toggle.clicked.connect(lambda _c, i=satir.kayit_id: self._vm.baslat(i))
            done_btn = QPushButton("Bitir")
            done_btn.clicked.connect(lambda _c, s=satir: self._on_bitir(s))
            del_btn = QPushButton("Sil")
            del_btn.clicked.connect(lambda _c, i=satir.kayit_id: self._vm.sil(i))
            h.addWidget(toggle)
            h.addWidget(done_btn)
            h.addWidget(del_btn)
        else:
            sure_etiketi = QLabel(_format_sure(satir.calisilan_saniye))
            sure_etiketi.setObjectName("Timer")
            done = QLabel(f"✓ +{satir.odul_xp} XP")
            done.setObjectName("Counter")
            h.addWidget(sure_etiketi)
            h.addWidget(done)

        return frame

    def _canli_saniye(self, satir: GorevSatiri) -> int:
        return canli_sure(
            satir.calisilan_saniye,
            satir.segment_baslangici if satir.calisiyor else None,
            self._container.saat.simdi(),
        )

    def _tick(self) -> None:
        for _kayit_id, (etiket, satir) in self._sure_etiketleri.items():
            if satir.calisiyor:
                etiket.setText(_format_sure(self._canli_saniye(satir)))

    def _on_add(self) -> None:
        dialog = AddTaskDialog(self)
        if dialog.exec():
            baslik, tekrar, ozel_odul = dialog.result_values()
            if baslik:
                self._vm.gorev_ekle(baslik, tekrar, ozel_odul)

    def _on_bitir(self, satir: GorevSatiri) -> None:
        on_dakika = round(self._canli_saniye(satir) / 60)
        dialog = BitirDialog(on_dakika, self)
        if dialog.exec():
            self._vm.tamamla(satir.kayit_id, dialog.dakika())

    def _on_event(self, event: DomainEvent) -> None:
        if isinstance(event, AppStarted):
            mesaj = "Yine buradasın. Çoğu insan dönmez; sen döndün."
            if self._kurtarma_sayisi:
                mesaj = "Yarım kalmış kronometre vardı, durdurdum — kayıtlı süre duruyor. " + mesaj
            self._status_label.setText(mesaj)
        elif isinstance(event, TaskCompleted):
            self._status_label.setText(f"+{event.xp} XP kazandın. Sırada ne var?")
            self._render()
