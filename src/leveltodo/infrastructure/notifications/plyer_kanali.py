"""OS bildirim kanalı (plyer).

Windows'ta sistem bildirimi (toast) gösterir. Bildirim izni/altyapısı yoksa ya da
hata olursa SESSİZCE geçer — garantili kanal uygulama-içi toast olduğu için OS
bildirimi "best effort"tur.
"""

from __future__ import annotations

from leveltodo.domain.bildirim.bildirim import Bildirim


def plyer_kanali(bildirim: Bildirim) -> None:
    try:
        from plyer import notification

        notification.notify(
            title=bildirim.baslik,
            message=bildirim.govde,
            app_name="LevelTodo",
            timeout=5,
        )
    except Exception:  # noqa: BLE001 - OS bildirimi best-effort; in-app toast garanti
        pass
