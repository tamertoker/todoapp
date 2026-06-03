"""Çekirdek döngünün uçtan uca testi (kronometresiz):
ekle → listele → bitir → ödül → toplamlar → günlük tekrar → kalıcılık."""

from datetime import datetime

from leveltodo.bootstrap import build_container
from leveltodo.domain.tasks.rules import Recurrence
from leveltodo.infrastructure.clock import FakeClock


def _container(db_url, clock):
    return build_container(db_url=db_url, clock=clock)


def test_full_loop(db_url):
    clock = FakeClock(datetime(2026, 6, 3, 10, 0))
    svc = _container(db_url, clock).tasks

    svc.create_task("Kitap oku", Recurrence.DAILY)
    svc.create_task("Faturayı öde", Recurrence.NONE, reward_override=20)

    rows = svc.list_today()
    assert len(rows) == 2

    onetime = next(r for r in rows if r.recurrence == "none")
    reward = svc.complete(onetime.instance_id)
    assert reward is not None and reward.xp == 20 and reward.points == 20
    assert svc.totals() == (20, 20)

    # Tek seferlik görev bitince listeden düşer.
    titles_after = [r.title for r in svc.list_today()]
    assert "Faturayı öde" not in titles_after

    # Her-gün görevi hâlâ bekliyor; bitir (kronometresiz → sabit 5).
    daily = next(r for r in svc.list_today() if r.recurrence == "daily")
    assert svc.complete(daily.instance_id).xp == 5
    assert svc.totals() == (25, 25)

    # Ertesi mantıksal günde her-gün görevi yeniden bekliyor olarak gelir.
    clock.advance(days=1)
    rows_tomorrow = svc.list_today()
    assert any(r.recurrence == "daily" and r.status == "pending" for r in rows_tomorrow)
    # Toplamlar korunur.
    assert svc.totals() == (25, 25)


def test_completing_twice_does_not_double_reward(db_url):
    clock = FakeClock(datetime(2026, 6, 3, 10, 0))
    svc = _container(db_url, clock).tasks

    svc.create_task("Tek iş", Recurrence.NONE)
    row = svc.list_today()[0]

    assert svc.complete(row.instance_id) is not None
    assert svc.complete(row.instance_id) is None  # ikinci kez ödül yok
    assert svc.totals() == (5, 5)


def test_data_persists_across_restart(db_url):
    clock = FakeClock(datetime(2026, 6, 3, 10, 0))
    svc = _container(db_url, clock).tasks
    svc.create_task("Kalıcı görev", Recurrence.DAILY)
    svc.complete(svc.list_today()[0].instance_id)

    # Aynı veritabanıyla yeni container (uygulamayı kapatıp açmak gibi).
    svc2 = _container(db_url, clock).tasks
    assert svc2.totals() == (5, 5)
