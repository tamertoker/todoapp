"""Stat servisi — yerleşik 4 stat + kullanıcının eklediği özel statları birleştirir.

Yerleşik statlar enum'da (Entelektüellik/Beden/Farkındalık/Disiplin). Özel statlar
veritabanındadır; anahtarları kendi id'leridir. Hepsi "gelişim alanı" olarak aynı
davranır: görevlerden XP kazanır, seviyeye ve profil seviyesine katılır. Yerleşik
statlar silinemez; özel statlar silinebilir.
"""

from __future__ import annotations

from dataclasses import dataclass

from leveltodo.domain.stats.statlar import GOREV_STATLARI, STAT_ETIKET, Stat
from leveltodo.infrastructure.persistence.sqlite.models import DEFAULT_USER_ID
from leveltodo.infrastructure.persistence.sqlite.stat_repository import SqlStatRepository
from leveltodo.shared.ids import new_id


@dataclass(frozen=True, slots=True)
class StatBilgi:
    anahtar: str
    etiket: str
    silinebilir: bool


class StatServisi:
    def __init__(self, stat_repo: SqlStatRepository, user_id: str = DEFAULT_USER_ID) -> None:
        self._repo = stat_repo
        self._user_id = user_id

    def _ozel(self) -> list[StatBilgi]:
        return [
            StatBilgi(anahtar=s.id, etiket=s.name, silinebilir=True)
            for s in self._repo.aktif(self._user_id)
        ]

    def tum_statlar(self) -> list[StatBilgi]:
        """Profil/seviye/istatistik için TÜM statlar (yerleşik 4 + özel)."""
        yerlesik = [StatBilgi(s.value, STAT_ETIKET[s], False) for s in Stat]
        return yerlesik + self._ozel()

    def gorev_statlari(self) -> list[StatBilgi]:
        """Göreve atanabilen statlar (yerleşik görev statları + özel; Disiplin hariç)."""
        yerlesik = [StatBilgi(s.value, STAT_ETIKET[s], False) for s in GOREV_STATLARI]
        return yerlesik + self._ozel()

    def anahtarlar(self) -> list[str]:
        return [b.anahtar for b in self.tum_statlar()]

    def etiket(self, anahtar: str) -> str:
        for b in self.tum_statlar():
            if b.anahtar == anahtar:
                return b.etiket
        return anahtar

    def stat_ekle(self, ad: str) -> str | None:
        ad = ad.strip()
        if not ad:
            return None
        stat_id = new_id()
        self._repo.ekle(
            id=stat_id,
            user_id=self._user_id,
            name=ad,
            sort_order=self._repo.sonraki_sira(self._user_id),
        )
        return stat_id

    def stat_sil(self, stat_id: str) -> None:
        self._repo.pasife_al(stat_id)
