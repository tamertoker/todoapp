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

MIDNIGHT = Palette(
    bg="#0f1b2d",
    panel="#16263d",
    border="#2e4a6b",
    text="#e6eef7",
    text_dim="#88a2bf",
    accent="#4fc3dc",
    accent_text="#0f1b2d",
)

FOREST = Palette(
    bg="#13201a",
    panel="#1d2f26",
    border="#38543f",
    text="#e8f0e6",
    text_dim="#92ad99",
    accent="#e0b552",
    accent_text="#13201a",
)

SUNSET = Palette(
    bg="#241420",
    panel="#341d2c",
    border="#5a3247",
    text="#f6e7ee",
    text_dim="#c39bae",
    accent="#ff7a4d",
    accent_text="#241420",
)

ARCANE = Palette(
    bg="#1b1230",
    panel="#271a41",
    border="#48306c",
    text="#efe6ff",
    text_dim="#a890c8",
    accent="#c86bff",
    accent_text="#1b1230",
)

KADIM = Palette(
    bg="#241a12",
    panel="#33261a",
    border="#5c4326",
    text="#efe2c8",
    text_dim="#b09a72",
    accent="#c9a24a",
    accent_text="#241a12",
)

THEMES = {
    "dark": DARK,
    "light": LIGHT,
    "midnight": MIDNIGHT,
    "forest": FOREST,
    "sunset": SUNSET,
    "arcane": ARCANE,
    "kadim": KADIM,
}


def get_palette(theme: str) -> Palette:
    return THEMES.get(theme, DARK)
