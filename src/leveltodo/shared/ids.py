"""Sıralanabilir benzersiz kimlikler (ULID).

ULID, oluşturulma zamanına göre sıralanabilen 26 karakterlik bir kimliktir;
veritabanı kayıtlarına ve hata ayıklamaya UUID'den daha dostudur.
"""

from __future__ import annotations

from ulid import ULID


def new_id() -> str:
    """Yeni bir ULID üret ve metin (string) olarak döndür."""
    return str(ULID())
