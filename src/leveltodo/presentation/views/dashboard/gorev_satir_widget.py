"""Kronometreli görev satırı — ana ekran ve Telafi ekranı ortak kullanır.

Bir görev satırını (başlık + etiket + süre + Başlat/Duraklat/Bitir/Sil) çizer.
Böylece telafi görevleri de ana ekrandaki gibi kronometreyle çalışır.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton

from leveltodo.application.gorev_servisi import GorevSatiri
from leveltodo.domain.streaks.seriler import seri_rengi
from leveltodo.domain.tasks.kurallar import canli_sure


def format_sure(saniye: int) -> str:
    saniye = max(0, saniye)
    saat, kalan = divmod(saniye, 3600)
    dakika, sn = divmod(kalan, 60)
    if saat:
        return f"{saat:02d}:{dakika:02d}:{sn:02d}"
    return f"{dakika:02d}:{sn:02d}"


def satir_canli_saniye(satir: GorevSatiri, simdi: datetime) -> int:
    return canli_sure(
        satir.calisilan_saniye,
        satir.segment_baslangici if satir.calisiyor else None,
        simdi,
    )


def kronometreli_satir(
    satir: GorevSatiri,
    *,
    simdi: datetime,
    sure_etiketleri: dict[str, tuple[QLabel, GorevSatiri]],
    baslat: Callable[[str], None],
    duraklat: Callable[[str], None],
    bitir: Callable[[GorevSatiri], None],
    sil: Callable[[str], None] | None = None,
    etiket_metni: str | None = None,
) -> QFrame:
    """Bir görev satırı çizer. Bekleyen satırın süre etiketini, canlı sayaç için
    sure_etiketleri sözlüğüne kaydeder."""
    frame = QFrame()
    frame.setObjectName("TaskRowActive" if satir.calisiyor else "TaskRow")
    h = QHBoxLayout(frame)
    h.setContentsMargins(12, 8, 12, 8)
    h.setSpacing(8)

    h.addWidget(QLabel(satir.baslik), stretch=1)

    if etiket_metni is not None:
        etiket = QLabel(etiket_metni)
        etiket.setObjectName("Tag")
        h.addWidget(etiket)
    elif satir.tekrar == "none":
        etiket = QLabel("Tek seferlik")
        etiket.setObjectName("Tag")
        h.addWidget(etiket)
    else:
        etiket = QLabel(f"🔥 {satir.seri}")
        etiket.setToolTip("Bu görevi üst üste kaç kez yaptın (seri)")
        etiket.setStyleSheet(f"color: {seri_rengi(satir.seri)}; font-weight: bold;")
        h.addWidget(etiket)

    if satir.durum == "pending":
        sure_etiketi = QLabel(format_sure(satir_canli_saniye(satir, simdi)))
        sure_etiketi.setObjectName("Timer")
        h.addWidget(sure_etiketi)
        sure_etiketleri[satir.kayit_id] = (sure_etiketi, satir)

        if satir.calisiyor:
            toggle = QPushButton("Duraklat")
            toggle.clicked.connect(lambda _c, i=satir.kayit_id: duraklat(i))
        else:
            toggle = QPushButton("Başlat")
            toggle.clicked.connect(lambda _c, i=satir.kayit_id: baslat(i))
        bitir_btn = QPushButton("Bitir")
        bitir_btn.clicked.connect(lambda _c, s=satir: bitir(s))
        h.addWidget(toggle)
        h.addWidget(bitir_btn)
    else:
        sure_etiketi = QLabel(format_sure(satir.calisilan_saniye))
        sure_etiketi.setObjectName("Timer")
        done = QLabel(f"✓ +{satir.odul_xp} XP")
        done.setObjectName("Counter")
        h.addWidget(sure_etiketi)
        h.addWidget(done)

    if sil is not None:
        sil_btn = QPushButton("Sil")
        sil_btn.clicked.connect(lambda _c, i=satir.kayit_id: sil(i))
        h.addWidget(sil_btn)

    return frame
