"""GUI smoke testi (başsız/offscreen).

Gerçek pencereyi açmadan, uygulamanın çökmeden kurulduğunu ve açılış olayının
(AppStarted) dashboard'a ulaştığını doğrular. run() çağrılmaz çünkü o, olay
döngüsünü başlatıp bloklar; bunun yerine olayı elle yayınlarız.
"""

from leveltodo.bootstrap import build_container
from leveltodo.domain.events import AppStarted
from leveltodo.domain.tasks.rules import Recurrence
from leveltodo.presentation.app import LevelTodoApp


def test_app_constructs_and_handles_started_event(db_url, qapp):
    container = build_container(db_url=db_url)
    app = LevelTodoApp(container)

    container.event_bus.publish(AppStarted(occurred_at=container.clock.now()))

    assert "döndün" in app.window._dashboard._status_label.text()


def test_theme_switch_applies_stylesheet(db_url, qapp):
    container = build_container(db_url=db_url)
    app = LevelTodoApp(container)

    app._apply_theme("light")
    assert qapp.styleSheet()  # boş değil
    app._apply_theme("dark")
    assert qapp.styleSheet()


def test_dashboard_task_flow_updates_counter(db_url, qapp):
    container = build_container(db_url=db_url)
    app = LevelTodoApp(container)
    dashboard = app.window._dashboard

    dashboard._vm.add_task("Test görevi", Recurrence.NONE, None)
    rows = container.tasks.list_today()
    assert len(rows) == 1

    dashboard._vm.complete(rows[0].instance_id)
    assert container.tasks.totals() == (5, 5)
    assert "5" in dashboard._xp_label.text()
