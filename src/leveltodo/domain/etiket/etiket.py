"""Etiket (proje) — saf yardımcılar.

Her görev bir etikete (projeye) bağlanabilir: renkli bir nokta + ad. Yeni etiket
eklenince paletten sıradaki renk otomatik atanır (kullanıcı sonradan değiştirebilir).
"""

from __future__ import annotations

ETIKET_RENKLERI: tuple[str, ...] = (
    "#1abc9c",  # turkuaz
    "#e74c3c",  # kırmızı
    "#9b59b6",  # mor
    "#3498db",  # mavi
    "#e67e22",  # turuncu
    "#2ecc71",  # yeşil
    "#f1c40f",  # sarı
    "#e84393",  # pembe
    "#34495e",  # lacivert
    "#16a085",  # koyu turkuaz
)


def renk_sec(sira: int) -> str:
    """Sıra numarasına göre paletten renk (döngüsel)."""
    return ETIKET_RENKLERI[sira % len(ETIKET_RENKLERI)]
