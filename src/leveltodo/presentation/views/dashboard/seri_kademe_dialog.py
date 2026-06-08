"""Seri (giriş serisi) kademe atlama kutlaması.

Kullanıcı yeni bir seri kademesine geçtiğinde ekranın ortasında iki bildirim çıkar:
1) Yeni kademeye geçtiğini ve alev simgesinin değiştiğini büyük ikonla duyurur.
2) "Tamam" denip kapatılınca, bir sonraki kademe için kaç gün kaldığını söyler.

Ton: gündelik ama epik alt tonlu; abartısız.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from leveltodo.presentation.common.ikonlar import ikon, seri_sonraki_esik


class _KademeKutu(QDialog):
    def __init__(
        self, parent: QWidget | None, baslik: str, mesaj: str, ikon_px: QPixmap | None
    ) -> None:
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Seri")
        v = QVBoxLayout(self)
        v.setContentsMargins(28, 24, 28, 20)
        v.setSpacing(14)

        baslik_l = QLabel(baslik)
        baslik_l.setObjectName("Title")
        baslik_l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(baslik_l)

        if ikon_px is not None:
            ikon_l = QLabel()
            ikon_l.setPixmap(ikon_px)
            ikon_l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            v.addWidget(ikon_l)

        mesaj_l = QLabel(mesaj)
        mesaj_l.setWordWrap(True)
        mesaj_l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mesaj_l.setMinimumWidth(320)
        v.addWidget(mesaj_l)

        tamam = QPushButton("Tamam")
        tamam.clicked.connect(self.accept)
        v.addWidget(tamam, alignment=Qt.AlignmentFlag.AlignCenter)


def kademe_atlama_goster(
    parent: QWidget | None, kademe: int, gun: int, sonraki_esik: int | None
) -> None:
    """İki ardışık kutu gösterir: önce kutlama, sonra bir sonraki hedef."""
    ikon_px = ikon(f"streak{kademe}", 112)
    _KademeKutu(
        parent,
        f"Seri Kademesi {kademe}!",
        (
            f"Giriş serin {gun}. güne ulaştı ve yeni bir kademeye yükseldin. "
            "Alev simgen de değişti — ateşi büyütmeye devam."
        ),
        ikon_px,
    ).exec()

    if sonraki_esik is None:
        ikinci = "En yüksek kademedesin. Buradan sonrası sadece bu ateşi söndürmemekle ilgili."
    else:
        kalan = max(1, sonraki_esik - gun)
        ikinci = (
            f"Bir sonraki kademe için {kalan} gün daha aralıksız devam etmen yeterli. "
            "Her gün bir tuğla."
        )
    _KademeKutu(parent, "Sıradaki Hedef", ikinci, None).exec()


__all__ = ["kademe_atlama_goster", "seri_sonraki_esik"]
