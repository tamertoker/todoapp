"""Basit Result tipi: bir işlemin başarı (Ok) ya da hata (Err) sonucunu taşır.

İstisna fırlatmadan, başarısızlığı açıkça döndürmek isteyen application
servisleri için kullanılır. Faz 0'da iskelet olarak konur; asıl kullanımı
Faz 1'deki use-case'lerde başlar.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Ok[T]:
    value: T

    @property
    def is_ok(self) -> bool:
        return True


@dataclass(frozen=True, slots=True)
class Err[E]:
    error: E

    @property
    def is_ok(self) -> bool:
        return False


type Result[T, E] = Ok[T] | Err[E]
