import json
import os

batch_index = 10
nodes = [
    {
        "id": "file:src/leveltodo/domain/tasks/rules.py",
        "type": "file",
        "name": "rules.py",
        "summary": "Görev ödül ve süre hesaplama kuralları.",
        "description": "Görevlerin tamamlanma sürelerine göre XP ve puan ödüllerini hesaplayan, kronometre mantığını yöneten saf iş kuralları.",
        "tags": ["domain", "tasks", "logic"],
        "languageNotes": "Recurrence: Tekrar, Reward: Ödül, Elapsed: Geçen süre.",
        "languageLesson": "Saf iş kuralları (pure business rules), veritabanı veya arayüzden bağımsız mantığı temsil eder ve kolayca test edilebilir.",
        "complexity": "simple"
    },
    {
        "id": "class:src/leveltodo/domain/tasks/rules.py:Recurrence",
        "type": "class",
        "name": "Recurrence",
        "summary": "Görev tekrar tipleri.",
        "description": "Görevlerin tek seferlik mi yoksa günlük mü tekrar edeceğini belirleyen Enum sınıfı.",
        "tags": ["domain", "enum"]
    },
    {
        "id": "class:src/leveltodo/domain/tasks/rules.py:TaskStatus",
        "type": "class",
        "name": "TaskStatus",
        "summary": "Görev durumları.",
        "description": "Görevin beklemede (pending) veya tamamlanmış (done) durumlarını belirleyen Enum sınıfı.",
        "tags": ["domain", "enum"]
    },
    {
        "id": "class:src/leveltodo/domain/tasks/rules.py:Reward",
        "type": "class",
        "name": "Reward",
        "summary": "Ödül veri yapısı.",
        "description": "XP ve puan değerlerini bir arada tutan dondurulmuş (frozen) dataclass.",
        "tags": ["domain", "dataclass"]
    },
    {
        "id": "function:src/leveltodo/domain/tasks/rules.py:compute_reward",
        "type": "function",
        "name": "compute_reward",
        "summary": "Ödül hesaplama mantığı.",
        "description": "Geçen süreye veya elle girilen değere göre XP ve puan ödülünü hesaplar.",
        "tags": ["domain", "logic"]
    },
    {
        "id": "function:src/leveltodo/domain/tasks/rules.py:live_elapsed",
        "type": "function",
        "name": "live_elapsed",
        "summary": "Aktif kronometre süresi hesaplama.",
        "description": "Kronometre çalışırken geçen süreyi, kaydedilen süreye o anki segmenti ekleyerek hesaplar.",
        "tags": ["domain", "logic"]
    },
    {
        "id": "file:src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/0001_initial.py",
        "type": "file",
        "name": "0001_initial.py",
        "summary": "İlk veritabanı şeması.",
        "description": "Kullanıcılar (users) ve ayarlar (settings) tablolarını oluşturan başlangıç migration dosyası.",
        "tags": ["infrastructure", "database", "migration"],
        "complexity": "simple"
    },
    {
        "id": "file:src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/0002_tasks.py",
        "type": "file",
        "name": "0002_tasks.py",
        "summary": "Görevler ve finansal olaylar şeması.",
        "description": "Görev (tasks), görev örnekleri (task_instances), XP olayları ve puan işlemlerini saklayan tabloları ekler.",
        "tags": ["infrastructure", "database", "migration"],
        "complexity": "moderate"
    },
    {
        "id": "file:src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/0003_stats.py",
        "type": "file",
        "name": "0003_stats.py",
        "summary": "Stat kolonları eklemesi.",
        "description": "Görevler ve XP olaylarına hangi istatistiği etkilediklerini belirten 'stat' kolonunu ekler.",
        "tags": ["infrastructure", "database", "migration"],
        "complexity": "simple"
    },
    {
        "id": "file:src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/0004_recurrence_param.py",
        "type": "file",
        "name": "0004_recurrence_param.py",
        "summary": "Esnek tekrar parametresi.",
        "description": "Görevlere daha detaylı tekrar kuralları tanımlamak için 'recurrence_param' kolonunu ekler.",
        "tags": ["infrastructure", "database", "migration"],
        "complexity": "simple"
    },
    {
        "id": "file:src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/0005_streaks.py",
        "type": "file",
        "name": "0005_streaks.py",
        "summary": "Seri takip sistemi.",
        "description": "Kullanıcıların günlük giriş ve görev serilerini takip eden 'streaks' tablosunu oluşturur.",
        "tags": ["infrastructure", "database", "migration"],
        "complexity": "simple"
    },
    {
        "id": "file:src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/0006_task_streak.py",
        "type": "file",
        "name": "0006_task_streak.py",
        "summary": "Göreve özel seri kolonları.",
        "description": "Görev bazında seri takibi yapmak için 'streak_count' ve 'streak_last_day' kolonlarını ekler.",
        "tags": ["infrastructure", "database", "migration"],
        "complexity": "simple"
    }
]

# Add init files as module nodes
init_files = [
    "src/leveltodo/domain/gunluk/__init__.py",
    "src/leveltodo/domain/magaza/__init__.py",
    "src/leveltodo/domain/mentor/__init__.py",
    "src/leveltodo/domain/rozetler/__init__.py",
    "src/leveltodo/domain/rutinler/__init__.py",
    "src/leveltodo/domain/settings/__init__.py",
    "src/leveltodo/domain/stats/__init__.py",
    "src/leveltodo/domain/streaks/__init__.py",
    "src/leveltodo/domain/tasks/__init__.py",
    "src/leveltodo/domain/time/__init__.py",
    "src/leveltodo/domain/uyandirma/__init__.py",
    "src/leveltodo/infrastructure/__init__.py",
    "src/leveltodo/infrastructure/assets/__init__.py",
    "src/leveltodo/infrastructure/backup/__init__.py",
    "src/leveltodo/infrastructure/eventbus/__init__.py",
    "src/leveltodo/infrastructure/notifications/__init__.py",
    "src/leveltodo/infrastructure/persistence/__init__.py"
]

for f in init_files:
    nodes.append({
        "id": f"file:{f}",
        "type": "file",
        "name": os.path.basename(os.path.dirname(f)) + "/__init__.py",
        "summary": f"{os.path.basename(os.path.dirname(f))} modülü başlangıcı.",
        "description": f"{os.path.basename(os.path.dirname(f))} alt modüllerini organize eden başlatma dosyası.",
        "tags": ["module", "init"]
    })

edges = [
    {"id": "edge:0002_tasks->0001_initial", "source": "file:src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/0002_tasks.py", "target": "file:src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/0001_initial.py", "type": "depends_on"},
    {"id": "edge:0003_stats->0002_tasks", "source": "file:src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/0003_stats.py", "target": "file:src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/0002_tasks.py", "type": "depends_on"},
    {"id": "edge:0004_recurrence_param->0003_stats", "source": "file:src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/0004_recurrence_param.py", "target": "file:src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/0003_stats.py", "type": "depends_on"},
    {"id": "edge:0005_streaks->0004_recurrence_param", "source": "file:src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/0005_streaks.py", "target": "file:src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/0004_recurrence_param.py", "type": "depends_on"},
    {"id": "edge:0006_task_streak->0005_streaks", "source": "file:src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/0006_task_streak.py", "target": "file:src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/0005_streaks.py", "type": "depends_on"}
]

result = {
    "batchIndex": 10,
    "nodes": nodes,
    "edges": edges
}

with open(r"C:\Users\tamer\Desktop\todoapp\todoapp\.understand-anything\intermediate\batch-10.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
