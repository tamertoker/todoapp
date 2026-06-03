"""Dashboard'un ViewModel'i.

Ekran ile görev servisi arasındaki aracı. Görev ekleme/bitirme/silme
isteklerini servise iletir ve "veri değişti" sinyali yayar; ekran bu sinyali
duyup listeyi yeniden çizer.
"""

from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal

from leveltodo.application.task_service import TaskRow, TaskService
from leveltodo.domain.tasks.rules import Recurrence


class DashboardViewModel(QObject):
    changed = pyqtSignal()

    def __init__(self, tasks: TaskService) -> None:
        super().__init__()
        self._tasks = tasks

    def rows(self) -> list[TaskRow]:
        return self._tasks.list_today()

    def totals(self) -> tuple[int, int]:
        return self._tasks.totals()

    def add_task(self, title: str, recurrence: Recurrence, override: int | None) -> None:
        self._tasks.create_task(title, recurrence, override)
        self.changed.emit()

    def complete(self, instance_id: str) -> None:
        self._tasks.complete(instance_id)
        self.changed.emit()

    def delete(self, instance_id: str) -> None:
        self._tasks.delete_task(instance_id)
        self.changed.emit()
