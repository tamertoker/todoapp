from dataclasses import dataclass
from datetime import datetime

from leveltodo.domain.events import AppStarted, DomainEvent
from leveltodo.infrastructure.eventbus.olay_hatti import OlayHatti


@dataclass(frozen=True, slots=True)
class _Other(DomainEvent):
    pass


def test_typed_subscriber_only_gets_its_type():
    hat = OlayHatti()
    received: list[DomainEvent] = []
    hat.subscribe(AppStarted, received.append)

    hat.publish(AppStarted(occurred_at=datetime(2026, 6, 2, 10, 0)))
    hat.publish(_Other(occurred_at=datetime(2026, 6, 2, 10, 0)))

    assert len(received) == 1
    assert isinstance(received[0], AppStarted)


def test_subscribe_all_gets_every_event():
    hat = OlayHatti()
    received: list[DomainEvent] = []
    hat.subscribe_all(received.append)

    hat.publish(AppStarted(occurred_at=datetime(2026, 6, 2, 10, 0)))
    hat.publish(_Other(occurred_at=datetime(2026, 6, 2, 10, 0)))

    assert len(received) == 2
