"""Rutin ekranı.

Kendi günlük ölçütlerini (kaç bardak su, kaç sayfa, spor yaptın mı) burada
tanımlar ve bugünün değerini girersin. Sayısal alanda hedefi tutturmak (en az
ya da en fazla), evet/hayır alanında işaretlemek — o alana atadığın gelişim
alanına (stat) XP kazandırır. Ödül gün başına bir kezdir.
"""

from __future__ import annotations

from PyQt6.QtCore import QTime, pyqtSignal
from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from leveltodo.application.rutin_servisi import RutinSatiri
from leveltodo.bootstrap import Container
from leveltodo.domain.rutinler.rutinler import RutinTuru, Yon
from leveltodo.domain.stats.statlar import STAT_ETIKET, Stat


class RutinView(QWidget):
    degisti = pyqtSignal()

    def __init__(self, container: Container, ses=None) -> None:
        super().__init__()
        self._container = container
        self._ses = ses

        title = QLabel("Rutin")
        title.setObjectName("Title")
        bilgi = QLabel("Günlük ölçütlerini tanımla, değerini gir — hedefi tutturunca XP kazan.")
        bilgi.setObjectName("Subtitle")

        self._ilerleme_bar = QProgressBar()
        self._ilerleme_bar.setObjectName("GunlukBar")
        self._ilerleme_bar.setTextVisible(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(bilgi)
        layout.addWidget(self._ilerleme_bar)
        layout.addWidget(self._uyandirma_karti())
        layout.addWidget(self._tanim_formu())
        layout.addWidget(QLabel("Bugünün rutinleri"))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        ic = QWidget()
        self._liste_layout = QVBoxLayout(ic)
        self._liste_layout.setContentsMargins(0, 0, 0, 0)
        self._liste_layout.setSpacing(8)
        scroll.setWidget(ic)
        layout.addWidget(scroll, stretch=1)

        self.yenile()

    # — Yeni alan tanımlama formu —
    def _tanim_formu(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("TaskRow")
        grid = QGridLayout(frame)
        grid.setContentsMargins(12, 10, 12, 10)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(4)

        self._ad = QLineEdit()
        self._ad.setPlaceholderText("Ad (ör. su, sayfa, spor)")

        self._tur = QComboBox()
        self._tur.addItem("Sayı", RutinTuru.SAYI)
        self._tur.addItem("Evet / Hayır", RutinTuru.EVET_HAYIR)
        self._tur.addItem("Metin", RutinTuru.METIN)
        self._tur.currentIndexChanged.connect(self._tur_degisti)

        self._yon = QComboBox()
        self._yon.addItem("En az", Yon.EN_AZ)
        self._yon.addItem("En fazla", Yon.EN_FAZLA)

        self._hedef = QSpinBox()
        self._hedef.setRange(1, 100000)
        self._hedef.setValue(8)

        self._stat = QComboBox()
        for s in Stat:
            self._stat.addItem(STAT_ETIKET[s], s)

        self._odul = QSpinBox()
        self._odul.setRange(1, 1000)
        self._odul.setValue(30)

        ekle_btn = QPushButton("Alan ekle")
        ekle_btn.clicked.connect(self._alan_ekle)

        basliklar = ("Ad", "Tür", "Yön", "Hedef", "Stat", "Ödül XP", "")
        for sutun, metin in enumerate(basliklar):
            etiket = QLabel(metin)
            etiket.setObjectName("Tag")
            grid.addWidget(etiket, 0, sutun)
        grid.addWidget(self._ad, 1, 0)
        grid.addWidget(self._tur, 1, 1)
        grid.addWidget(self._yon, 1, 2)
        grid.addWidget(self._hedef, 1, 3)
        grid.addWidget(self._stat, 1, 4)
        grid.addWidget(self._odul, 1, 5)
        grid.addWidget(ekle_btn, 1, 6)
        grid.setColumnStretch(0, 1)
        return frame

    def _tur_degisti(self) -> None:
        tur = self._tur.currentData()
        sayi = tur is RutinTuru.SAYI
        metin = tur is RutinTuru.METIN
        self._yon.setEnabled(sayi)
        self._hedef.setEnabled(sayi)
        # Metin alanının hedefi/ödülü yok → stat ve XP de kapanır.
        self._stat.setEnabled(not metin)
        self._odul.setEnabled(not metin)

    def _alan_ekle(self) -> None:
        ad = self._ad.text().strip()
        if not ad:
            return
        tur = self._tur.currentData()
        if tur is RutinTuru.SAYI:
            self._container.rutin.alan_ekle(
                ad,
                tur,
                self._stat.currentData(),
                self._odul.value(),
                yon=self._yon.currentData(),
                hedef=self._hedef.value(),
            )
        elif tur is RutinTuru.EVET_HAYIR:
            self._container.rutin.alan_ekle(ad, tur, self._stat.currentData(), self._odul.value())
        else:  # METIN — hedefsiz/ödülsüz
            self._container.rutin.alan_ekle(ad, tur)
        self._ad.clear()
        self.yenile()
        self.degisti.emit()

    # — Uyku rutini (uyandırma disiplini) —
    def _uyandirma_karti(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("TaskRow")
        h = QHBoxLayout(frame)
        h.setContentsMargins(12, 8, 12, 8)
        h.setSpacing(8)
        h.addWidget(QLabel("Uyku rutini"))
        h.addWidget(QLabel("Hedef:"))
        self._hedef_edit = QTimeEdit()
        self._hedef_edit.setDisplayFormat("HH:mm")
        self._hedef_edit.setTime(self._saat_parse(self._container.uyandirma.hedef))
        self._hedef_edit.timeChanged.connect(self._hedef_kaydet)
        h.addWidget(self._hedef_edit)
        h.addWidget(QLabel("Kalkış:"))
        self._kalkis_edit = QTimeEdit()
        self._kalkis_edit.setDisplayFormat("HH:mm")
        self._kalkis_edit.setTime(QTime.currentTime())
        h.addWidget(self._kalkis_edit)
        kalktim_btn = QPushButton("Kalktım")
        kalktim_btn.clicked.connect(self._kalktim)
        h.addWidget(kalktim_btn)
        self._uyanma_sonuc = QLabel()
        self._uyanma_sonuc.setObjectName("Tag")
        h.addWidget(self._uyanma_sonuc, stretch=1)
        return frame

    def _saat_parse(self, hhmm: str) -> QTime:
        try:
            saat, dakika = hhmm.split(":")
            return QTime(int(saat), int(dakika))
        except (ValueError, AttributeError):
            return QTime(7, 0)

    def _hedef_kaydet(self, t: QTime) -> None:
        self._container.uyandirma.hedef_ayarla(t.toString("HH:mm"))

    def _kalktim(self) -> None:
        gercek = self._kalkis_edit.time().toString("HH:mm")
        basarili = self._container.uyandirma.kalktim(gercek)
        if not basarili and self._ses is not None:
            self._ses.cal("hata")  # geç kalkış: başarısızlık anı
        self._uyanma_yenile()
        self.degisti.emit()

    def _uyanma_yenile(self) -> None:
        kayit = self._container.uyandirma.bugun_kaydi()
        if kayit is None:
            self._uyanma_sonuc.setText("Bugün henüz kalkmadın.")
        elif kayit.basarili:
            self._uyanma_sonuc.setText(f"Bugün {kayit.gercek} — zamanında ✓ (+Disiplin)")
        else:
            self._uyanma_sonuc.setText(f"Bugün {kayit.gercek} — geç kalkıldı")

    # — Bugünün rutin listesi —
    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.yenile()

    def yenile(self) -> None:
        self._uyanma_yenile()
        while self._liste_layout.count():
            item = self._liste_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

        alanlar = self._container.rutin.bugunku_alanlar()
        toplam = len(alanlar)
        biten = sum(
            1
            for a in alanlar
            if a.odul_verildi or (a.tur is RutinTuru.METIN and a.bugun_metin)
        )
        self._ilerleme_bar.setVisible(toplam > 0)
        if toplam > 0:
            self._ilerleme_bar.setMaximum(toplam)
            self._ilerleme_bar.setValue(biten)
            self._ilerleme_bar.setFormat(f"Bugünün rutinleri: {biten} / {toplam}")
        if not alanlar:
            bos = QLabel("Henüz rutin alanı yok. Yukarıdan ilkini ekle.")
            bos.setObjectName("Subtitle")
            self._liste_layout.addWidget(bos)
        else:
            for alan in alanlar:
                self._liste_layout.addWidget(self._satir(alan))
        self._liste_layout.addStretch(1)

    def _satir(self, alan: RutinSatiri) -> QFrame:
        frame = QFrame()
        frame.setObjectName("TaskRow")
        h = QHBoxLayout(frame)
        h.setContentsMargins(12, 8, 12, 8)
        h.setSpacing(8)

        ad = QLabel(alan.ad)
        h.addWidget(ad, stretch=1)

        if alan.tur is RutinTuru.EVET_HAYIR:
            kutu = QCheckBox("yaptım")
            kutu.setChecked((alan.bugun_deger or 0) >= 1)
            kutu.toggled.connect(
                lambda isaretli, fid=alan.field_id: self._deger_gir(fid, 1 if isaretli else 0)
            )
            h.addWidget(kutu)
        elif alan.tur is RutinTuru.METIN:
            satir_metin = QLineEdit(alan.bugun_metin or "")
            satir_metin.setPlaceholderText("bugünkü not…")
            kaydet = QPushButton("Kaydet")
            kaydet.clicked.connect(
                lambda _c, fid=alan.field_id, le=satir_metin: self._metin_gir(fid, le.text())
            )
            h.addWidget(satir_metin, stretch=2)
            h.addWidget(kaydet)
        else:
            hedef_metni = f"{'en az' if alan.yon is Yon.EN_AZ else 'en fazla'} {alan.hedef}"
            ipucu = QLabel(hedef_metni)
            ipucu.setObjectName("Tag")
            spin = QSpinBox()
            spin.setRange(0, 100000)
            spin.setValue(alan.bugun_deger or 0)
            kaydet = QPushButton("Kaydet")
            kaydet.clicked.connect(
                lambda _c, fid=alan.field_id, s=spin: self._deger_gir(fid, s.value())
            )
            h.addWidget(ipucu)
            h.addWidget(spin)
            h.addWidget(kaydet)

        # Ödül etiketi yalnızca ödüllü türlerde (metin türünün ödülü yok).
        if alan.tur is not RutinTuru.METIN:
            odul = QLabel(f"+{alan.odul_xp} {STAT_ETIKET[Stat(alan.stat)]}")
            odul.setObjectName("Counter")
            h.addWidget(odul)
            if alan.odul_verildi:
                alindi = QLabel("✓ bugün alındı")
                alindi.setObjectName("Tag")
                h.addWidget(alindi)

        sil = QPushButton("Sil")
        sil.clicked.connect(lambda _c, fid=alan.field_id: self._alan_sil(fid))
        h.addWidget(sil)
        return frame

    def _deger_gir(self, field_id: str, deger: int) -> None:
        self._container.rutin.deger_gir(field_id, deger)
        self.yenile()
        self.degisti.emit()

    def _metin_gir(self, field_id: str, metin: str) -> None:
        self._container.rutin.metin_gir(field_id, metin)
        self.yenile()
        self.degisti.emit()

    def _alan_sil(self, field_id: str) -> None:
        self._container.rutin.alan_sil(field_id)
        self.yenile()
        self.degisti.emit()
