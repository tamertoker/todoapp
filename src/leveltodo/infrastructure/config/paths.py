"""Uygulama dosya yolları.

Veritabanı ve günlükler, kullanıcının kişisel uygulama-veri klasörüne yazılır
(Windows'ta %LOCALAPPDATA%\\leveltodo). Roaming yerine Local kullanılır; çünkü
SQLite veritabanı ağ profili üzerinden senkronlanırsa kilitlenme/bozulma riski
doğar.

Testler ve geliştirme için LEVELTODO_DATA_DIR ortam değişkeni ile bu konum
geçici bir klasöre yönlendirilebilir; böylece gerçek verilere dokunulmaz.
"""

from __future__ import annotations

import os
from pathlib import Path

from platformdirs import user_data_dir

APP_NAME = "leveltodo"


def data_dir() -> Path:
    override = os.environ.get("LEVELTODO_DATA_DIR")
    base = Path(override) if override else Path(user_data_dir(APP_NAME, appauthor=False))
    base.mkdir(parents=True, exist_ok=True)
    return base


def db_path() -> Path:
    return data_dir() / "leveltodo.db"


def db_url() -> str:
    return f"sqlite:///{db_path()}"


def logs_dir() -> Path:
    d = data_dir() / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d
