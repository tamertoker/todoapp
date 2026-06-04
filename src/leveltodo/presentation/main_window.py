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
from leveltodo.infrastructure.eventbus.qt_bridge import QtEventBridge
from leveltodo.presentation.views.admin.admin_view import AdminView
from leveltodo.presentation.views.avatar.avatar_view import AvatarEditorView
from leveltodo.presentation.views.dashboard.dashboard_view import DashboardView
from leveltodo.presentation.views.settings.settings_view import SettingsView
from leveltodo.presentation.views.settings.settings_viewmodel import SettingsViewModel


class MainWindow(QWidget):
    theme_changed = pyqtSignal(str)

    def __init__(self, container: Container, bridge: QtEventBridge) -> None:
        super().__init__()
        self._container = container
        self.setWindowTitle("LevelTodo")
        self.resize(1180, 760)

        # — Sayfalar —
        self._dashboard = DashboardView(container, bridge)
        self._avatar_editor = AvatarEditorView()
        settings_vm = SettingsViewModel(container.settings)
        self._settings = SettingsView(settings_vm)
        self._admin = AdminView(container)

        self._stack = QStackedWidget()
        self._stack.addWidget(self._dashboard)
        self._stack.addWidget(self._avatar_editor)
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
        settings_vm.dayStartHourChanged.connect(lambda _h: self._dashboard.refresh_day())
        self._admin.degisti.connect(self._dashboard.refresh_day)

        self._tray = self._build_tray()

    def _build_nav(self) -> QVBoxLayout:
        nav = QVBoxLayout()
        nav.setContentsMargins(8, 16, 8, 16)
        nav.setSpacing(4)

        group = QButtonGroup(self)
        for index, label in enumerate(("Anasayfa", "Avatar", "Ayarlar", "Debug")):
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
