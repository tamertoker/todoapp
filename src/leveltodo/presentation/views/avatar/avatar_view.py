"""Avatar deneme/önizleme ekranı.

Soldaki menüden ulaşılır. Tüm vücut paletleri, kıyafetler, saçlar ve şapkalar
arasında ileri/geri gezilir; seçilen her parçanın adı sağda yazılır ve avatar
büyütülmüş olarak görünür. Seviye kilitleri sonra eklenecek; burası şimdilik
"hepsini görmek" içindir.
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from leveltodo.infrastructure.assets.avatar import AvatarOlusturucu, kategori_secenekleri
from leveltodo.infrastructure.config import paths

_KATEGORI_ADI = {"vucut": "Vücut", "kiyafet": "Kıyafet", "sac": "Saç", "sapka": "Şapka"}
# Vücut ve kıyafet hep var; saç ve şapka "Yok" olabilir.
_ISTEGE_BAGLI = {"sac", "sapka"}


def _kisa_ad(dosya: str) -> str:
    parcalar = Path(dosya).stem.split("_")
    return " ".join(parcalar[4:]) if len(parcalar) > 4 else Path(dosya).stem


class AvatarEditorView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._avatar = AvatarOlusturucu(paths.assets_dir())
        self._secenekler = kategori_secenekleri(paths.assets_dir())
        self._indeks: dict[str, int] = {"vucut": 0, "kiyafet": 0, "sac": -1, "sapka": -1}
        # Varsayılan kıyafet: en basit (fstr v01) bulunursa onunla başla.
        self._indeks["kiyafet"] = next(
            (i for i, f in enumerate(self._secenekler["kiyafet"]) if "fstr_v01" in f), 0
        )

        title = QLabel("Avatar — Deneme")
        title.setObjectName("Title")
        bilgi = QLabel("Tüm parçaları buradan gez. Seviye kilitlerini sonra ayarlayacağız.")
        bilgi.setObjectName("Subtitle")

        onizleme_cerceve = QFrame()
        onizleme_cerceve.setObjectName("AvatarFrame")
        oc = QVBoxLayout(onizleme_cerceve)
        self._onizleme = QLabel()
        self._onizleme.setAlignment(Qt.AlignmentFlag.AlignCenter)
        oc.addWidget(self._onizleme)

        self._secim_etiketleri: dict[str, QLabel] = {}
        kontroller = QVBoxLayout()
        kontroller.setSpacing(12)
        for kategori in ("vucut", "kiyafet", "sac", "sapka"):
            kontroller.addLayout(self._build_kategori_satiri(kategori))
        kontroller.addStretch(1)

        govde = QHBoxLayout()
        govde.setSpacing(20)
        govde.addWidget(onizleme_cerceve)
        govde.addLayout(kontroller, stretch=1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(bilgi)
        layout.addLayout(govde, stretch=1)

        self._render()

    def _build_kategori_satiri(self, kategori: str):
        satir = QHBoxLayout()
        ad = QLabel(_KATEGORI_ADI[kategori])
        ad.setFixedWidth(80)
        geri = QPushButton("◀")
        geri.setFixedWidth(40)
        geri.clicked.connect(lambda _c, k=kategori: self._degistir(k, -1))
        secim = QLabel()
        secim.setObjectName("Counter")
        ileri = QPushButton("▶")
        ileri.setFixedWidth(40)
        ileri.clicked.connect(lambda _c, k=kategori: self._degistir(k, +1))
        self._secim_etiketleri[kategori] = secim

        satir.addWidget(ad)
        satir.addWidget(geri)
        satir.addWidget(secim, stretch=1)
        satir.addWidget(ileri)
        return satir

    def _degistir(self, kategori: str, yon: int) -> None:
        secenekler = self._secenekler[kategori]
        if not secenekler:
            return
        alt_sinir = -1 if kategori in _ISTEGE_BAGLI else 0
        aralik = len(secenekler) - alt_sinir  # -1 dahil toplam seçenek sayısı
        # alt_sinir..len-1 arasında döngüsel ilerle
        mevcut = self._indeks[kategori] - alt_sinir
        self._indeks[kategori] = (mevcut + yon) % aralik + alt_sinir
        self._render()

    def _secili_dosya(self, kategori: str) -> str | None:
        indeks = self._indeks[kategori]
        if indeks < 0:
            return None
        return self._secenekler[kategori][indeks]

    def _render(self) -> None:
        katmanlar: list[str] = []
        for kategori in ("vucut", "kiyafet", "sac", "sapka"):
            dosya = self._secili_dosya(kategori)
            self._secim_etiketleri[kategori].setText(_kisa_ad(dosya) if dosya else "Yok")
            if dosya is not None:
                katmanlar.append(dosya)
        self._onizleme.setPixmap(self._avatar.olustur(katmanlar, buyutme=6))
