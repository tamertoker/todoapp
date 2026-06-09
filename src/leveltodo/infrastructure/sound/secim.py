"""Hangi olayda hangi sesin çalacağı — saf seçim (Qt'siz)."""

from __future__ import annotations


def tamamlama_sesi(kritik: bool, combo_tetik: bool) -> str:
    """Görev tamamlama anının sesi: kritik > combo > sıradan tamamlama."""
    if kritik:
        return "kritik"
    if combo_tetik:
        return "combo"
    return "tamamla"
