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
import sys
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


def assets_dir() -> Path:
    """gorsel ve ses dosyalarinin bulundugu klasor."""
    override = os.environ.get("LEVELTODO_ASSETS_DIR")
    if override:
        return Path(override)
    # PyInstaller ile paketlenince asset'ler gecici cikarim klasorune konur
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", ".")) / "assets"
    return Path(__file__).resolve().parents[4] / "assets"
