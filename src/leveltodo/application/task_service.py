"""Görev servisi — çekirdek döngünün beyni.

Görev ekleme, bugünün listesini hazırlama ve görevi tamamlayıp ödül yazma
işlerini yönetir. Saat ve "gün başlangıcı" ayarını kullanarak hangi mantıksal
günde olduğumuzu bilir; her-gün görevlerinin bugünkü kaydını tembelce (lazy)
üretir.
"""

from __future__ import annotations

from dataclasses import dataclass

from leveltodo.domain.events import TaskCompleted
from leveltodo.domain.tasks.rules import Recurrence, Reward, compute_reward
from leveltodo.domain.time.clock import IClock
from leveltodo.domain.time.day import DayId
from leveltodo.infrastructure.eventbus.bus import EventBus
from leveltodo.infrastructure.persistence.sqlite.ledger_repository import SqlLedgerRepository
from leveltodo.infrastructure.persistence.sqlite.models import DEFAULT_USER_ID
from leveltodo.infrastructure.persistence.sqlite.task_repository import SqlTaskRepository
from leveltodo.shared.ids import new_id

_COMPLETION_SOURCE = "task_completion"


@dataclass(frozen=True, slots=True)
class TaskRow:
    """Ekranın bir görev satırını çizmek için ihtiyaç duyduğu sade veri."""

    instance_id: str
    title: str
    status: str
    recurrence: str
    committed_seconds: int
    reward_xp: int | None
    reward_points: int | None


class TaskService:
    def __init__(
        self,
        tasks: SqlTaskRepository,
        ledger: SqlLedgerRepository,
        clock: IClock,
        event_bus: EventBus,
        day_start_hour_getter,
        user_id: str = DEFAULT_USER_ID,
    ) -> None:
        self._tasks = tasks
        self._ledger = ledger
        self._clock = clock
        self._bus = event_bus
        self._day_start_hour = day_start_hour_getter
        self._user_id = user_id

    def _today(self):
        return DayId.of(self._clock.now(), self._day_start_hour()).value

    def create_task(
        self, title: str, recurrence: Recurrence, reward_override: int | None = None
    ) -> str:
        task_id = new_id()
        self._tasks.add_template(
            id=task_id,
            user_id=self._user_id,
            title=title.strip(),
            recurrence=recurrence.value,
            reward_override=reward_override,
        )
        if recurrence is Recurrence.NONE:
            self._tasks.add_instance(
                id=new_id(),
                task_id=task_id,
                user_id=self._user_id,
                day=self._today(),
                title=title.strip(),
            )
        return task_id

    def list_today(self) -> list[TaskRow]:
        day = self._today()
        self._ensure_daily_instances(day)
        rows = self._tasks.today_rows(self._user_id, day)
        return [
            TaskRow(
                instance_id=inst.id,
                title=inst.title,
                status=inst.status,
                recurrence=recurrence,
                committed_seconds=inst.committed_seconds,
                reward_xp=inst.reward_xp,
                reward_points=inst.reward_points,
            )
            for inst, recurrence in rows
        ]

    def _ensure_daily_instances(self, day) -> None:
        for template in self._tasks.active_daily_templates(self._user_id):
            if not self._tasks.instance_exists(template.id, day):
                self._tasks.add_instance(
                    id=new_id(),
                    task_id=template.id,
                    user_id=self._user_id,
                    day=day,
                    title=template.title,
                )

    def complete(self, instance_id: str) -> Reward | None:
        instance = self._tasks.get_instance(instance_id)
        if instance is None:
            return None
        template = self._tasks.get_template(instance.task_id)
        override = template.reward_override if template is not None else None

        reward = compute_reward(instance.committed_seconds, override)
        now = self._clock.now()
        ok = self._tasks.complete_instance(
            instance_id=instance_id,
            reward_xp=reward.xp,
            reward_points=reward.points,
            completed_at=now,
        )
        if not ok:
            return None

        self._ledger.record(
            user_id=self._user_id,
            day=self._today(),
            source=_COMPLETION_SOURCE,
            ref_id=instance_id,
            xp=reward.xp,
            points=reward.points,
        )
        self._bus.publish(
            TaskCompleted(
                occurred_at=now,
                instance_id=instance_id,
                xp=reward.xp,
                points=reward.points,
            )
        )
        return reward

    def delete_task(self, instance_id: str) -> None:
        instance = self._tasks.get_instance(instance_id)
        if instance is not None:
            self._tasks.deactivate_template(instance.task_id)

    def totals(self) -> tuple[int, int]:
        return self._ledger.totals(self._user_id)
