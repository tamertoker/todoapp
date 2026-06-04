"""Veritabanı tabloları (Faz 0).

İki tablo:
- users: Kişiler. Şimdilik tek bir varsayılan kullanıcı var, ama tüm tablolar
  baştan user_id taşır; ileride çoklu profil eklemek kolay olsun diye.
- settings: Kullanıcı ayarları. "anahtar = değer" biçiminde tutulur (değer JSON
  metni olarak saklanır). Yeni bir ayar eklemek için tabloyu değiştirmek
  gerekmez — sadece yeni bir anahtar yazılır.
"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
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


class Task(Base):
    """Görev şablonu. Tek seferlik ya da her gün tekrar eden bir görevin tanımı.
    Asıl 'yapılacak' kayıtları (TaskInstance) bundan üretilir."""

    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200))
    recurrence: Mapped[str] = mapped_column(String(10))  # none|daily|every_x|weekly|monthly
    recurrence_param: Mapped[str | None] = mapped_column(String(60), nullable=True)
    reward_override: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stat: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class TaskInstance(Base):
    """Bir görevin belirli bir güne düşen somut kaydı. Kronometre süresi, durum
    ve kazanılan ödül burada yaşar; geçmiş bozulmaz."""

    __tablename__ = "task_instances"
    __table_args__ = (UniqueConstraint("task_id", "day", name="uq_instance_task_day"),)

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    day: Mapped[date] = mapped_column(Date)
    title: Mapped[str] = mapped_column(String(200))  # o anki başlık (anlık görüntü)
    status: Mapped[str] = mapped_column(String(10), default="pending")

    committed_seconds: Mapped[int] = mapped_column(Integer, default=0)
    timer_running: Mapped[bool] = mapped_column(Boolean, default=False)
    segment_started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    reward_xp: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reward_points: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class XpEvent(Base):
    """Kazanılan her XP'nin kaydı (denetim/grafik için kaynak)."""

    __tablename__ = "xp_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    day: Mapped[date] = mapped_column(Date)
    source: Mapped[str] = mapped_column(String(40))
    ref_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    amount: Mapped[int] = mapped_column(Integer)
    stat: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Streak(Base):
    """Seri (streak) kaydı. type='login' giriş serisi, type='task' görev serisi.
    Kullanıcı + tip başına tek satır."""

    __tablename__ = "streaks"
    __table_args__ = (UniqueConstraint("user_id", "type", name="uq_streak_user_type"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(10))
    current_count: Mapped[int] = mapped_column(Integer, default=0)
    best_count: Mapped[int] = mapped_column(Integer, default=0)
    last_day: Mapped[date | None] = mapped_column(Date, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class PointTransaction(Base):
    """Kazanılan/harcanan her puanın kaydı."""

    __tablename__ = "point_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    day: Mapped[date] = mapped_column(Date)
    source: Mapped[str] = mapped_column(String(40))
    ref_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    amount: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
