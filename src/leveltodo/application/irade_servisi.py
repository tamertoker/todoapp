"""İrade servisi.

İrade eylemleri (erken kalkmak, ertelediğini bitirmek, kendine sözünü tutmak…)
kaydedilir ve özel **Disiplin** statına XP yazılır. Disiplin sıradan görevlerle
değil, yalnızca iradeyi zorlayan bu eylemlerle büyür.
"""

from __future__ import annotations

from leveltodo.application.dondurma_servisi import DondurmaServisi
from leveltodo.domain.stats.statlar import Stat
from leveltodo.domain.time.gun import Gun
from leveltodo.domain.time.saat import Saat
from leveltodo.infrastructure.persistence.sqlite.irade_repository import SqlIradeRepository
from leveltodo.infrastructure.persistence.sqlite.ledger_repository import SqlLedgerRepository
from leveltodo.infrastructure.persistence.sqlite.models import DEFAULT_USER_ID, WillAct
from leveltodo.shared.ids import new_id

_IRADE_KAYNAGI = "will"


class IradeServisi:
    def __init__(
        self,
        irade_repo: SqlIradeRepository,
        defter_repo: SqlLedgerRepository,
        saat: Saat,
        gun_baslangic_getir,
        dondurma: DondurmaServisi,
        profil_getir,
        user_id: str = DEFAULT_USER_ID,
    ) -> None:
        self._irade = irade_repo
        self._defter = defter_repo
        self._saat = saat
        self._gun_baslangic = gun_baslangic_getir
        self._dondurma = dondurma
        self._profil_getir = profil_getir
        self._user_id = user_id

    def _bugun(self):
        return Gun.olustur(self._saat.simdi(), self._gun_baslangic()).tarih

    def ekle(self, baslik: str, xp: int) -> None:
        kayit_id = new_id()
        simdi = self._saat.simdi()
        gun = self._bugun()
        self._irade.ekle(
            id=kayit_id,
            user_id=self._user_id,
            day=gun,
            title=baslik.strip(),
            xp=xp,
            created_at=simdi,
        )
        self._defter.record(
            user_id=self._user_id,
            day=gun,
            source=_IRADE_KAYNAGI,
            ref_id=kayit_id,
            xp=xp,
            points=0,
            stat=Stat.DISIPLIN.value,
        )
        self._dondurma.seviye_odulu(self._profil_getir())

    def son_eylemler(self) -> list[WillAct]:
        return self._irade.son_eylemler(self._user_id)
