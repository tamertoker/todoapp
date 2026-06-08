"""İkon yükleyici — assets/icons/<ad>.png varsa ölçekli QPixmap döndürür.

Eksik ikon uygulamayı KIRMAZ: dosya yoksa None döner ve çağıran taraf metin/emoji
fallback'ine düşer. Böylece kullanıcı ikonları teker teker ekledikçe yerlerine otururlar.

Ayrıca giriş serisi gün sayısını 6 kademeye eşler (streak1..streak6). Kademe alt
sınırları kullanıcının verdiği değerler: 5, 21, 40, 80, 150 gün.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

from leveltodo.infrastructure.config import paths

# (alt_sinir_gun, kademe) — büyükten küçüğe; gün >= alt_sinir olan ilk satır kademeyi verir.
_SERI_ESIKLER: list[tuple[int, int]] = [(150, 6), (80, 5), (40, 4), (21, 3), (5, 2)]

_cache: dict[tuple[str, int], QPixmap | None] = {}


def seri_kademe(gun: int) -> int:
    """Giriş serisi gün sayısını 0..6 kademeye çevirir (0 = henüz seri yok)."""
    if gun <= 0:
        return 0
    for alt_sinir, kademe in _SERI_ESIKLER:
        if gun >= alt_sinir:
            return kademe
    return 1


def seri_sonraki_esik(gun: int) -> int | None:
    """Bir sonraki kademeye geçmek için gereken gün eşiği; en üst kademede None."""
    for alt_sinir, _ in reversed(_SERI_ESIKLER):  # 5, 21, 40, 80, 150
        if gun < alt_sinir:
            return alt_sinir
    return None


def ikon(ad: str, boy: int = 20) -> QPixmap | None:
    """assets/icons/<ad>.png yükler ve kenarı `boy` piksele ölçekler; yoksa None."""
    anahtar = (ad, boy)
    if anahtar in _cache:
        return _cache[anahtar]
    yol = paths.assets_dir() / "icons" / f"{ad}.png"
    px: QPixmap | None = None
    if yol.exists():
        ham = QPixmap(str(yol))
        if not ham.isNull():
            px = ham.scaled(
                boy,
                boy,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
    _cache[anahtar] = px
    return px


def seri_ikon(gun: int, boy: int = 24) -> QPixmap | None:
    """Giriş serisi gün sayısına uygun streak ikonunu döndürür; seri yoksa None."""
    kademe = seri_kademe(gun)
    if kademe == 0:
        return None
    return ikon(f"streak{kademe}", boy)


def uygulama_ikonu() -> QIcon | None:
    """Uygulama/pencere ikonu: assets/icons/rekor_xp.png varsa onu döndürür, yoksa None."""
    yol = paths.assets_dir() / "icons" / "rekor_xp.png"
    if yol.exists():
        ic = QIcon(str(yol))
        if not ic.isNull():
            return ic
    return None


def ikonlu_baslik(metin: str, ikon_ad: str, ikon_boy: int = 28) -> QWidget:
    """Sol başta ikon, yanında "Title" stilli başlık olan satır. İkon yoksa sadece başlık."""
    kap = QWidget()
    h = QHBoxLayout(kap)
    h.setContentsMargins(0, 0, 0, 0)
    h.setSpacing(8)
    px = ikon(ikon_ad, ikon_boy)
    if px is not None:
        ik = QLabel()
        ik.setPixmap(px)
        h.addWidget(ik)
    baslik = QLabel(metin)
    baslik.setObjectName("Title")
    h.addWidget(baslik)
    h.addStretch(1)
    return kap
