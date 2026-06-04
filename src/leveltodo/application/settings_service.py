"""Ayar servisi.

Ekran ile ayar deposu arasındaki katman. Görevleri:
- Varsayılan ayarları bilmek (kullanıcı hiç değiştirmediyse bunlar geçerli).
- Değerleri JSON metnine çevirip saklamak ve okurken geri çözmek.
- Sık okunan ayarlar için küçük bir bellek-içi kopya (cache) tutmak.

Depo (repository) detaylarını bilmez; sadece ISettingsRepository sözleşmesini
kullanır. Bu yüzden saf, test edilebilir application kodudur.
"""

from __future__ import annotations

import json
from typing import Any

from leveltodo.domain.settings.repository import ISettingsRepository

DEFAULTS: dict[str, Any] = {
    "day_start_hour": 4,
    "theme": "dark",
    "minimize_to_tray": True,
    "dondurma_stok": 0,
    "dondurma_son_seviye": 0,
}


class SettingsService:
    def __init__(self, repo: ISettingsRepository, user_id: str) -> None:
        self._repo = repo
        self._user_id = user_id
        self._cache: dict[str, Any] = {
            key: json.loads(raw) for key, raw in repo.get_all(user_id).items()
        }

    def get(self, key: str) -> Any:
        if key in self._cache:
            return self._cache[key]
        return DEFAULTS[key]

    def set(self, key: str, value: Any) -> None:
        self._repo.upsert(self._user_id, key, json.dumps(value))
        self._cache[key] = value

    # — Tipli kısayollar —
    @property
    def day_start_hour(self) -> int:
        return int(self.get("day_start_hour"))

    @property
    def theme(self) -> str:
        return str(self.get("theme"))

    @property
    def minimize_to_tray(self) -> bool:
        return bool(self.get("minimize_to_tray"))
