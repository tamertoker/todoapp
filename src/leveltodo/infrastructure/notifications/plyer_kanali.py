"""OS bildirim kanalı (plyer).

Windows'ta sistem bildirimi (toast) gösterir. Bildirim izni/altyapısı yoksa ya da
hata olursa SESSİZCE geçer — garantili kanal uygulama-içi toast olduğu için OS
bildirimi "best effort"tur.
"""

from __future__ import annotations

import logging

from leveltodo.domain.bildirim.bildirim import Bildirim

logger = logging.getLogger(__name__)


def plyer_kanali(bildirim: Bildirim) -> None:
    try:
        from plyer import notification

        notification.notify(
            title=bildirim.baslik,
            message=bildirim.govde,
            app_name="LevelTodo",
            timeout=5,
        )
        logger.info("OS bildirimi gonderildi: %s", bildirim.baslik)
    except Exception as hata:  # noqa: BLE001 - OS bildirimi best-effort; in-app toast garanti
        logger.warning("OS bildirimi gonderilemedi (in-app toast yine calisir): %r", hata)
