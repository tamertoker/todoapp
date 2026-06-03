"""Ayar deposu arayüzü (ISettingsRepository).

Domain katmanı, ayarların "nasıl" saklandığını bilmez (SQLite mi, dosya mı...);
sadece "ayarları getir / bir ayarı kaydet" sözleşmesini tanımlar. Asıl saklama
işini Infrastructure katmanındaki SQLite implementasyonu yapar. Bu ayrım
sayesinde ileride saklama biçimini değiştirsek domain'e dokunmayız.
"""

from __future__ import annotations

from typing import Protocol


class ISettingsRepository(Protocol):
    def get_all(self, user_id: str) -> dict[str, str]:
        """Kullanıcının tüm ayarlarını {anahtar: ham_değer} olarak döndürür."""
        ...

    def upsert(self, user_id: str, key: str, raw_value: str) -> None:
        """Bir ayarı kaydeder; varsa günceller, yoksa ekler."""
        ...
