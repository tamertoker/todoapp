"""Veritabanı şema güncellemelerini (migration) programatik çalıştırma.

Alembic, veritabanı şemasını sürümleyen araçtır. Uygulama her açılışta
`upgrade_to_head` çağırır; bu, veritabanını en güncel şemaya getirir (eksik
tabloları oluşturur). Böylece kullanıcı elle komut çalıştırmak zorunda kalmaz.
"""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config


def _alembic_config(url: str) -> Config:
    here = Path(__file__).resolve().parent
    cfg = Config()
    cfg.set_main_option("script_location", str(here / "migrations"))
    cfg.set_main_option("sqlalchemy.url", url)
    return cfg


def upgrade_to_head(url: str) -> None:
    command.upgrade(_alembic_config(url), "head")
