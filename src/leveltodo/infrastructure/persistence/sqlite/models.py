"""Veritabanı tabloları (Faz 0).

İki tablo:
- users: Kişiler. Şimdilik tek bir varsayılan kullanıcı var, ama tüm tablolar
  baştan user_id taşır; ileride çoklu profil eklemek kolay olsun diye.
- settings: Kullanıcı ayarları. "anahtar = değer" biçiminde tutulur (değer JSON
  metni olarak saklanır). Yeni bir ayar eklemek için tabloyu değiştirmek
  gerekmez — sadece yeni bir anahtar yazılır.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from leveltodo.infrastructure.persistence.sqlite.base import Base

# Tek kullanıcılı sürümde sabit kullanıcı kimliği (çoklu profil Faz V2).
DEFAULT_USER_ID = "default"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), default="Oyuncu")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Setting(Base):
    __tablename__ = "settings"
    __table_args__ = (UniqueConstraint("user_id", "key", name="uq_settings_user_key"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    key: Mapped[str] = mapped_column(String(80))
    value: Mapped[str] = mapped_column(String)  # JSON metni
