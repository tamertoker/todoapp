"""Takvim görünümü — günün 24 saatini çalışma bloklarıyla görsel olarak gösterir.

Gün görünümü: tek bir günün 24 saati, çalışmalar gerçek başlangıç-bitiş
saatlerinde renkli bloklar olarak (blokta görev adı). Hafta görünümü: o haftanın
yedi günü yan yana sütunlar. Sağ üstte tarih seçici + ileri/geri okları; +/− ile
yakınlaşıp uzaklaşılır (blok boyutu ve aynı anda görünen saat aralığı değişir).
Aynı saatte çakışan işler yan yana bölünür.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from PyQt6.QtCore import QDate, QRect, Qt
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen
from PyQt6.QtWidgets import (
    QButtonGroup,
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from leveltodo.application.istatistik_servisi import TakvimBlok
from leveltodo.bootstrap import Container

_GUN_KISA = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
_AY_KISA = [
    "Oca", "Şub", "Mar", "Nis", "May", "Haz",
    "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara",
]
_GUTTER = 54  # sol saat şeridi genişliği (px)
_MIN_BLOK = 18  # en kısa blok yüksekliği (px) — işaretler de görünür kalsın
_PX_MIN, _PX_MAKS, _PX_ADIM = 24, 160, 16


def _saat_kesir(dt: datetime) -> float:
    return dt.hour + dt.minute / 60 + dt.second / 3600


def _sure_metni(saniye: int) -> str:
    saat, kalan = divmod(max(0, saniye), 3600)
    return f"{saat}:{kalan // 60:02d}" if saat else f"{kalan // 60}dk"


class _Izgara(QWidget):
    """Saat ızgarası + blokları çizen tuval (dikey scroll içinde yaşar)."""

    def __init__(self) -> None:
        super().__init__()
        self._gunler: list[date] = []
        self._bloklar: dict[date, list[TakvimBlok]] = {}
        self._px_saat = 48
        self.setMinimumWidth(360)
        self._yukseklik_uygula()

    def ayarla(
        self, gunler: list[date], bloklar: dict[date, list[TakvimBlok]], px_saat: int
    ) -> None:
        self._gunler = gunler
        self._bloklar = bloklar
        self._px_saat = px_saat
        self._yukseklik_uygula()
        self.update()

    def _yukseklik_uygula(self) -> None:
        self.setFixedHeight(24 * self._px_saat + 4)

    def _kolon_genislik(self) -> float:
        n = max(1, len(self._gunler))
        return (self.width() - _GUTTER) / n

    def paintEvent(self, event) -> None:  # noqa: ARG002
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor("#15101f"))
        col_w = self._kolon_genislik()

        # — Saat çizgileri + şerit etiketleri —
        p.setFont(QFont(self.font().family(), 8))
        for s in range(25):
            y = round(s * self._px_saat)
            p.setPen(QPen(QColor("#2a2140"), 1))
            p.drawLine(_GUTTER, y, self.width(), y)
            if s < 24:
                p.setPen(QPen(QColor("#7a6f99"), 1))
                p.drawText(QRect(0, y + 2, _GUTTER - 6, 16),
                           Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop,
                           f"{s:02d}:00")

        # — Sütun ayraçları —
        p.setPen(QPen(QColor("#2a2140"), 1))
        for i in range(len(self._gunler) + 1):
            x = round(_GUTTER + i * col_w)
            p.drawLine(x, 0, x, self.height())

        # — Bloklar —
        for i, gun in enumerate(self._gunler):
            kol_x = _GUTTER + i * col_w
            self._kolon_ciz(p, self._bloklar.get(gun, []), kol_x, col_w)

    def _kolon_ciz(
        self, p: QPainter, bloklar: list[TakvimBlok], kol_x: float, kol_w: float
    ) -> None:
        if not bloklar:
            return
        sirali = sorted(bloklar, key=lambda b: b.baslangic)
        # Çakışan blokları kümele ve her küme içinde yan yana "şerit"lere yerleştir.
        for kume, serit_sayisi, serit in self._serit_yerlesim(sirali):
            y0 = _saat_kesir(kume.baslangic) * self._px_saat
            saat_sure = (kume.bitis - kume.baslangic).total_seconds() / 3600
            yuk = max(_MIN_BLOK, saat_sure * self._px_saat)
            w = kol_w / serit_sayisi
            x = kol_x + serit * w
            self._blok_ciz(p, kume, x + 1, y0, w - 2, yuk - 1)

    @staticmethod
    def _serit_yerlesim(sirali: list[TakvimBlok]):
        """(blok, kümedeki_şerit_sayısı, blok_şeridi) üçlüleri üretir."""
        sonuc = []
        i = 0
        n = len(sirali)
        while i < n:
            # bir çakışma kümesi topla
            kume = [sirali[i]]
            kume_son = sirali[i].bitis
            j = i + 1
            while j < n and sirali[j].baslangic < kume_son:
                kume.append(sirali[j])
                if sirali[j].bitis > kume_son:
                    kume_son = sirali[j].bitis
                j += 1
            # küme içinde şerit ata (greedy)
            serit_son: list[datetime] = []
            atama: list[int] = []
            for b in kume:
                yerlesti = False
                for k, son in enumerate(serit_son):
                    if son <= b.baslangic:
                        serit_son[k] = b.bitis
                        atama.append(k)
                        yerlesti = True
                        break
                if not yerlesti:
                    atama.append(len(serit_son))
                    serit_son.append(b.bitis)
            sayi = max(1, len(serit_son))
            for b, k in zip(kume, atama, strict=True):
                sonuc.append((b, sayi, k))
            i = j
        return sonuc

    def _blok_ciz(self, p: QPainter, b: TakvimBlok, x: float, y: float, w: float, h: float) -> None:
        renk = QColor(b.renk)
        dolgu = QColor(renk)
        dolgu.setAlpha(70)
        rect = QRect(round(x), round(y), round(w), round(h))
        p.fillRect(rect, dolgu)
        # sol renk şeridi
        p.fillRect(QRect(rect.left(), rect.top(), 3, rect.height()), renk)
        if b.tamamlandi:
            p.setPen(QPen(renk, 1, Qt.PenStyle.DashLine))
        else:
            p.setPen(QPen(renk, 1))
        p.drawRect(rect)

        # — Metin: görev adı (+ süre/işaret) —
        ic = rect.adjusted(7, 1, -4, -1)
        if ic.width() < 12:
            return
        p.setPen(QColor("#f2ecff"))
        fm = QFontMetrics(self.font())
        baslik = fm.elidedText(b.baslik, Qt.TextElideMode.ElideRight, ic.width())
        p.drawText(ic, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, baslik)
        if h >= 30:
            alt = "✓ tamamlandı" if b.tamamlandi else _sure_metni(
                int((b.bitis - b.baslangic).total_seconds())
            )
            p.setPen(QColor("#cdbfe6"))
            p.drawText(ic.adjusted(0, 16, 0, 0),
                       Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, alt)


class _Baslik(QWidget):
    """Scroll dışında kalan, kaymayan sütun başlığı (gün adları)."""

    def __init__(self) -> None:
        super().__init__()
        self._gunler: list[date] = []
        self.setFixedHeight(34)

    def ayarla(self, gunler: list[date]) -> None:
        self._gunler = gunler
        self.update()

    def paintEvent(self, event) -> None:  # noqa: ARG002
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#1c1530"))
        n = max(1, len(self._gunler))
        col_w = (self.width() - _GUTTER) / n
        bugun = date.today()
        p.setFont(QFont(self.font().family(), 9, QFont.Weight.Bold))
        for i, gun in enumerate(self._gunler):
            x = _GUTTER + i * col_w
            metin = f"{_GUN_KISA[gun.weekday()]} · {gun.day} {_AY_KISA[gun.month - 1]}"
            p.setPen(QColor("#c9a6ff") if gun == bugun else QColor("#cdbfe6"))
            p.drawText(QRect(round(x), 0, round(col_w), 34),
                       Qt.AlignmentFlag.AlignCenter, metin)


class TakvimView(QWidget):
    def __init__(self, container: Container) -> None:
        super().__init__()
        self._container = container
        self._mod = "gun"  # "gun" | "hafta"
        self._ref: date = container.istatistik.bugun()
        self._px_saat = 48

        # — Kontroller —
        self._gun_btn = QPushButton("Gün")
        self._hafta_btn = QPushButton("Hafta")
        for b, m in ((self._gun_btn, "gun"), (self._hafta_btn, "hafta")):
            b.setObjectName("NavButton")
            b.setCheckable(True)
            b.clicked.connect(lambda _c, mod=m: self._mod_degis(mod))
        self._gun_btn.setChecked(True)
        grup = QButtonGroup(self)
        grup.addButton(self._gun_btn)
        grup.addButton(self._hafta_btn)

        geri = QPushButton("◀")
        geri.setFixedWidth(36)
        geri.clicked.connect(lambda: self._kaydir(-1))
        ileri = QPushButton("▶")
        ileri.setFixedWidth(36)
        ileri.clicked.connect(lambda: self._kaydir(+1))

        self._tarih = QDateEdit()
        self._tarih.setCalendarPopup(True)
        self._tarih.setDisplayFormat("dd.MM.yyyy")
        self._tarih.setDate(QDate(self._ref.year, self._ref.month, self._ref.day))
        self._tarih.dateChanged.connect(self._tarih_degisti)

        self._aralik_label = QLabel()
        self._aralik_label.setObjectName("ProfileBar")

        eksi = QPushButton("−")
        eksi.setFixedWidth(36)
        eksi.clicked.connect(lambda: self._zoom(-_PX_ADIM))
        arti = QPushButton("+")
        arti.setFixedWidth(36)
        arti.clicked.connect(lambda: self._zoom(+_PX_ADIM))

        ust = QHBoxLayout()
        ust.addWidget(self._gun_btn)
        ust.addWidget(self._hafta_btn)
        ust.addSpacing(12)
        ust.addWidget(geri)
        ust.addWidget(ileri)
        ust.addSpacing(8)
        ust.addWidget(self._aralik_label, stretch=1)
        ust.addWidget(QLabel("Tarih:"))
        ust.addWidget(self._tarih)
        ust.addSpacing(8)
        ust.addWidget(eksi)
        ust.addWidget(arti)

        # — Başlık + ızgara —
        self._baslik = _Baslik()
        self._izgara = _Izgara()
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setWidget(self._izgara)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addLayout(ust)
        layout.addWidget(self._baslik)
        layout.addWidget(self._scroll, stretch=1)

        self.yenile()
        # Açılışta sabah saatlerine kaydır (gece boşluğunu atla).
        self._scroll.verticalScrollBar().setValue(6 * self._px_saat)

    def _mod_degis(self, mod: str) -> None:
        self._mod = mod
        self.yenile()

    def _kaydir(self, yon: int) -> None:
        adim = 7 if self._mod == "hafta" else 1
        self._ref = self._ref + timedelta(days=yon * adim)
        self._tarih.blockSignals(True)
        self._tarih.setDate(QDate(self._ref.year, self._ref.month, self._ref.day))
        self._tarih.blockSignals(False)
        self.yenile()

    def _tarih_degisti(self) -> None:
        self._ref = self._tarih.date().toPyDate()
        self.yenile()

    def _zoom(self, delta: int) -> None:
        yeni = max(_PX_MIN, min(_PX_MAKS, self._px_saat + delta))
        if yeni == self._px_saat:
            return
        oran = self._scroll.verticalScrollBar().value() / max(1, self._izgara.height())
        self._px_saat = yeni
        self.yenile()
        self._scroll.verticalScrollBar().setValue(round(oran * self._izgara.height()))

    def _gun_listesi(self) -> list[date]:
        if self._mod == "hafta":
            pazartesi = self._ref - timedelta(days=self._ref.weekday())
            return [pazartesi + timedelta(days=i) for i in range(7)]
        return [self._ref]

    def yenile(self) -> None:
        gunler = self._gun_listesi()
        bas, bit = gunler[0], gunler[-1]
        bloklar: dict[date, list[TakvimBlok]] = {g: [] for g in gunler}
        for b in self._container.istatistik.takvim_bloklari(bas, bit):
            if b.gun in bloklar:
                bloklar[b.gun].append(b)

        if self._mod == "hafta":
            bas_m = _AY_KISA[bas.month - 1]
            bit_m = _AY_KISA[bit.month - 1]
            self._aralik_label.setText(
                f"{bas.day} {bas_m} – {bit.day} {bit_m} {bit.year}"
            )
        else:
            self._aralik_label.setText(
                f"{_GUN_KISA[bas.weekday()]}, {bas.day} {_AY_KISA[bas.month - 1]} {bas.year}"
            )
        self._baslik.ayarla(gunler)
        self._izgara.ayarla(gunler, bloklar, self._px_saat)
