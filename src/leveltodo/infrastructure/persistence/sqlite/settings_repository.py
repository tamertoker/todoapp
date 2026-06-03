"""Ayar deposunun SQLite implementasyonu.

domain/settings/repository.py'deki ISettingsRepository sözleşmesini yerine
getirir: ayarları okur ve yazar. "upsert" = varsa güncelle, yoksa ekle.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from leveltodo.infrastructure.persistence.sqlite.models import Setting


class SqlSettingsRepository:
    def __init__(self, session_factory: sessionmaker) -> None:
        self._session_factory = session_factory

    def get_all(self, user_id: str) -> dict[str, str]:
        with self._session_factory() as session:
            rows = session.scalars(
                select(Setting).where(Setting.user_id == user_id)
            ).all()
            return {row.key: row.value for row in rows}

    def upsert(self, user_id: str, key: str, raw_value: str) -> None:
        with self._session_factory() as session:
            existing = session.scalar(
                select(Setting).where(Setting.user_id == user_id, Setting.key == key)
            )
            if existing is None:
                session.add(Setting(user_id=user_id, key=key, value=raw_value))
            else:
                existing.value = raw_value
            session.commit()
