"""Seans-tabanlı görev satırı — başlık + toplam süre + Başlat/Durdur + açılır seanslar.

Görev hiç "bitmez": Başlat ile yeni bir seans açılır, Durdur ile kapanır (süresine
göre ödül). Başlık satırında o güne ait tüm seansların TOPLAM süresi kalın yazar;
açılır bölümde her seans (başlangıç–bitiş saatleri DÜZENLENEBİLİR + süre + sil), ayrıca
elle seans ekleme satırı bulunur. Açık/kapalı durumu satır yeniden çizilse de korunur.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from PyQt6.QtCore import QTime
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from leveltodo.application.gorev_servisi import GorevSatiri, SeansSatiri
from leveltodo.domain.streaks.seriler import seri_rengi
from leveltodo.presentation.common.ikonlar import seri_ikon
from leveltodo.presentation.views.dashboard.gorev_satir_widget import (
    format_sure,
    satir_canli_saniye,
)


def _qtime(hhmm: str) -> QTime:
    try:
        s, d = hhmm.split(":")
        return QTime(int(s), int(d))
    except (ValueError, AttributeError):
        return QTime(0, 0)


def _saat_kutusu(hhmm: str) -> QTimeEdit:
    kutu = QTimeEdit()
    kutu.setDisplayFormat("HH:mm")
    kutu.setTime(_qtime(hhmm))
    return kutu


def seansli_gorev_satir(
    satir: GorevSatiri,
    *,
    simdi: datetime,
    sure_etiketleri: dict[str, tuple[QLabel, GorevSatiri]],
    ilerleme_barlari: dict[str, tuple[QProgressBar, GorevSatiri]] | None = None,
    seanslar: list[SeansSatiri],
    baslat: Callable[[str], None],
    durdur: Callable[[str], None],
    tamamla: Callable[[str], None],
    sil: Callable[[str], None],
    seans_sil: Callable[[str], None],
    seans_guncelle: Callable[[str, str, str], None],
    seans_manuel_ekle: Callable[[str, str, str], None],
    acik: bool,
    toggle_acik: Callable[[str, bool], None],
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

    expander = QPushButton("▼" if acik else "▶")
    expander.setObjectName("Expander")
    expander.setCheckable(True)
    expander.setChecked(acik)
    expander.setFixedWidth(30)
    h.addWidget(expander)
    h.addWidget(QLabel(satir.baslik))
    if satir.etiket_ad:
        nokta = QLabel()
        nokta.setFixedSize(12, 12)
        nokta.setStyleSheet(
            f"background-color: {satir.etiket_renk or '#888888'}; border-radius: 6px;"
        )
        ad = QLabel(satir.etiket_ad)
        ad.setStyleSheet("font-weight: bold;")
        h.addWidget(nokta)
        h.addWidget(ad)
    h.addStretch(1)
    if satir.tekrar != "none":
        seri_px = seri_ikon(satir.seri, 24)
        if seri_px is not None:
            seri_ik = QLabel()
            seri_ik.setPixmap(seri_px)
            h.addWidget(seri_ik)
            seri = QLabel(str(satir.seri))
        else:
            seri = QLabel(f"🔥 {satir.seri}")
        seri.setStyleSheet(f"color: {seri_rengi(satir.seri)}; font-weight: bold;")
        h.addWidget(seri)

    toplam = QLabel(format_sure(satir_canli_saniye(satir, simdi)))
    toplam.setObjectName("Counter")
    h.addWidget(toplam)
    sure_etiketleri[satir.kayit_id] = (toplam, satir)

    if satir.calisiyor:
        btn = QPushButton("Durdur")
        btn.clicked.connect(lambda _c, i=satir.kayit_id: durdur(i))
    else:
        btn = QPushButton("Başlat")
        btn.clicked.connect(lambda _c, i=satir.kayit_id: baslat(i))
    h.addWidget(btn)
    bitir_btn = QPushButton("Bitir")
    bitir_btn.setToolTip(
        "Görevi tamamlar ve XP verir. (Sadece süre tutmak istersen Başlat/Durdur'u kullan.)"
    )
    bitir_btn.clicked.connect(lambda _c, i=satir.kayit_id: tamamla(i))
    h.addWidget(bitir_btn)
    sil_btn = QPushButton("Sil")
    sil_btn.setToolTip("Görevi listeden kaldırır; geçmiş süre/istatistikler korunur.")
    sil_btn.clicked.connect(lambda _c, i=satir.kayit_id: sil(i))
    h.addWidget(sil_btn)

    # Hedef süre verilmişse görev satırının ÜSTÜNDE mikro ilerleme barı (silik metinli).
    if satir.hedef_sure:
        bar = QProgressBar()
        bar.setObjectName("MikroBar")
        bar.setTextVisible(True)
        bar.setMaximumHeight(14)
        bar.setMaximum(max(1, satir.hedef_sure))
        calisilan = satir_canli_saniye(satir, simdi)
        bar.setValue(min(calisilan, satir.hedef_sure))
        bar.setFormat(f"{format_sure(calisilan)} / {format_sure(satir.hedef_sure)}")
        v.addWidget(bar)
        if ilerleme_barlari is not None:
            ilerleme_barlari[satir.kayit_id] = (bar, satir)
    v.addWidget(header)

    alt = QWidget()
    av = QVBoxLayout(alt)
    av.setContentsMargins(40, 2, 12, 6)
    av.setSpacing(3)
    if not seanslar:
        bos = QLabel("Henüz seans yok. Başlat'a basınca ilki açılır.")
        bos.setObjectName("Tag")
        av.addWidget(bos)
    for se in seanslar:
        av.addWidget(_seans_satiri(se, seans_sil, seans_guncelle))
    av.addWidget(_manuel_satir(satir.kayit_id, seans_manuel_ekle))

    alt.setVisible(acik)

    def _toggle(on: bool) -> None:
        alt.setVisible(on)
        expander.setText("▼" if on else "▶")
        toggle_acik(satir.kayit_id, on)

    expander.toggled.connect(_toggle)
    v.addWidget(alt)
    return kap


def _seans_satiri(
    se: SeansSatiri,
    seans_sil: Callable[[str], None],
    seans_guncelle: Callable[[str, str, str], None],
) -> QWidget:
    kap = QWidget()
    sh = QHBoxLayout(kap)
    sh.setContentsMargins(0, 0, 0, 0)
    sh.setSpacing(6)
    if se.bitis is None:
        # Hâlâ çalışan açık seans — düzenlenmez.
        sh.addWidget(QLabel(f"{se.baslangic} – (çalışıyor)"))
        sh.addStretch(1)
        sh.addWidget(QLabel(format_sure(se.sure)))
    else:
        bas_edit = _saat_kutusu(se.baslangic)
        bit_edit = _saat_kutusu(se.bitis)
        sure_l = QLabel(format_sure(se.sure))
        sure_l.setObjectName("Timer")
        kaydet = QPushButton("Kaydet")
        kaydet.clicked.connect(
            lambda _c, sid=se.seans_id, b=bas_edit, e=bit_edit: seans_guncelle(
                sid, b.time().toString("HH:mm"), e.time().toString("HH:mm")
            )
        )
        ssil = QPushButton("Sil")
        ssil.clicked.connect(lambda _c, sid=se.seans_id: seans_sil(sid))
        sh.addWidget(bas_edit)
        sh.addWidget(QLabel("–"))
        sh.addWidget(bit_edit)
        sh.addWidget(sure_l)
        sh.addStretch(1)
        sh.addWidget(kaydet)
        sh.addWidget(ssil)
    return kap


def _manuel_satir(kayit_id: str, seans_manuel_ekle: Callable[[str, str, str], None]) -> QWidget:
    kap = QWidget()
    mh = QHBoxLayout(kap)
    mh.setContentsMargins(0, 0, 0, 0)
    mh.setSpacing(6)
    m_bas = _saat_kutusu("12:00")
    m_bit = _saat_kutusu("12:30")
    ekle = QPushButton("Seans ekle")
    ekle.clicked.connect(
        lambda _c, b=m_bas, e=m_bit: seans_manuel_ekle(
            kayit_id, b.time().toString("HH:mm"), e.time().toString("HH:mm")
        )
    )
    mh.addWidget(QLabel("Elle:"))
    mh.addWidget(m_bas)
    mh.addWidget(QLabel("–"))
    mh.addWidget(m_bit)
    mh.addStretch(1)
    mh.addWidget(ekle)
    return kap
