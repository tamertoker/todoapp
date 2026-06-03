from leveltodo.bootstrap import build_container
from leveltodo.domain.events import AppStarted
from leveltodo.domain.tasks.kurallar import Tekrar
from leveltodo.presentation.app import LevelTodoApp


def test_app_constructs_and_handles_started_event(db_url, qapp):
    container = build_container(db_url=db_url)
    app = LevelTodoApp(container)

    container.olay_hatti.publish(AppStarted(occurred_at=container.saat.simdi()))

    assert "döndün" in app.window._dashboard._status_label.text()


def test_theme_toggle_changes_stylesheet(db_url, qapp):
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

    dashboard._vm.gorev_ekle("Test görevi", Tekrar.YOK, None)
    satirlar = container.gorevler.bugunku_gorevler()
    assert len(satirlar) == 1

    dashboard._vm.tamamla(satirlar[0].kayit_id)
    assert container.gorevler.toplamlar() == (5, 5)
    assert "5" in dashboard._xp_label.text()


def test_add_task_dialog_blocks_empty_title(qapp):
    from PyQt6.QtWidgets import QDialog

    from leveltodo.presentation.views.dashboard.add_task_dialog import AddTaskDialog

    dialog = AddTaskDialog()
    dialog.accept()  # boş başlık → kabul edilmemeli
    assert dialog.result() != QDialog.DialogCode.Accepted
    assert dialog._warning.isVisibleTo(dialog)

    dialog._title.setText("Bir görev")
    dialog.accept()  # başlık dolu → kabul edilir
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_add_task_dialog_esnek_tekrar(qapp):
    from leveltodo.presentation.views.dashboard.add_task_dialog import AddTaskDialog

    dialog = AddTaskDialog()
    dialog._title.setText("Her 5 günde")
    dialog._tekrar.setCurrentIndex(2)  # "Her X günde bir"
    dialog._x_spin.setValue(5)

    baslik, tekrar, parametre, _ozel, _stat = dialog.result_values()
    assert baslik == "Her 5 günde"
    assert tekrar is Tekrar.HER_X_GUN
    assert parametre == "5"
