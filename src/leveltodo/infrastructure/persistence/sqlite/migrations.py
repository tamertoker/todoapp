"""Veritabanı şema güncellemelerini (migration) programatik çalıştırma.

Alembic, veritabanı şemasını sürümleyen araçtır. Uygulama her açılışta
`upgrade_to_head` çağırır; bu, veritabanını en güncel şemaya getirir (eksik
tabloları oluşturur). Böylece kullanıcı elle komut çalıştırmak zorunda kalmaz.
"""

from __future__ import annotations

import sys
from pathlib import Path

from alembic import command
from alembic.config import Config


def _alembic_config(url: str) -> Config:
    # paketlenmis (PyInstaller) halde migration klasoru cikarim dizinine konur
    if getattr(sys, "frozen", False):
        script_location = Path(getattr(sys, "_MEIPASS", ".")) / "migrations"
    else:
        script_location = Path(__file__).resolve().parent / "migrations"
    cfg = Config()
    cfg.set_main_option("script_location", str(script_location))
    cfg.set_main_option("sqlalchemy.url", url)
    return cfg


def upgrade_to_head(url: str) -> None:
    command.upgrade(_alembic_config(url), "head")
