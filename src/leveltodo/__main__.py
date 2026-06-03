"""Giriş noktası: `python -m leveltodo` ya da `leveltodo` komutu.

Sıra: günlük kur → container'ı inşa et (veritabanı + migration + ayarlar) →
Qt uygulamasını başlat.
"""

from __future__ import annotations

from leveltodo.bootstrap import build_container
from leveltodo.infrastructure.config import paths
from leveltodo.presentation.app import LevelTodoApp
from leveltodo.shared.logging import setup_logging


def main() -> int:
    setup_logging(log_file=paths.logs_dir() / "leveltodo.log")
    container = build_container()
    app = LevelTodoApp(container)
    return app.run()


if __name__ == "__main__":
    raise SystemExit(main())
