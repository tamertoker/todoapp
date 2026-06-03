"""Domain olaylarını Qt arayüzüne taşıyan köprü.

Domain tarafı saf Python'dur ve PyQt'yi bilmez. Ama bir olay olduğunda
arayüzün (ekranın) güncellenmesi gerekir. Bu köprü, veriyolundaki her olayı
yakalayıp bir Qt sinyaline (`domain_event`) çevirir. Qt, sinyali güvenli
şekilde ana arayüz iş parçacığına (thread) taşır; böylece olay başka bir
thread'de doğmuş olsa bile ekran güncellemesi doğru yerde çalışır.
"""

from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal

from leveltodo.domain.events import DomainEvent
from leveltodo.infrastructure.eventbus.olay_hatti import OlayHatti


class QtEventBridge(QObject):
    domain_event = pyqtSignal(object)

    def __init__(self, olay_hatti: OlayHatti, parent: QObject | None = None) -> None:
        super().__init__(parent)
        olay_hatti.subscribe_all(self._forward)

    def _forward(self, event: DomainEvent) -> None:
        self.domain_event.emit(event)
