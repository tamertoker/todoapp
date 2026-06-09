import json

nodes = [
    # Magaza Servisi
    {
        "id": "file:src/leveltodo/application/magaza_servisi.py",
        "name": "magaza_servisi.py",
        "type": "file",
        "filePath": "src/leveltodo/application/magaza_servisi.py",
        "summary": "Mağaza servisi. Oyun-içi Puan ile gerçek-hayat ödüllerinin satın alınmasını yönetir.",
        "tags": ["python", "application", "service"],
        "complexity": "medium"
    },
    {
        "id": "class:src/leveltodo/application/magaza_servisi.py:MagazaServisi",
        "name": "MagazaServisi",
        "type": "class",
        "filePath": "src/leveltodo/application/magaza_servisi.py",
        "summary": "Mağaza işlemlerini (bakiye, ödül ekleme/silme, satın alma) yürüten servis sınıfı.",
        "tags": ["python", "class", "application"]
    },
    # Cuzdan Servisi
    {
        "id": "file:src/leveltodo/application/cuzdan_servisi.py",
        "name": "cuzdan_servisi.py",
        "type": "file",
        "filePath": "src/leveltodo/application/cuzdan_servisi.py",
        "summary": "Cüzdan servisi. Gerçek para gelir/gider işlemlerini, bütçe hedeflerini ve istek listesini (wishlist) yönetir.",
        "tags": ["python", "application", "service"],
        "complexity": "medium"
    },
    {
        "id": "class:src/leveltodo/application/cuzdan_servisi.py:CuzdanServisi",
        "name": "CuzdanServisi",
        "type": "class",
        "filePath": "src/leveltodo/application/cuzdan_servisi.py",
        "summary": "Cüzdan ve wishlist işlemlerini yürüten ana servis sınıfı.",
        "tags": ["python", "class", "application"]
    },
    {
        "id": "class:src/leveltodo/application/cuzdan_servisi.py:AylikOzet",
        "name": "AylikOzet",
        "type": "class",
        "filePath": "src/leveltodo/application/cuzdan_servisi.py",
        "summary": "Aylık gelir, gider ve tasarruf bilgilerini tutan veri sınıfı.",
        "tags": ["python", "dataclass", "application"]
    },
    {
        "id": "class:src/leveltodo/application/cuzdan_servisi.py:WishlistSatiri",
        "name": "WishlistSatiri",
        "type": "class",
        "filePath": "src/leveltodo/application/cuzdan_servisi.py",
        "summary": "İstek listesindeki bir öğenin görüntüleme verilerini tutan sınıf.",
        "tags": ["python", "dataclass", "application"]
    },
    # Takvim View
    {
        "id": "file:src/leveltodo/presentation/views/pano/takvim_view.py",
        "name": "takvim_view.py",
        "type": "file",
        "filePath": "src/leveltodo/presentation/views/pano/takvim_view.py",
        "summary": "Takvim görünümü. Günlük ve haftalık çalışma bloklarını görselleştirir.",
        "tags": ["python", "ui", "presentation"],
        "complexity": "high"
    },
    {
        "id": "class:src/leveltodo/presentation/views/pano/takvim_view.py:TakvimView",
        "name": "TakvimView",
        "type": "class",
        "filePath": "src/leveltodo/presentation/views/pano/takvim_view.py",
        "summary": "Ana takvim arayüzü bileşeni.",
        "tags": ["python", "class", "ui"]
    },
    {
        "id": "class:src/leveltodo/presentation/views/pano/takvim_view.py:_Izgara",
        "name": "_Izgara",
        "type": "class",
        "filePath": "src/leveltodo/presentation/views/pano/takvim_view.py",
        "summary": "Saat ızgarasını ve blokları çizen tuval bileşeni.",
        "tags": ["python", "class", "ui", "internal"]
    },
    # Batch 9 - Other files (Inits)
    {
        "id": "file:src/leveltodo/application/__init__.py",
        "name": "__init__.py",
        "type": "file",
        "filePath": "src/leveltodo/application/__init__.py",
        "summary": "Application paket başlatıcısı.",
        "tags": ["python", "init"]
    },
    {
        "id": "file:src/leveltodo/domain/__init__.py",
        "name": "__init__.py",
        "type": "file",
        "filePath": "src/leveltodo/domain/__init__.py",
        "summary": "Domain paket başlatıcısı.",
        "tags": ["python", "init"]
    }
]

edges = [
    # MagazaServisi contains
    {"source": "class:src/leveltodo/application/magaza_servisi.py:MagazaServisi", "target": "file:src/leveltodo/application/magaza_servisi.py", "type": "contains", "weight": 1.0},
    # CuzdanServisi contains
    {"source": "class:src/leveltodo/application/cuzdan_servisi.py:CuzdanServisi", "target": "file:src/leveltodo/application/cuzdan_servisi.py", "type": "contains", "weight": 1.0},
    {"source": "class:src/leveltodo/application/cuzdan_servisi.py:AylikOzet", "target": "file:src/leveltodo/application/cuzdan_servisi.py", "type": "contains", "weight": 1.0},
    {"source": "class:src/leveltodo/application/cuzdan_servisi.py:WishlistSatiri", "target": "file:src/leveltodo/application/cuzdan_servisi.py", "type": "contains", "weight": 1.0},
    # TakvimView contains
    {"source": "class:src/leveltodo/presentation/views/pano/takvim_view.py:TakvimView", "target": "file:src/leveltodo/presentation/views/pano/takvim_view.py", "type": "contains", "weight": 1.0},
    {"source": "class:src/leveltodo/presentation/views/pano/takvim_view.py:_Izgara", "target": "file:src/leveltodo/presentation/views/pano/takvim_view.py", "type": "contains", "weight": 1.0},
    
    # Dependencies (exemplary)
    {"source": "class:src/leveltodo/application/magaza_servisi.py:MagazaServisi", "target": "file:src/leveltodo/domain/magaza/magaza.py", "type": "uses", "weight": 1.0},
    {"source": "class:src/leveltodo/application/cuzdan_servisi.py:CuzdanServisi", "target": "file:src/leveltodo/domain/cuzdan/cuzdan.py", "type": "uses", "weight": 1.0},
    {"source": "class:src/leveltodo/presentation/views/pano/takvim_view.py:TakvimView", "target": "file:src/leveltodo/application/istatistik_servisi.py", "type": "uses", "weight": 1.0}
]

output = {
    "nodes": nodes,
    "edges": edges
}

with open('.understand-anything/intermediate/batch-9.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("Batch 9 JSON generated successfully.")
