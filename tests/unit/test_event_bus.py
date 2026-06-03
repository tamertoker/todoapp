from dataclasses import dataclass
from datetime import datetime

from leveltodo.domain.events import AppStarted, DomainEvent
from leveltodo.infrastructure.eventbus.bus import EventBus


@dataclass(frozen=True, slots=True)
class _Other(DomainEvent):
    pass


def test_typed_subscriber_only_gets_its_type():
    bus = EventBus()
    received: list[DomainEvent] = []
    bus.subscribe(AppStarted, received.append)

    bus.publish(AppStarted(occurred_at=datetime(2026, 6, 2, 10, 0)))
    bus.publish(_Other(occurred_at=datetime(2026, 6, 2, 10, 0)))

    assert len(received) == 1
    assert isinstance(received[0], AppStarted)


def test_subscribe_all_gets_every_event():
    bus = EventBus()
    received: list[DomainEvent] = []
    bus.subscribe_all(received.append)

    bus.publish(AppStarted(occurred_at=datetime(2026, 6, 2, 10, 0)))
    bus.publish(_Other(occurred_at=datetime(2026, 6, 2, 10, 0)))

    assert len(received) == 2
