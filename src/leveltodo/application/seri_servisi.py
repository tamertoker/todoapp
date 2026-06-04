"""Seri servisi — giriş ve görev serilerini yönetir.

- Uygulama her açıldığında giriş serisi o güne işaretlenir.
- Bir görev tamamlanınca (TaskCompleted olayı) görev serisi o güne işaretlenir.
Hangi mantıksal güne sayılacağı, olay/saat zamanı + gün başlangıç saatinden bulunur.
"""

from __future__ import annotations

from leveltodo.domain.events import TaskCompleted
from leveltodo.domain.streaks.seriler import SeriTipi, seri_ilerlet
from leveltodo.domain.time.gun import Gun
from leveltodo.domain.time.saat import Saat
from leveltodo.infrastructure.persistence.sqlite.models import DEFAULT_USER_ID
from leveltodo.infrastructure.persistence.sqlite.streak_repository import SqlStreakRepository


class SeriServisi:
    def __init__(
        self,
        repo: SqlStreakRepository,
        saat: Saat,
        gun_baslangic_getir,
        user_id: str = DEFAULT_USER_ID,
    ) -> None:
        self._repo = repo
        self._saat = saat
        self._gun_baslangic = gun_baslangic_getir
        self._user_id = user_id

    def giris_kaydet(self) -> None:
        self._kaydet(SeriTipi.GIRIS, self._bugun())

    def gorev_tamamlandi(self, olay: TaskCompleted) -> None:
        gun = Gun.olustur(olay.occurred_at, self._gun_baslangic()).tarih
        self._kaydet(SeriTipi.GOREV, gun)

    def durumlar(self) -> dict[SeriTipi, tuple[int, int]]:
        """{SeriTipi: (mevcut, en_iyi)}."""
        ham = self._repo.hepsi(self._user_id)
        return {tip: ham.get(tip.value, (0, 0)) for tip in SeriTipi}

    def _bugun(self):
        return Gun.olustur(self._saat.simdi(), self._gun_baslangic()).tarih

    def _kaydet(self, tip: SeriTipi, gun) -> None:
        satir = self._repo.getir(self._user_id, tip.value)
        mevcut = satir.current_count if satir is not None else 0
        en_iyi = satir.best_count if satir is not None else 0
        son_gun = satir.last_day if satir is not None else None
        yeni_m, yeni_e, yeni_g = seri_ilerlet(mevcut, en_iyi, son_gun, gun)
        self._repo.upsert(self._user_id, tip.value, yeni_m, yeni_e, yeni_g)
