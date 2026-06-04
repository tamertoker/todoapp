"""Dashboard (ana ekran) — Faz 2.

Üstte profil/unvan barı. Solda avatar (seviyeyle evrilir) ve 4 stat barı.
Sağda iki kasa (XP/Puan), "Görev Ekle" ve bugünün görev listesi (kronometreli).
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from leveltodo.application.gorev_servisi import GorevSatiri
from leveltodo.bootstrap import Container
from leveltodo.domain.events import AppStarted, DomainEvent, TaskCompleted
from leveltodo.domain.stats.statlar import STAT_ETIKET, Stat, unvan_listesi
from leveltodo.domain.streaks.seriler import SeriTipi, seri_rengi
from leveltodo.domain.time.gun import Gun
from leveltodo.infrastructure.assets.avatar import (
    AvatarOlusturucu,
    ai_avatar_yolu,
    avatar_katmanlari,
    kilitli_goruntu,
)
from leveltodo.infrastructure.config import paths
from leveltodo.infrastructure.eventbus.qt_bridge import QtEventBridge
from leveltodo.presentation.views.dashboard.add_task_dialog import AddTaskDialog
from leveltodo.presentation.views.dashboard.bitir_dialog import BitirDialog
from leveltodo.presentation.views.dashboard.dashboard_viewmodel import DashboardViewModel
from leveltodo.presentation.views.dashboard.gorev_satir_widget import (
    format_sure,
    kronometreli_satir,
    satir_canli_saniye,
)

_STAT_SIRA = (Stat.ENTELEKTUELLIK, Stat.BEDEN, Stat.FARKINDALIK, Stat.DISIPLIN)
_GUN_KISA = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]


def _tekrar_aciklama(tekrar: str, parametre: str) -> str:
    if tekrar == "daily":
        return "Her gün"
    if tekrar == "every_x":
        return f"Her {parametre} günde"
    if tekrar == "weekly":
        gunler = [_GUN_KISA[int(g)] for g in parametre.split(",") if g != ""]
        return "-".join(gunler) if gunler else "Haftalık"
    if tekrar == "monthly":
        return f"Ayın {parametre}'i"
    return "Tek seferlik"


class DashboardView(QWidget):
    def __init__(self, container: Container, bridge: QtEventBridge) -> None:
        super().__init__()
        self._container = container
        self._vm = DashboardViewModel(container.gorevler, container.kronometre)
        self._avatar = AvatarOlusturucu(paths.assets_dir())
        self._unvan_listesi = unvan_listesi()
        self._onizleme_indeks = 0
        self._mevcut_rank_indeks: int | None = None
        self._pixmap_cache: dict[str, QPixmap] = {}
        self._sure_etiketleri: dict[str, tuple[QLabel, GorevSatiri]] = {}
        self._mod = "bugun"  # "bugun" | "tumu"

        title = QLabel("LevelTodo")
        title.setObjectName("Title")
        self._unvan_label = QLabel()
        self._unvan_label.setObjectName("ProfileBar")

        self._xp_label = QLabel()
        self._xp_label.setObjectName("Counter")
        self._points_label = QLabel()
        self._points_label.setObjectName("Counter")
        ust = QHBoxLayout()
        ust.addWidget(title)
        ust.addStretch(1)
        ust.addWidget(self._xp_label)
        ust.addSpacing(20)
        ust.addWidget(self._points_label)

        sol = self._build_sol_panel()
        sag = self._build_sag_panel()
        orta = QHBoxLayout()
        orta.setSpacing(16)
        orta.addWidget(sol)
        orta.addLayout(sag, stretch=1)

        self._giris_seri_label = QLabel()
        self._dondurma_label = QLabel()
        self._combo_label = QLabel()
        seri_satiri = QHBoxLayout()
        seri_satiri.addWidget(self._giris_seri_label)
        seri_satiri.addSpacing(20)
        seri_satiri.addWidget(self._dondurma_label)
        seri_satiri.addSpacing(20)
        seri_satiri.addWidget(self._combo_label)
        seri_satiri.addStretch(1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.addLayout(ust)
        layout.addWidget(self._unvan_label)
        layout.addLayout(seri_satiri)
        layout.addLayout(orta, stretch=1)

        self._vm.changed.connect(self._render)
        bridge.domain_event.connect(self._on_event)

        # Açılışta yarım kalmış kronometre varsa durdur (kaydedilen süre korunur).
        self._kurtarma_sayisi = self._vm.kurtar()

        self._tick_timer = QTimer(self)
        self._tick_timer.timeout.connect(self._tick)
        self._tick_timer.start(1000)
        self._checkpoint_timer = QTimer(self)
        self._checkpoint_timer.timeout.connect(self._vm.checkpoint)
        self._checkpoint_timer.start(30000)

        self.refresh_day()
        self._render()

    # — Sol panel: avatar + stat barları —
    def _build_sol_panel(self) -> QWidget:
        panel = QWidget()
        panel.setFixedWidth(280)
        v = QVBoxLayout(panel)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(12)

        avatar_frame = QFrame()
        avatar_frame.setObjectName("AvatarFrame")
        af = QVBoxLayout(avatar_frame)
        self._avatar_label = QLabel()
        self._avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        af.addWidget(self._avatar_label)
        v.addWidget(avatar_frame)

        # Oklar avatarın altındaki unvan yazısının iki yanında (üst panele dokunmaz).
        self._geri_btn = QPushButton("◀")
        self._geri_btn.setFixedWidth(40)
        self._geri_btn.clicked.connect(lambda: self._onizleme_kaydir(-1))
        self._ileri_btn = QPushButton("▶")
        self._ileri_btn.setFixedWidth(40)
        self._ileri_btn.clicked.connect(lambda: self._onizleme_kaydir(+1))
        self._onizleme_unvan_label = QLabel()
        self._onizleme_unvan_label.setObjectName("Counter")
        self._onizleme_unvan_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        alt_satir = QHBoxLayout()
        alt_satir.addWidget(self._geri_btn)
        alt_satir.addWidget(self._onizleme_unvan_label, stretch=1)
        alt_satir.addWidget(self._ileri_btn)
        v.addLayout(alt_satir)

        self._stat_seviye_label: dict[Stat, QLabel] = {}
        self._stat_bar: dict[Stat, QProgressBar] = {}
        for stat in _STAT_SIRA:
            etiket = QLabel()
            bar = QProgressBar()
            bar.setTextVisible(True)
            bar.setFormat("%v / %m")
            self._stat_seviye_label[stat] = etiket
            self._stat_bar[stat] = bar
            v.addWidget(etiket)
            v.addWidget(bar)
        v.addStretch(1)
        return panel

    # — Sağ panel: kasalar + görev listesi —
    def _build_sag_panel(self) -> QVBoxLayout:
        subtitle = QLabel("Burada güç, gösterdiğin iradeyle ölçülür.")
        subtitle.setObjectName("Subtitle")
        self._day_label = QLabel()
        self._status_label = QLabel("…")
        self._status_label.setObjectName("Subtitle")

        add_btn = QPushButton("+ Görev Ekle")
        add_btn.clicked.connect(self._on_add)

        self._mod_bugun_btn = QPushButton("Bugün")
        self._mod_bugun_btn.setObjectName("NavButton")
        self._mod_bugun_btn.setCheckable(True)
        self._mod_bugun_btn.setChecked(True)
        self._mod_tumu_btn = QPushButton("Tümü")
        self._mod_tumu_btn.setObjectName("NavButton")
        self._mod_tumu_btn.setCheckable(True)
        mod_grup = QButtonGroup(self)
        mod_grup.addButton(self._mod_bugun_btn)
        mod_grup.addButton(self._mod_tumu_btn)
        self._mod_bugun_btn.clicked.connect(lambda: self._mod_degis("bugun"))
        self._mod_tumu_btn.clicked.connect(lambda: self._mod_degis("tumu"))
        mod_satiri = QHBoxLayout()
        mod_satiri.addWidget(self._mod_bugun_btn)
        mod_satiri.addWidget(self._mod_tumu_btn)
        mod_satiri.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        tasks_container = QWidget()
        self._tasks_layout = QVBoxLayout(tasks_container)
        self._tasks_layout.setContentsMargins(0, 0, 0, 0)
        self._tasks_layout.setSpacing(8)
        scroll.setWidget(tasks_container)

        sag = QVBoxLayout()
        sag.setSpacing(10)
        sag.addWidget(subtitle)
        sag.addWidget(self._day_label)
        sag.addWidget(self._status_label)
        sag.addWidget(add_btn)
        sag.addLayout(mod_satiri)
        sag.addWidget(scroll, stretch=1)
        return sag

    def refresh_day(self) -> None:
        gun = Gun.olustur(self._container.saat.simdi(), self._container.settings.day_start_hour)
        self._day_label.setText(f"Bugün: {gun}")
        self._day_label.setToolTip(
            "Gün, senin belirlediğin 'gün başlangıcı' saatine göre sayılır (varsayılan 04:00). "
            "Örneğin gece 02:00 hâlâ dünkü güne sayılır."
        )
        self._render()

    def _render(self) -> None:
        xp, puan = self._vm.toplamlar()
        self._xp_label.setText(f"XP  {xp}")
        self._points_label.setText(f"Puan  {puan}")

        self._render_profil_ve_statlar()
        self._render_seriler()
        self._render_gorevler()

    def _render_seriler(self) -> None:
        giris, _ = self._container.seri.durumlar()[SeriTipi.GIRIS]
        self._giris_seri_label.setText(f"🔥 Giriş serisi: {giris} gün")
        self._giris_seri_label.setStyleSheet(f"color: {seri_rengi(giris)}; font-weight: bold;")
        self._dondurma_label.setText(f"❄ Dondurma: {self._container.dondurma.stok()}")

        simdi = self._container.saat.simdi()
        if self._container.combo.aktif_mi(simdi):
            kalan = self._container.combo.kalan_dakika(simdi)
            self._combo_label.setText(f"🔥 Combo ×1.5 ({kalan} dk)")
            self._combo_label.setStyleSheet("color: #ff7a4d; font-weight: bold;")
        else:
            self._combo_label.setText("")

    def _render_profil_ve_statlar(self) -> None:
        durumlar = self._vm.stat_durumlari()
        profil, unvan = self._vm.profil_durumu()

        metin = f"{unvan.unvan}  ·  Profil Sv {profil}"
        if unvan.sonraki_unvan is not None:
            metin += f"  ·  {unvan.sonraki_unvan}'a {unvan.sonraki_unvana_kalan} sv"
        self._unvan_label.setText(metin)

        for stat in _STAT_SIRA:
            durum = durumlar[stat]
            self._stat_seviye_label[stat].setText(f"{STAT_ETIKET[stat]}  ·  Sv {durum.seviye}")
            bar = self._stat_bar[stat]
            bar.setMaximum(max(1, durum.sonraki_seviye_esigi))
            bar.setValue(durum.bu_seviyedeki_xp)

        self._avatar_onizleme_ciz()

    def _render_gorevler(self) -> None:
        self._sure_etiketleri = {}
        while self._tasks_layout.count():
            item = self._tasks_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)  # ekrandan hemen kaldır (hayalet satır olmasın)
                widget.deleteLater()

        if self._mod == "tumu":
            ozetler = self._vm.tum_tekrarli_gorevler()
            if not ozetler:
                bos = QLabel("Henüz tekrarlı görev yok.")
                bos.setObjectName("Subtitle")
                self._tasks_layout.addWidget(bos)
            else:
                for ozet in ozetler:
                    self._tasks_layout.addWidget(self._build_ozet_row(ozet))
        else:
            satirlar = self._vm.satirlar()
            if not satirlar:
                bos = QLabel("Bugün için görev yok. Başlamak için bir görev ekle.")
                bos.setObjectName("Subtitle")
                self._tasks_layout.addWidget(bos)
            else:
                for satir in satirlar:
                    self._tasks_layout.addWidget(self._build_row(satir))
        self._tasks_layout.addStretch(1)

    def _mod_degis(self, mod: str) -> None:
        self._mod = mod
        self._render_gorevler()

    def _build_ozet_row(self, ozet) -> QFrame:
        frame = QFrame()
        frame.setObjectName("TaskRow")
        h = QHBoxLayout(frame)
        h.setContentsMargins(12, 8, 12, 8)
        h.setSpacing(8)

        baslik = QLabel(ozet.baslik)
        aciklama = QLabel(_tekrar_aciklama(ozet.tekrar, ozet.parametre))
        aciklama.setObjectName("Tag")
        seri = QLabel(f"🔥 {ozet.seri}")
        seri.setStyleSheet(f"color: {seri_rengi(ozet.seri)}; font-weight: bold;")

        bugun = Gun.olustur(
            self._container.saat.simdi(), self._container.settings.day_start_hour
        ).tarih
        if ozet.sonraki is None:
            sonraki_metin = "Sonraki: —"
        elif ozet.sonraki == bugun:
            sonraki_metin = "Sonraki: Bugün"
        else:
            sonraki_metin = f"Sonraki: {ozet.sonraki}"
        sonraki = QLabel(sonraki_metin)
        sonraki.setObjectName("Tag")

        sil = QPushButton("Sil")
        sil.clicked.connect(lambda _c, i=ozet.task_id: self._vm.sablon_sil(i))

        h.addWidget(baslik, stretch=1)
        h.addWidget(aciklama)
        h.addWidget(seri)
        h.addWidget(sonraki)
        h.addWidget(sil)
        return frame

    def _build_row(self, satir: GorevSatiri) -> QFrame:
        return kronometreli_satir(
            satir,
            simdi=self._container.saat.simdi(),
            sure_etiketleri=self._sure_etiketleri,
            baslat=self._vm.baslat,
            duraklat=self._vm.duraklat,
            bitir=self._on_bitir,
            sil=self._vm.sil,
        )

    def _tick(self) -> None:
        simdi = self._container.saat.simdi()
        for _kayit_id, (etiket, satir) in self._sure_etiketleri.items():
            if satir.calisiyor:
                etiket.setText(format_sure(satir_canli_saniye(satir, simdi)))

    # — Avatar önizleme (ok'larla gelecek seviyeleri gözetleme) —
    def _kilit_yolu(self) -> Path:
        return paths.assets_dir() / "ui" / "kilit.png"

    def _rank_pixmap(self, ad: str, min_seviye: int) -> QPixmap:
        if ad not in self._pixmap_cache:
            ai_yol = ai_avatar_yolu(paths.assets_dir(), ad)
            if ai_yol is not None:
                self._pixmap_cache[ad] = self._avatar.ai_resmi(ai_yol, 240)
            else:
                self._pixmap_cache[ad] = self._avatar.olustur(
                    avatar_katmanlari(min_seviye), buyutme=4
                )
        return self._pixmap_cache[ad]

    def _onizleme_kaydir(self, yon: int) -> None:
        yeni = self._onizleme_indeks + yon
        if 0 <= yeni < len(self._unvan_listesi):
            self._onizleme_indeks = yeni
            self._avatar_onizleme_ciz()

    def _avatar_onizleme_ciz(self) -> None:
        liste = self._unvan_listesi
        profil, _ = self._vm.profil_durumu()
        mevcut_idx = 0
        for i, (_ad, min_lv) in enumerate(liste):
            if profil >= min_lv:
                mevcut_idx = i
        # Seviye atlayıp yeni bir unvana geçilince önizleme oraya kayar.
        if mevcut_idx != self._mevcut_rank_indeks:
            self._mevcut_rank_indeks = mevcut_idx
            self._onizleme_indeks = mevcut_idx

        indeks = self._onizleme_indeks
        ad, min_lv = liste[indeks]
        kilitli = indeks > mevcut_idx
        pixmap = self._rank_pixmap(ad, min_lv)
        if kilitli:
            pixmap = kilitli_goruntu(pixmap, self._kilit_yolu())
        self._avatar_label.setPixmap(pixmap)

        etiket = f"{ad} · Sv {min_lv}+"
        if kilitli:
            etiket += "  · 🔒"
        self._onizleme_unvan_label.setText(etiket)
        self._geri_btn.setEnabled(indeks > 0)
        self._ileri_btn.setEnabled(indeks < len(liste) - 1)

    def _on_add(self) -> None:
        dialog = AddTaskDialog(self)
        if dialog.exec():
            baslik, tekrar, parametre, ozel_odul, stat = dialog.result_values()
            if baslik:
                self._vm.gorev_ekle(baslik, tekrar, ozel_odul, stat, parametre)

    def _on_bitir(self, satir: GorevSatiri) -> None:
        on_dakika = round(satir_canli_saniye(satir, self._container.saat.simdi()) / 60)
        dialog = BitirDialog(on_dakika, self)
        if dialog.exec():
            self._vm.tamamla(satir.kayit_id, dialog.dakika())

    def _on_event(self, event: DomainEvent) -> None:
        if isinstance(event, AppStarted):
            mesaj = "Yine buradasın. Çoğu insan dönmez; sen döndün."
            if self._kurtarma_sayisi:
                mesaj = "Yarım kalmış kronometre vardı, durdurdum — kayıtlı süre duruyor. " + mesaj
            self._status_label.setText(mesaj)
        elif isinstance(event, TaskCompleted):
            if event.combo_tetik:
                self._status_label.setText("🔥 COMBO başladı! 1 saat boyunca ödüller ×1.5!")
            elif event.kritik:
                self._status_label.setText(
                    f"⚡ KRİTİK! +{event.xp} XP, +{event.points} puan (2 katı)!"
                )
            else:
                self._status_label.setText(f"+{event.xp} XP kazandın. Sırada ne var?")
            self._render()
