
from __future__ import annotations

from leveltodo.bootstrap import build_container
from leveltodo.infrastructure.config import paths
from leveltodo.presentation.app import LevelTodoApp
from leveltodo.shared.logging import setup_logging


def main() -> int:
    # Hataları görmek için burada log dosyasını oluşturuyoruz.
    setup_logging(log_file=paths.logs_dir() / "leveltodo.log")
    # Servis konteynırı. İhtiyaç duyulan servisler buradan çağrılır.
    container = build_container()
    app = LevelTodoApp(container)
    return app.run()


if __name__ == "__main__":
    raise SystemExit(main())
