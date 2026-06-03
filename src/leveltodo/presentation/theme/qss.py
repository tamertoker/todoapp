"""QSS (arayüz stil sayfası) üretimi.

Bir paletten ve font adından, Qt'nin anlayacağı stil metnini üretir. QSS,
web'deki CSS'in Qt karşılığıdır: hangi öğe nasıl görünsün onu söyler.
Pixel havası için köşeler keskin (border-radius yok) ve kenarlıklar belirgin.
"""

from __future__ import annotations

from leveltodo.presentation.theme.palette import Palette


def build_qss(palette: Palette, font_family: str) -> str:
    p = palette
    return f"""
    * {{
        font-family: "{font_family}";
        font-size: 13px;
    }}
    QWidget {{
        background-color: {p.bg};
        color: {p.text};
    }}
    QFrame#Panel {{
        background-color: {p.panel};
        border: 2px solid {p.border};
    }}
    QLabel#Title {{
        font-size: 22px;
        font-weight: bold;
        color: {p.accent};
    }}
    QLabel#Subtitle {{
        color: {p.text_dim};
    }}
    QPushButton {{
        background-color: {p.panel};
        color: {p.text};
        border: 2px solid {p.border};
        padding: 6px 14px;
    }}
    QPushButton:hover {{
        border-color: {p.accent};
    }}
    QPushButton:pressed {{
        background-color: {p.accent};
        color: {p.accent_text};
    }}
    QPushButton#NavButton {{
        text-align: left;
        border: none;
        border-left: 4px solid transparent;
    }}
    QPushButton#NavButton:checked {{
        border-left: 4px solid {p.accent};
        color: {p.accent};
        background-color: {p.panel};
    }}
    QComboBox, QSpinBox {{
        background-color: {p.bg};
        color: {p.text};
        border: 2px solid {p.border};
        padding: 4px 6px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {p.panel};
        color: {p.text};
        selection-background-color: {p.accent};
        selection-color: {p.accent_text};
    }}
    QCheckBox {{
        spacing: 8px;
    }}
    QLabel#Counter {{
        font-size: 16px;
        font-weight: bold;
        color: {p.accent};
    }}
    QFrame#TaskRow {{
        background-color: {p.panel};
        border: 2px solid {p.border};
    }}
    QLabel#Tag {{
        color: {p.text_dim};
    }}
    """
