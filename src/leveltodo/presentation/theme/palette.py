"""Renk paletleri (dark + light).

Her tema bir avuç renkten oluşur. QSS (arayüz stili) bu renkleri kullanır.
Pixel-RPG havası için renkler doygun ama gözü yormayan tonlarda seçildi.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Palette:
    bg: str           # ana arka plan
    panel: str        # panel/kutu yüzeyi
    border: str       # keskin pixel kenarlık
    text: str         # ana metin
    text_dim: str     # ikincil/soluk metin
    accent: str       # vurgu (butonlar, seçili öğe)
    accent_text: str  # vurgu üzerindeki metin


DARK = Palette(
    bg="#1a1726",
    panel="#241f33",
    border="#4a3f66",
    text="#ece8f5",
    text_dim="#9a8fb8",
    accent="#c9a227",
    accent_text="#1a1726",
)

LIGHT = Palette(
    bg="#efe9dc",
    panel="#fbf7ec",
    border="#b9a886",
    text="#2c2620",
    text_dim="#6f6552",
    accent="#9a6b1f",
    accent_text="#fbf7ec",
)

THEMES = {"dark": DARK, "light": LIGHT}


def get_palette(theme: str) -> Palette:
    return THEMES.get(theme, DARK)
