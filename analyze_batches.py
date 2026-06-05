import ast
import json
import os

def analyze_file(file_path):
    if not os.path.exists(file_path):
        return [], []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return [], []

    nodes = []
    edges = []

    # File node
    file_id = f"file:{file_path}"
    nodes.append({
        "id": file_id,
        "label": os.path.basename(file_path),
        "type": "file",
        "layer": get_layer(file_path),
        "summary": f"{file_path} dosyası."
    })

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append(f"{module}.{alias.name}")

    for imp in imports:
        # We don't know the exact file for imports easily without more logic, 
        # but we can create placeholder edges or nodes if needed.
        pass

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_id = f"class:{file_path}:{node.name}"
            nodes.append({
                "id": class_id,
                "label": node.name,
                "type": "class",
                "layer": get_layer(file_path),
                "summary": f"{node.name} sınıfı."
            })
            edges.append({
                "source": class_id,
                "target": file_id,
                "type": "defined_in"
            })
            
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    func_id = f"function:{file_path}:{node.name}.{item.name}"
                    nodes.append({
                        "id": func_id,
                        "label": item.name,
                        "type": "function",
                        "layer": get_layer(file_path),
                        "summary": f"{node.name} sınıfı içinde {item.name} metodu."
                    })
                    edges.append({
                        "source": func_id,
                        "target": class_id,
                        "type": "member_of"
                    })
        
        elif isinstance(node, ast.FunctionDef):
            func_id = f"function:{file_path}:{node.name}"
            nodes.append({
                "id": func_id,
                "label": node.name,
                "type": "function",
                "layer": get_layer(file_path),
                "summary": f"{node.name} fonksiyonu."
            })
            edges.append({
                "source": func_id,
                "target": file_id,
                "type": "defined_in"
            })

    return nodes, edges

def get_layer(path):
    if "domain" in path: return "Domain"
    if "application" in path: return "Application"
    if "infrastructure" in path: return "Infrastructure"
    if "presentation" in path: return "Presentation"
    if "tests" in path: return "Test"
    return "Shared"

def process_batch(batch_idx, files):
    all_nodes = []
    all_edges = []
    for f in files:
        nodes, edges = analyze_file(f)
        all_nodes.extend(nodes)
        all_edges.extend(edges)
    
    # Try to find calls between functions/classes
    # This is complex with just AST, but we can do basic name matching
    
    output = {
        "batchIndex": batch_idx,
        "nodes": all_nodes,
        "edges": all_edges
    }
    
    os.makedirs(".understand-anything/intermediate", exist_ok=True)
    with open(f".understand-anything/intermediate/batch-{batch_idx}.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    batches = {
        "36": ["gemini-code-1780678002928.py", "generate_scan_result.py", "src/leveltodo/__init__.py", "src/leveltodo/__main__.py", "src/leveltodo/application/__init__.py", "src/leveltodo/application/bildirim_servisi.py", "src/leveltodo/application/combo_servisi.py", "src/leveltodo/application/dondurma_servisi.py", "src/leveltodo/application/dusman_servisi.py", "src/leveltodo/application/gorev_servisi.py", "src/leveltodo/application/gunluk_servisi.py", "src/leveltodo/application/irade_servisi.py", "src/leveltodo/application/kronometre_servisi.py", "src/leveltodo/application/mentor_servisi.py", "src/leveltodo/application/rozet_servisi.py", "src/leveltodo/application/rutin_servisi.py", "src/leveltodo/application/seri_servisi.py", "src/leveltodo/application/settings_service.py", "src/leveltodo/application/uyandirma_servisi.py"],
        "37": ["src/leveltodo/bootstrap.py", "src/leveltodo/domain/__init__.py", "src/leveltodo/domain/bildirim/__init__.py", "src/leveltodo/domain/bildirim/bildirim.py", "src/leveltodo/domain/dusman/__init__.py", "src/leveltodo/domain/dusman/dusman.py", "src/leveltodo/domain/events.py", "src/leveltodo/domain/gunluk/__init__.py", "src/leveltodo/domain/gunluk/gunluk.py", "src/leveltodo/domain/mentor/__init__.py", "src/leveltodo/domain/mentor/mesajlar.py", "src/leveltodo/domain/rozetler/__init__.py", "src/leveltodo/domain/rozetler/rozetler.py", "src/leveltodo/domain/rutinler/__init__.py", "src/leveltodo/domain/rutinler/rutinler.py", "src/leveltodo/domain/sans.py", "src/leveltodo/domain/settings/__init__.py", "src/leveltodo/domain/settings/repository.py", "src/leveltodo/domain/stats/__init__.py", "src/leveltodo/domain/stats/statlar.py", "src/leveltodo/domain/streaks/__init__.py", "src/leveltodo/domain/streaks/seriler.py", "src/leveltodo/domain/tasks/__init__.py", "src/leveltodo/domain/tasks/kurallar.py", "src/leveltodo/domain/tasks/rules.py"],
        "38": ["src/leveltodo/domain/time/__init__.py", "src/leveltodo/domain/time/gun.py", "src/leveltodo/domain/time/saat.py", "src/leveltodo/domain/uyandirma/__init__.py", "src/leveltodo/domain/uyandirma/uyandirma.py", "src/leveltodo/infrastructure/__init__.py", "src/leveltodo/infrastructure/assets/__init__.py", "src/leveltodo/infrastructure/assets/avatar.py", "src/leveltodo/infrastructure/assets/dusman.py", "src/leveltodo/infrastructure/backup/__init__.py", "src/leveltodo/infrastructure/backup/yedekleme.py", "src/leveltodo/infrastructure/config/__init__.py", "src/leveltodo/infrastructure/config/paths.py", "src/leveltodo/infrastructure/eventbus/__init__.py", "src/leveltodo/infrastructure/eventbus/olay_hatti.py", "src/leveltodo/infrastructure/eventbus/qt_bridge.py", "src/leveltodo/infrastructure/notifications/__init__.py", "src/leveltodo/infrastructure/notifications/plyer_kanali.py", "src/leveltodo/infrastructure/persistence/__init__.py", "src/leveltodo/infrastructure/persistence/sqlite/__init__.py", "src/leveltodo/infrastructure/persistence/sqlite/base.py", "src/leveltodo/infrastructure/persistence/sqlite/bootstrap_data.py", "src/leveltodo/infrastructure/persistence/sqlite/engine.py", "src/leveltodo/infrastructure/persistence/sqlite/gunluk_repository.py", "src/leveltodo/infrastructure/persistence/sqlite/irade_repository.py"],
        "39": ["src/leveltodo/infrastructure/persistence/sqlite/ledger_repository.py", "src/leveltodo/infrastructure/persistence/sqlite/migrations.py", "src/leveltodo/infrastructure/persistence/sqlite/migrations/env.py", "src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/0001_initial.py", "src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/0002_tasks.py", "src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/0003_stats.py", "src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/0004_recurrence_param.py", "src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/0005_streaks.py", "src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/0006_task_streak.py", "src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/0007_will_acts.py", "src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/0008_routines.py", "src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/0009_journal.py", "src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/0010_routine_text.py", "src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/0011_wake.py", "src/leveltodo/infrastructure/persistence/sqlite/models.py", "src/leveltodo/infrastructure/persistence/sqlite/rutin_repository.py", "src/leveltodo/infrastructure/persistence/sqlite/settings_repository.py", "src/leveltodo/infrastructure/persistence/sqlite/streak_repository.py", "src/leveltodo/infrastructure/persistence/sqlite/task_repository.py", "src/leveltodo/infrastructure/persistence/sqlite/uyandirma_repository.py", "src/leveltodo/infrastructure/saat.py", "src/leveltodo/infrastructure/sans.py", "src/leveltodo/infrastructure/sound/__init__.py", "src/leveltodo/infrastructure/sound/secim.py"],
        "40": ["src/leveltodo/infrastructure/sound/ses_motoru.py", "src/leveltodo/presentation/__init__.py", "src/leveltodo/presentation/app.py", "src/leveltodo/presentation/common/__init__.py", "src/leveltodo/presentation/common/icon.py", "src/leveltodo/presentation/common/toast.py", "src/leveltodo/presentation/main_window.py", "src/leveltodo/presentation/mesajlar.py", "src/leveltodo/presentation/theme/__init__.py", "src/leveltodo/presentation/theme/arrows.py", "src/leveltodo/presentation/theme/fonts.py", "src/leveltodo/presentation/theme/palette.py", "src/leveltodo/presentation/theme/qss.py", "src/leveltodo/presentation/views/__init__.py", "src/leveltodo/presentation/views/admin/__init__.py", "src/leveltodo/presentation/views/admin/admin_view.py", "src/leveltodo/presentation/views/avatar/__init__.py", "src/leveltodo/presentation/views/avatar/avatar_view.py", "src/leveltodo/presentation/views/dashboard/__init__.py", "src/leveltodo/presentation/views/dashboard/add_task_dialog.py", "src/leveltodo/presentation/views/dashboard/bitir_dialog.py", "src/leveltodo/presentation/views/dashboard/dashboard_view.py", "src/leveltodo/presentation/views/dashboard/dashboard_viewmodel.py", "src/leveltodo/presentation/views/dashboard/gorev_satir_widget.py", "src/leveltodo/presentation/views/gunluk/__init__.py"],
        "41": ["src/leveltodo/presentation/views/gunluk/gunluk_view.py", "src/leveltodo/presentation/views/irade/__init__.py", "src/leveltodo/presentation/views/irade/irade_view.py", "src/leveltodo/presentation/views/rozetler/__init__.py", "src/leveltodo/presentation/views/rozetler/rozet_view.py", "src/leveltodo/presentation/views/rutin/__init__.py", "src/leveltodo/presentation/views/rutin/rutin_view.py", "src/leveltodo/presentation/views/settings/__init__.py", "src/leveltodo/presentation/views/settings/settings_view.py", "src/leveltodo/presentation/views/settings/settings_viewmodel.py", "src/leveltodo/presentation/views/telafi/__init__.py", "src/leveltodo/presentation/views/telafi/telafi_view.py", "src/leveltodo/shared/__init__.py", "src/leveltodo/shared/ids.py", "src/leveltodo/shared/logging.py", "src/leveltodo/shared/result.py", "tests/conftest.py", "tests/integration/test_backup.py", "tests/integration/test_bildirim.py", "tests/integration/test_combo.py", "tests/integration/test_dondurma.py", "tests/integration/test_dusman.py", "tests/integration/test_gunluk.py", "tests/integration/test_irade.py", "tests/integration/test_kritik.py"],
        "42": ["tests/integration/test_mentor.py", "tests/integration/test_migrations.py", "tests/integration/test_recurrence.py", "tests/integration/test_rozet.py", "tests/integration/test_rutin.py", "tests/integration/test_ses.py", "tests/integration/test_settings_persistence.py", "tests/integration/test_stats_loop.py", "tests/integration/test_streaks.py", "tests/integration/test_task_loop.py", "tests/integration/test_telafi.py", "tests/integration/test_timer.py", "tests/integration/test_uyandirma.py", "tests/smoke/test_app_smoke.py", "tests/unit/test_avatar.py", "tests/unit/test_day_id.py", "tests/unit/test_event_bus.py", "tests/unit/test_fake_clock.py", "tests/unit/test_mesajlar.py", "tests/unit/test_palette.py", "tests/unit/test_rewards.py", "tests/unit/test_rozetler.py", "tests/unit/test_seriler.py", "tests/unit/test_statlar.py", "tests/unit/test_tekrar.py"]
    }
    
    for idx, files in batches.items():
        process_batch(int(idx), files)
