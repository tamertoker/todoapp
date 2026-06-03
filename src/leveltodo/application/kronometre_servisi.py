"""Kronometre servisi — başlat / duraklat / devam, periyodik kayıt (checkpoint)
ve açılışta yarım kalmış kronometreyi kurtarma.

Aynı anda yalnızca bir kronometre çalışır: yenisi başlatılınca açık olan
durdurulur. Böylece "şu an neyle meşgulüm" tek ve net kalır.
"""

from __future__ import annotations

from leveltodo.domain.time.saat import Saat
from leveltodo.infrastructure.persistence.sqlite.models import DEFAULT_USER_ID
from leveltodo.infrastructure.persistence.sqlite.task_repository import SqlTaskRepository


class KronometreServisi:
    def __init__(
        self, gorev_repo: SqlTaskRepository, saat: Saat, user_id: str = DEFAULT_USER_ID
    ) -> None:
        self._gorev = gorev_repo
        self._saat = saat
        self._user_id = user_id

    def baslat(self, kayit_id: str) -> None:
        simdi = self._saat.simdi()
        for kayit in self._gorev.calisan_kayitlar(self._user_id):
            if kayit.id != kayit_id:
                self._gorev.timer_duraklat(kayit.id, simdi)
        self._gorev.timer_baslat(kayit_id, simdi)

    def duraklat(self, kayit_id: str) -> None:
        self._gorev.timer_duraklat(kayit_id, self._saat.simdi())

    def checkpoint(self) -> None:
        self._gorev.timer_checkpoint(self._saat.simdi(), self._user_id)

    def kurtar(self) -> int:
        return self._gorev.timer_kurtar(self._user_id)
