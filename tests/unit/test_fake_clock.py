from datetime import datetime

from leveltodo.infrastructure.clock import FakeClock


def test_fake_clock_returns_set_time():
    clock = FakeClock(datetime(2026, 6, 2, 9, 0))
    assert clock.now() == datetime(2026, 6, 2, 9, 0)


def test_fake_clock_advances():
    clock = FakeClock(datetime(2026, 6, 2, 9, 0))
    clock.advance(days=1, hours=2)
    assert clock.now() == datetime(2026, 6, 3, 11, 0)


def test_fake_clock_set():
    clock = FakeClock(datetime(2026, 6, 2, 9, 0))
    clock.set(datetime(2026, 12, 31, 23, 59))
    assert clock.now() == datetime(2026, 12, 31, 23, 59)
