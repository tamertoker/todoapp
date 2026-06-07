"""Seans-tabanlı görev satırı — başlık + toplam süre + Başlat/Durdur + açılır seanslar.

Görev hiç "bitmez": Başlat ile yeni bir seans açılır, Durdur ile kapanır (süresine
göre ödül). Başlık satırında o güne ait tüm seansların TOPLAM süresi kalın yazar;
açılır bölümde tek tek seanslar (başlangıç–bitiş + süre) listelenir.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from leveltodo.application.gorev_servisi import GorevSatiri, SeansSatiri
from leveltodo.domain.streaks.seriler import seri_rengi
from leveltodo.presentation.views.dashboard.gorev_satir_widget import (
    format_sure,
    satir_canli_saniye,
)


def seansli_gorev_satir(
    satir: GorevSatiri,
    *,
    simdi: datetime,
    sure_etiketleri: dict[str, tuple[QLabel, GorevSatiri]],
    seanslar: list[SeansSatiri],
    baslat: Callable[[str], None],
    durdur: Callable[[str], None],
    sil: Callable[[str], None],
    seans_sil: Callable[[str], None],
) -> QWidget:
    kap = QWidget()
    v = QVBoxLayout(kap)
    v.setContentsMargins(0, 0, 0, 0)
    v.setSpacing(2)

    header = QFrame()
    header.setObjectName("TaskRowActive" if satir.calisiyor else "TaskRow")
    h = QHBoxLayout(header)
    h.setContentsMargins(12, 8, 12, 8)
    h.setSpacing(8)

    expander = QPushButton("▸")
    expander.setCheckable(True)
    expander.setFixedWidth(28)
    h.addWidget(expander)
    h.addWidget(QLabel(satir.baslik))
    if satir.etiket_ad:
        proje = QLabel(f"● {satir.etiket_ad}")
        proje.setStyleSheet(f"color: {satir.etiket_renk or '#888888'}; font-weight: bold;")
        h.addWidget(proje)
    h.addStretch(1)
    if satir.tekrar != "none":
        seri = QLabel(f"🔥 {satir.seri}")
        seri.setStyleSheet(f"color: {seri_rengi(satir.seri)}; font-weight: bold;")
        h.addWidget(seri)

    toplam = QLabel(format_sure(satir_canli_saniye(satir, simdi)))
    toplam.setObjectName("Counter")  # toplam birikmiş süre kalın
    h.addWidget(toplam)
    sure_etiketleri[satir.kayit_id] = (toplam, satir)

    if satir.calisiyor:
        btn = QPushButton("Durdur")
        btn.clicked.connect(lambda _c, i=satir.kayit_id: durdur(i))
    else:
        btn = QPushButton("Başlat")
        btn.clicked.connect(lambda _c, i=satir.kayit_id: baslat(i))
    h.addWidget(btn)
    sil_btn = QPushButton("Sil")
    sil_btn.clicked.connect(lambda _c, i=satir.kayit_id: sil(i))
    h.addWidget(sil_btn)
    v.addWidget(header)

    alt = QWidget()
    av = QVBoxLayout(alt)
    av.setContentsMargins(36, 0, 12, 4)
    av.setSpacing(2)
    if not seanslar:
        bos = QLabel("Henüz seans yok. Başlat'a basınca ilki açılır.")
        bos.setObjectName("Tag")
        av.addWidget(bos)
    else:
        for se in seanslar:
            aralik = (
                f"{se.baslangic} – {se.bitis}" if se.bitis else f"{se.baslangic} – (çalışıyor)"
            )
            sh = QHBoxLayout()
            aralik_l = QLabel(aralik)
            aralik_l.setObjectName("Tag")
            sure_l = QLabel(format_sure(se.sure))
            sure_l.setObjectName("Timer")
            ssil = QPushButton("Sil")
            ssil.clicked.connect(lambda _c, sid=se.seans_id: seans_sil(sid))
            sh.addWidget(aralik_l, stretch=1)
            sh.addWidget(sure_l)
            sh.addWidget(ssil)
            kapx = QWidget()
            kapx.setLayout(sh)
            av.addWidget(kapx)
    alt.setVisible(False)
    expander.toggled.connect(alt.setVisible)
    expander.toggled.connect(lambda on: expander.setText("▾" if on else "▸"))
    v.addWidget(alt)
    return kap
