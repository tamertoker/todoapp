"""Ayarlar ekranının ViewModel'i (MVVM).

ViewModel, ekran (View) ile servis arasındaki aracıdır. View sadece "kaydet"
der; ViewModel ayarı servise yazdırır ve "tema değişti / gün saati değişti"
gibi sinyaller yayar. Bu sinyalleri pencere dinleyip temayı yeniden uygular
veya dashboard'ı tazeler. Böylece ekran ile iş mantığı ayrık kalır.
"""

from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal

from leveltodo.application.settings_service import SettingsService


class SettingsViewModel(QObject):
    themeChanged = pyqtSignal(str)
    dayStartHourChanged = pyqtSignal(int)
    saved = pyqtSignal()

    def __init__(self, settings: SettingsService) -> None:
        super().__init__()
        self._settings = settings

    @property
    def theme(self) -> str:
        return self._settings.theme

    @property
    def day_start_hour(self) -> int:
        return self._settings.day_start_hour

    @property
    def minimize_to_tray(self) -> bool:
        return self._settings.minimize_to_tray

    def save(self, theme: str, day_start_hour: int, minimize_to_tray: bool) -> None:
        theme_changed = theme != self._settings.theme
        hour_changed = day_start_hour != self._settings.day_start_hour

        self._settings.set("theme", theme)
        self._settings.set("day_start_hour", day_start_hour)
        self._settings.set("minimize_to_tray", minimize_to_tray)

        if theme_changed:
            self.themeChanged.emit(theme)
        if hour_changed:
            self.dayStartHourChanged.emit(day_start_hour)
        self.saved.emit()
