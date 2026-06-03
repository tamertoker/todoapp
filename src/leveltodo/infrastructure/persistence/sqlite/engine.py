"""Veritabanı motoru ve oturum üreticisi.

- create_engine: veritabanı dosyasına bağlanır.
- sessionmaker: her veritabanı işlemi için bir "oturum" (session) üretir.
- SQLite'ta foreign key (tablolar arası bağ) kuralları varsayılan olarak
  KAPALIDIR; her bağlantıda PRAGMA ile açıyoruz ki bağ kuralları işlesin.
"""

from __future__ import annotations

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import sessionmaker


def create_engine_and_factory(url: str) -> tuple[Engine, sessionmaker]:
    engine = create_engine(url, future=True)

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_connection, _record):  # noqa: ANN001
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    factory = sessionmaker(engine, expire_on_commit=False, future=True)
    return engine, factory
