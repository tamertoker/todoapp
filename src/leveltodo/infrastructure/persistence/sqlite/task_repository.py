"""Görev şablonları ve görev kayıtları (instance) için veri deposu.

Okuma metotları, veritabanından çekilen kayıtları döndürür (yalnızca sütun
değerleri okunur, güvenli). Yazma metotları işi tek bir oturum içinde yapar:
kaydı bul, değiştir, kaydet.
"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import sessionmaker

from leveltodo.infrastructure.persistence.sqlite.models import Task, TaskInstance


class SqlTaskRepository:
    def __init__(self, session_factory: sessionmaker) -> None:
        self._sf = session_factory

    # — Şablonlar —
    def add_template(
        self, *, id: str, user_id: str, title: str, recurrence: str, reward_override: int | None
    ) -> None:
        with self._sf() as s:
            s.add(
                Task(
                    id=id,
                    user_id=user_id,
                    title=title,
                    recurrence=recurrence,
                    reward_override=reward_override,
                )
            )
            s.commit()

    def get_template(self, task_id: str) -> Task | None:
        with self._sf() as s:
            return s.get(Task, task_id)

    def deactivate_template(self, task_id: str) -> None:
        with self._sf() as s:
            task = s.get(Task, task_id)
            if task is not None:
                task.is_active = False
                s.commit()

    def active_daily_templates(self, user_id: str) -> list[Task]:
        with self._sf() as s:
            stmt = select(Task).where(
                Task.user_id == user_id,
                Task.recurrence == "daily",
                Task.is_active.is_(True),
            )
            return list(s.scalars(stmt))

    # — Kayıtlar (instance) —
    def add_instance(
        self, *, id: str, task_id: str, user_id: str, day: date, title: str
    ) -> None:
        with self._sf() as s:
            s.add(TaskInstance(id=id, task_id=task_id, user_id=user_id, day=day, title=title))
            s.commit()

    def instance_exists(self, task_id: str, day: date) -> bool:
        with self._sf() as s:
            stmt = select(TaskInstance.id).where(
                TaskInstance.task_id == task_id, TaskInstance.day == day
            )
            return s.scalar(stmt) is not None

    def get_instance(self, instance_id: str) -> TaskInstance | None:
        with self._sf() as s:
            return s.get(TaskInstance, instance_id)

    def today_rows(self, user_id: str, day: date) -> list[tuple[TaskInstance, str]]:
        """Bugünün listesi: her-gün görevlerinin bugünkü kaydı + henüz
        yapılmamış tek seferlik görevler. Her satır (kayıt, tekrar-tipi)."""
        with self._sf() as s:
            stmt = (
                select(TaskInstance, Task.recurrence)
                .join(Task, Task.id == TaskInstance.task_id)
                .where(
                    TaskInstance.user_id == user_id,
                    Task.is_active.is_(True),
                    or_(
                        and_(Task.recurrence == "daily", TaskInstance.day == day),
                        and_(Task.recurrence == "none", TaskInstance.status == "pending"),
                    ),
                )
                .order_by(TaskInstance.status.desc(), TaskInstance.title)
            )
            return [(inst, rec) for inst, rec in s.execute(stmt).all()]

    def complete_instance(
        self,
        *,
        instance_id: str,
        reward_xp: int,
        reward_points: int,
        completed_at: datetime,
    ) -> bool:
        """Kaydı 'yapıldı' işaretler. Zaten yapılmışsa False döner (çift ödül yok)."""
        with self._sf() as s:
            inst = s.get(TaskInstance, instance_id)
            if inst is None or inst.status == "done":
                return False
            inst.status = "done"
            inst.reward_xp = reward_xp
            inst.reward_points = reward_points
            inst.completed_at = completed_at
            inst.timer_running = False
            inst.segment_started_at = None
            s.commit()
            return True
