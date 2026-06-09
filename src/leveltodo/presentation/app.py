"""Uygulama sınıfı — Qt tarafının kurulumu.

bootstrap'ın ürettiği Container'ı (saf altyapı) alır ve üstüne Qt katmanını
kurar: QApplication, tema uygulama, olay köprüsü, ana pencere. Tema değişimi
canlı çalışır: ayarlardan tema değişince stylesheet ve ikon yeniden uygulanır.
"""

from __future__ import annotations

import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

from leveltodo.bootstrap import Container
from leveltodo.domain.events import AppStarted
from leveltodo.infrastructure.config import paths
from leveltodo.infrastructure.eventbus.qt_bridge import QtEventBridge
from leveltodo.presentation.common.icon import make_app_icon
from leveltodo.presentation.common.ikonlar import uygulama_ikonu
from leveltodo.presentation.common.imlec import imlec_uygula
from leveltodo.presentation.main_window import MainWindow
from leveltodo.presentation.theme.arrows import ok_yollari
from leveltodo.presentation.theme.fonts import gecerli_font, load_all_fonts
from leveltodo.presentation.theme.palette import get_palette
from leveltodo.presentation.theme.qss import build_qss


class LevelTodoApp:
    def __init__(self, container: Container) -> None:
        self.container = container
        container.seri.giris_kaydet()  # bugünkü giriş serisini işaretle
        self.qapp = QApplication.instance() or QApplication(sys.argv)
        load_all_fonts()  # tüm .ttf'leri Qt'ye yükle
        self._font_family = gecerli_font(str(container.settings.get("font")))
        self.qapp.setFont(QFont(self._font_family))  # QSS dışı widget'lara da uygula

        self.bridge = QtEventBridge(container.olay_hatti)
        self.window = MainWindow(container, self.bridge)

        self._apply_theme(container.settings.theme)
        self.window.theme_changed.connect(self._apply_theme)
        self.window.font_changed.connect(self._apply_font)

        # Temiz çıkışta çalışan kronometreyi kaydet (kısa süreler bile kaybolmasın).
        self.qapp.aboutToQuit.connect(container.kronometre.checkpoint)

        # Mentor/düşman/amnesti mesajlarını periyodik değerlendir (gün içinde).
        self._mentor_timer = QTimer(self.qapp)
        self._mentor_timer.setInterval(30 * 60 * 1000)  # 30 dakika
        self._mentor_timer.timeout.connect(container.mentor.periyodik_kontrol)
        self._mentor_timer.start()

        # Görev hatırlatmalarını sık kontrol et (saat hassasiyeti için dakikada bir).
        self._hatirlatma_timer = QTimer(self.qapp)
        self._hatirlatma_timer.setInterval(60 * 1000)  # 1 dakika
        self._hatirlatma_timer.timeout.connect(container.hatirlatma.kontrol)
        self._hatirlatma_timer.start()

    def _apply_theme(self, theme: str) -> None:
        palette = get_palette(theme)
        up_arrow, down_arrow = ok_yollari(palette.text)
        self.qapp.setStyleSheet(build_qss(palette, self._font_family, up_arrow, down_arrow))
        icon = uygulama_ikonu() or make_app_icon(palette)
        self.qapp.setWindowIcon(icon)
        self.window.set_icon(icon)

    def _apply_font(self, font: str) -> None:
        self._font_family = gecerli_font(font)
        qfont = QFont(self._font_family)
        # Press Start 2P çok geniş/iri bir piksel fonttur; varsayılan puntoda taşar.
        if self._font_family == "Press Start 2P":
            qfont.setPointSize(7)
        self.qapp.setFont(qfont)
        self._apply_theme(self.container.settings.theme)

    def run(self) -> int:
        self.window.show()
        imlec_uygula(paths.assets_dir(), self.container.settings.get("imlec"))
        self.container.olay_hatti.publish(AppStarted(occurred_at=self.container.saat.simdi()))
        self.container.mentor.periyodik_kontrol()  # açılışta bir kez
        self.container.hatirlatma.kontrol()
        return self.qapp.exec()
