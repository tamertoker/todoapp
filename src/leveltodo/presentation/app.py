"""Uygulama sınıfı — Qt tarafının kurulumu.

bootstrap'ın ürettiği Container'ı (saf altyapı) alır ve üstüne Qt katmanını
kurar: QApplication, tema uygulama, olay köprüsü, ana pencere. Tema değişimi
canlı çalışır: ayarlardan tema değişince stylesheet ve ikon yeniden uygulanır.
"""

from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from leveltodo.bootstrap import Container
from leveltodo.domain.events import AppStarted
from leveltodo.infrastructure.eventbus.qt_bridge import QtEventBridge
from leveltodo.presentation.common.icon import make_app_icon
from leveltodo.presentation.main_window import MainWindow
from leveltodo.presentation.theme.fonts import load_pixel_font
from leveltodo.presentation.theme.palette import get_palette
from leveltodo.presentation.theme.qss import build_qss


class LevelTodoApp:
    def __init__(self, container: Container) -> None:
        self.container = container
        self.qapp = QApplication.instance() or QApplication(sys.argv)
        self._font_family = load_pixel_font()

        self.bridge = QtEventBridge(container.olay_hatti)
        self.window = MainWindow(container, self.bridge)

        self._apply_theme(container.settings.theme)
        self.window.theme_changed.connect(self._apply_theme)

    def _apply_theme(self, theme: str) -> None:
        palette = get_palette(theme)
        self.qapp.setStyleSheet(build_qss(palette, self._font_family))
        icon = make_app_icon(palette)
        self.qapp.setWindowIcon(icon)
        self.window.set_icon(icon)

    def run(self) -> int:
        self.window.show()
        self.container.olay_hatti.publish(AppStarted(occurred_at=self.container.saat.simdi()))
        return self.qapp.exec()
