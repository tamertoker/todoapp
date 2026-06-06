"""Ana pencere.

Solda dikey bir menü (Anasayfa / Ayarlar), sağda seçili sayfayı gösteren bir
alan vardır. Ayrıca sistem tepsisi (tray) ikonu ve menüsü buradan kurulur.
Pencere "X" ile kapatıldığında — ayar açıksa — uygulama kapanmaz, tepsiye
iner ve arka planda yaşamaya devam eder (ileride çalışan kronometre için şart).
"""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction, QCloseEvent, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QHBoxLayout,
    QMenu,
    QPushButton,
    QStackedWidget,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from leveltodo.bootstrap import Container
from leveltodo.domain.events import DusmanDevrildi, SeviyeAtlandi, TaskCompleted
from leveltodo.infrastructure.config import paths
from leveltodo.infrastructure.eventbus.qt_bridge import QtEventBridge
from leveltodo.infrastructure.sound.secim import tamamlama_sesi
from leveltodo.infrastructure.sound.ses_motoru import SesMotoru
from leveltodo.presentation.common.toast import ToastYoneticisi
from leveltodo.presentation.views.admin.admin_view import AdminView
from leveltodo.presentation.views.avatar.avatar_view import AvatarEditorView
from leveltodo.presentation.views.cuzdan.cuzdan_view import CuzdanView
from leveltodo.presentation.views.dashboard.dashboard_view import DashboardView
from leveltodo.presentation.views.gunluk.gunluk_view import GunlukView
from leveltodo.presentation.views.irade.irade_view import IradeView
from leveltodo.presentation.views.istatistik.istatistik_view import IstatistikView
from leveltodo.presentation.views.magaza.magaza_view import MagazaView
from leveltodo.presentation.views.rozetler.rozet_view import RozetView
from leveltodo.presentation.views.rutin.rutin_view import RutinView
from leveltodo.presentation.views.settings.settings_view import SettingsView
from leveltodo.presentation.views.settings.settings_viewmodel import SettingsViewModel
from leveltodo.presentation.views.telafi.telafi_view import TelafiView


class MainWindow(QWidget):
    theme_changed = pyqtSignal(str)
    font_changed = pyqtSignal(str)

    def __init__(self, container: Container, bridge: QtEventBridge) -> None:
        super().__init__()
        self._container = container
        self.setWindowTitle("LevelTodo")
        self.resize(1180, 760)

        # Ses motoru (efektler) — görünümlerden önce kurulur ki onlara verilebilsin.
        self._ses = SesMotoru(paths.assets_dir() / "sounds", container.settings)

        # — Sayfalar —
        self._dashboard = DashboardView(container, bridge)
        self._irade = IradeView(container, self._ses)
        self._rutin = RutinView(container)
        self._gunluk = GunlukView(container)
        self._telafi = TelafiView(container)
        self._avatar_editor = AvatarEditorView()
        self._rozetler = RozetView(container, self._ses)
        self._istatistik = IstatistikView(container)
        self._cuzdan = CuzdanView(container)
        self._magaza = MagazaView(container)
        settings_vm = SettingsViewModel(container.settings)
        self._settings = SettingsView(
            settings_vm, container.yedekleyici, container.bildirim, self._ses
        )
        self._admin = AdminView(container)

        self._stack = QStackedWidget()
        self._stack.addWidget(self._dashboard)
        self._stack.addWidget(self._irade)
        self._stack.addWidget(self._rutin)
        self._stack.addWidget(self._gunluk)
        self._stack.addWidget(self._telafi)
        self._stack.addWidget(self._avatar_editor)
        self._stack.addWidget(self._rozetler)
        self._stack.addWidget(self._istatistik)
        self._stack.addWidget(self._cuzdan)
        self._stack.addWidget(self._magaza)
        self._stack.addWidget(self._settings)
        self._stack.addWidget(self._admin)

        # — Sol menü —
        nav = self._build_nav()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addLayout(nav)
        layout.addWidget(self._stack, stretch=1)

        # — Ayar sinyallerini bağla —
        settings_vm.themeChanged.connect(self.theme_changed)
        settings_vm.fontChanged.connect(self.font_changed)
        settings_vm.dayStartHourChanged.connect(lambda _h: self._dashboard.refresh_day())
        self._admin.degisti.connect(self._dashboard.refresh_day)
        self._telafi.degisti.connect(self._dashboard.refresh_day)
        self._irade.degisti.connect(self._dashboard.refresh_day)
        self._rutin.degisti.connect(self._dashboard.refresh_day)
        self._gunluk.degisti.connect(self._dashboard.refresh_day)
        self._magaza.degisti.connect(self._dashboard.refresh_day)

        self._tray = self._build_tray()

        # Uygulama-içi toast'ı garantili bildirim kanalı olarak kaydet.
        self._toast = ToastYoneticisi(self)
        container.bildirim.kanal_ekle(self._toast.goster)

        # Olaylara göre ses çal (UI thread'inde, köprü üzerinden güvenli).
        bridge.domain_event.connect(self._ses_isle)

    def _ses_isle(self, event: object) -> None:
        if isinstance(event, TaskCompleted):
            self._ses.cal(tamamlama_sesi(event.kritik, event.combo_tetik))
        elif isinstance(event, SeviyeAtlandi):
            self._ses.cal("seviye")
        elif isinstance(event, DusmanDevrildi):
            self._ses.cal("dusman_devrildi")

    def _build_nav(self) -> QVBoxLayout:
        nav = QVBoxLayout()
        nav.setContentsMargins(8, 16, 8, 16)
        nav.setSpacing(4)

        group = QButtonGroup(self)
        for index, label in enumerate(
            (
                "Anasayfa",
                "İrade",
                "Rutin",
                "Günlük",
                "Telafi",
                "Avatar",
                "Rozetler",
                "İstatistik",
                "Cüzdan",
                "Mağaza",
                "Ayarlar",
                "Debug",
            )
        ):
            btn = QPushButton(label)
            btn.setObjectName("NavButton")
            btn.setCheckable(True)
            btn.clicked.connect(lambda _checked, i=index: self._stack.setCurrentIndex(i))
            group.addButton(btn)
            nav.addWidget(btn)
            if index == 0:
                btn.setChecked(True)
        nav.addStretch(1)
        return nav

    def _build_tray(self) -> QSystemTrayIcon | None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return None
        tray = QSystemTrayIcon(self.windowIcon(), self)
        tray.setToolTip("LevelTodo")

        menu = QMenu()
        show_action = QAction("Göster", self)
        show_action.triggered.connect(self._show_and_raise)
        quit_action = QAction("Çıkış", self)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(show_action)
        menu.addAction(quit_action)
        tray.setContextMenu(menu)
        tray.activated.connect(self._on_tray_activated)
        tray.show()
        return tray

    def set_icon(self, icon: QIcon) -> None:
        self.setWindowIcon(icon)
        if self._tray is not None:
            self._tray.setIcon(icon)

    def _show_and_raise(self) -> None:
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._show_and_raise()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._tray is not None and self._container.settings.minimize_to_tray:
            event.ignore()
            self.hide()
        else:
            event.accept()
