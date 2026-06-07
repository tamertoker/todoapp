"""QSS (arayüz stil sayfası) üretimi.

Bir paletten ve font adından, Qt'nin anlayacağı stil metnini üretir. Pixel-RPG
havası için: keskin köşeler, kalın çift-tonlu kenarlıklar, hafif degrade ("oyulmuş
menü" hissi), parlak (glossy) ilerleme barları ve bevel'li butonlar. Renkler
paletten gelir; bu yüzden tüm temalarda tutarlı durur.
"""

from __future__ import annotations

from leveltodo.presentation.theme.palette import Palette


def _shift(hexc: str, amount: int) -> str:
    """Bir hex rengi açar (amount>0) ya da koyulaştırır (amount<0)."""
    h = hexc.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    def f(v: int) -> int:
        return max(0, min(255, v + amount))

    return f"#{f(r):02x}{f(g):02x}{f(b):02x}"


def build_qss(palette: Palette, font_family: str, up_arrow: str, down_arrow: str) -> str:
    p = palette
    panel_l = _shift(p.panel, 16)
    panel_d = _shift(p.panel, -16)
    acc_l = _shift(p.accent, 34)
    acc_d = _shift(p.accent, -34)
    return f"""
    * {{
        font-family: "{font_family}";
        font-size: 13px;
    }}
    QWidget {{
        background-color: {p.bg};
        color: {p.text};
    }}
    QLabel#Title {{
        font-size: 22px;
        font-weight: bold;
        color: {p.accent};
        border-bottom: 2px solid {p.accent};
        padding-bottom: 4px;
    }}
    QLabel#Subtitle {{
        color: {p.text_dim};
    }}
    QLabel#Counter {{
        font-size: 16px;
        font-weight: bold;
        color: {p.accent};
    }}
    QLabel#Tag {{
        color: {p.text_dim};
    }}
    QLabel#Timer {{
        color: {p.text_dim};
        font-weight: bold;
    }}
    QLabel#ProfileBar {{
        font-size: 15px;
        font-weight: bold;
        color: {p.accent};
    }}

    QFrame#Panel, QFrame#AvatarFrame {{
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1, stop:0 {p.panel}, stop:1 {panel_d});
        border: 3px solid {p.border};
    }}
    QFrame#TaskRow {{
        background-color: {p.panel};
        border: 2px solid {p.border};
    }}
    QFrame#TaskRowActive {{
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1, stop:0 {panel_l}, stop:1 {p.panel});
        border: 3px solid {p.accent};
    }}

    QPushButton {{
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1, stop:0 {panel_l}, stop:1 {panel_d});
        color: {p.text};
        border: 2px solid {p.border};
        padding: 6px 14px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        border: 2px solid {p.accent};
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1, stop:0 {panel_l}, stop:1 {p.panel});
    }}
    QPushButton:pressed {{
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1, stop:0 {panel_d}, stop:1 {p.panel});
        color: {p.accent_text};
        border: 2px solid {p.accent};
    }}
    QPushButton#NavButton {{
        background-color: transparent;
        text-align: left;
        border: none;
        border-left: 4px solid transparent;
        font-weight: normal;
        padding: 6px 10px;
    }}
    QPushButton#NavButton:hover {{
        color: {p.accent};
        border-left: 4px solid {p.border};
    }}
    QPushButton#NavButton:checked {{
        border-left: 4px solid {p.accent};
        color: {p.accent};
        background-color: {p.panel};
    }}
    QPushButton#Expander {{
        font-weight: bold;
        padding: 2px;
    }}
    QPushButton#Expander:checked {{
        background-color: {p.accent};
        color: {p.accent_text};
        border-color: {p.accent};
    }}

    QComboBox, QSpinBox, QLineEdit, QTimeEdit, QDateEdit, QDoubleSpinBox, QTextEdit {{
        background-color: {p.bg};
        color: {p.text};
        border: 2px solid {p.border};
        padding: 4px 6px;
        selection-background-color: {p.accent};
        selection-color: {p.accent_text};
    }}
    QComboBox:hover, QSpinBox:hover, QLineEdit:hover, QTimeEdit:hover, QDateEdit:hover {{
        border: 2px solid {p.accent};
    }}
    QComboBox QAbstractItemView {{
        background-color: {p.panel};
        color: {p.text};
        selection-background-color: {p.accent};
        selection-color: {p.accent_text};
    }}
    QRadioButton, QCheckBox {{
        spacing: 8px;
        color: {p.text};
    }}
    QRadioButton::indicator, QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border: 2px solid {p.border};
        background-color: {p.bg};
    }}
    QRadioButton::indicator:checked, QCheckBox::indicator:checked {{
        background-color: {p.accent};
        border: 2px solid {p.accent};
    }}
    QRadioButton::indicator:hover, QCheckBox::indicator:hover {{
        border-color: {p.accent};
    }}
    QSpinBox::up-button, QTimeEdit::up-button, QDateEdit::up-button, QDoubleSpinBox::up-button {{
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: 18px;
        border-left: 2px solid {p.border};
        background-color: {p.panel};
    }}
    QSpinBox::down-button, QTimeEdit::down-button, QDateEdit::down-button,
    QDoubleSpinBox::down-button {{
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: 18px;
        border-left: 2px solid {p.border};
        background-color: {p.panel};
    }}
    QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
        background-color: {p.accent};
    }}
    QSpinBox::up-arrow {{
        image: url("{up_arrow}");
        width: 10px;
        height: 10px;
    }}
    QSpinBox::down-arrow {{
        image: url("{down_arrow}");
        width: 10px;
        height: 10px;
    }}

    QProgressBar {{
        border: 2px solid {p.border};
        background-color: {panel_d};
        text-align: center;
        color: {p.text};
        font-weight: bold;
        min-height: 16px;
    }}
    QProgressBar::chunk {{
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1, stop:0 {acc_l}, stop:1 {acc_d});
    }}
    QProgressBar#DusmanHpBar::chunk {{
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1, stop:0 #e74c3c, stop:1 #922b21);
    }}

    QScrollBar:vertical {{
        background: {p.bg};
        width: 12px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {p.border};
        min-height: 24px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {p.accent};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}

    QFrame#Toast {{
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1, stop:0 {panel_l}, stop:1 {panel_d});
        border: 2px solid {p.accent};
    }}
    QLabel#ToastBaslik {{
        font-weight: bold;
        color: {p.accent};
    }}
    QLabel#ToastGovde {{
        color: {p.text};
    }}
    QFrame#RozetKartAcik {{
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1, stop:0 {panel_l}, stop:1 {p.panel});
        border: 2px solid {p.accent};
    }}
    QFrame#RozetKartKilitli {{
        background-color: {p.bg};
        border: 2px solid {p.border};
    }}
    """
