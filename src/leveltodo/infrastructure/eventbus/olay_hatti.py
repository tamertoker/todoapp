"""Domain olay hattı (OlayHatti).

"blinker" kütüphanesi üzerine ince bir sarmalayıcı. Olaylar buradan yayınlanır
(publish) ve dinleyiciler buraya abone olur (subscribe). İki tür abonelik:
- subscribe(OlayTuru, handler): yalnızca o türdeki olaylarda çağrılır.
- subscribe_all(handler): her olayda çağrılır (Qt köprüsü bunu kullanır).

Not: blinker varsayılan olarak dinleyicileri "zayıf referans"la tutar ve çöp
toplama (garbage collection) onları silebilir. Bunu engellemek için weak=False
kullanıyoruz, böylece bağladığımız fonksiyonlar yaşamaya devam eder.

"""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

import blinker

from leveltodo.domain.events import DomainEvent

E = TypeVar("E", bound=DomainEvent)


class OlayHatti:
    def __init__(self) -> None:
        self._signals: dict[type, blinker.Signal] = {}
        self._any = blinker.Signal()

    def subscribe(self, event_type: type[E], handler: Callable[[E], None]) -> None:
        sig = self._signals.setdefault(event_type, blinker.Signal())
        sig.connect(lambda sender, **_kw: handler(sender), weak=False)

    def subscribe_all(self, handler: Callable[[DomainEvent], None]) -> None:
        self._any.connect(lambda sender, **_kw: handler(sender), weak=False)

    def publish(self, event: DomainEvent) -> None:
        self._any.send(event)
        sig = self._signals.get(type(event))
        if sig is not None:
            sig.send(event)
