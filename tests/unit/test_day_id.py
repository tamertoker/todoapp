from datetime import datetime

from leveltodo.domain.time.day import DayId


def test_before_day_start_counts_as_previous_day():
    # Gün başlangıcı 04:00; saat 03:30 → hâlâ dünkü gün.
    moment = datetime(2026, 6, 2, 3, 30)
    assert DayId.of(moment, day_start_hour=4).value == datetime(2026, 6, 1).date()


def test_after_day_start_counts_as_same_day():
    moment = datetime(2026, 6, 2, 4, 30)
    assert DayId.of(moment, day_start_hour=4).value == datetime(2026, 6, 2).date()


def test_exact_day_start_is_new_day():
    moment = datetime(2026, 6, 2, 4, 0)
    assert DayId.of(moment, day_start_hour=4).value == datetime(2026, 6, 2).date()


def test_midnight_with_zero_start_is_same_day():
    moment = datetime(2026, 6, 2, 0, 0)
    assert DayId.of(moment, day_start_hour=0).value == datetime(2026, 6, 2).date()


def test_invalid_hour_raises():
    import pytest

    with pytest.raises(ValueError):
        DayId.of(datetime(2026, 6, 2, 12, 0), day_start_hour=24)
