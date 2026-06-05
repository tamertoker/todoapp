"""Uyandırma servisi.

Hedef uyanış saatini yönetir ve sabah "kalktım" denince o günün kaydını tutar.
Hedefe (tolerans payıyla) zamanında kalkıldıysa Disiplin'e XP yazar — gün başına
bir kez. Ceza yoktur: geç kalınca yalnızca ödül verilmez.
"""

from __future__ import annotations

from leveltodo.application.dondurma_servisi import DondurmaServisi
from leveltodo.domain.stats.statlar import Stat
from leveltodo.domain.time.gun import Gun
from leveltodo.domain.time.saat import Saat
from leveltodo.domain.uyandirma.uyandirma import (
    UYANDIRMA_ODUL_XP,
    dakikaya,
    uyanma_basarili_mi,
)
from leveltodo.infrastructure.persistence.sqlite.ledger_repository import SqlLedgerRepository
from leveltodo.infrastructure.persistence.sqlite.models import DEFAULT_USER_ID, WakeLog
from leveltodo.infrastructure.persistence.sqlite.uyandirma_repository import SqlUyandirmaRepository
from leveltodo.shared.ids import new_id

_UYANDIRMA_KAYNAGI = "wake"
_HEDEF_ANAHTAR = "uyandirma_hedef"


class UyandirmaServisi:
    def __init__(
        self,
        uyandirma_repo: SqlUyandirmaRepository,
        defter_repo: SqlLedgerRepository,
        settings,
        saat: Saat,
        gun_baslangic_getir,
        dondurma: DondurmaServisi,
        profil_getir,
        user_id: str = DEFAULT_USER_ID,
    ) -> None:
        self._repo = uyandirma_repo
        self._defter = defter_repo
        self._settings = settings
        self._saat = saat
        self._gun_baslangic = gun_baslangic_getir
        self._dondurma = dondurma
        self._profil_getir = profil_getir
        self._user_id = user_id

    def _bugun(self):
        return Gun.olustur(self._saat.simdi(), self._gun_baslangic()).tarih

    @property
    def hedef(self) -> str:
        return str(self._settings.get(_HEDEF_ANAHTAR))

    def hedef_ayarla(self, hhmm: str) -> None:
        self._settings.set(_HEDEF_ANAHTAR, hhmm)

    def bugun_kaydi(self) -> WakeLog | None:
        return self._repo.gun_kaydi(self._user_id, self._bugun())

    def kalktim(self) -> bool:
        """Şimdiki saati o günün kalkışı olarak kaydeder; zamanındaysa ödül verir.
        Gün başına bir kez geçerlidir (mevcut kayıt varsa tekrar ödül vermez)."""
        gun = self._bugun()
        mevcut = self._repo.gun_kaydi(self._user_id, gun)
        if mevcut is not None:
            return mevcut.basarili  # bugün zaten kalkıldı

        simdi = self._saat.simdi()
        gercek = simdi.strftime("%H:%M")
        hedef = self.hedef
        basarili = uyanma_basarili_mi(dakikaya(hedef), dakikaya(gercek))
        self._repo.kaydet(
            id=new_id(),
            user_id=self._user_id,
            day=gun,
            hedef=hedef,
            gercek=gercek,
            basarili=basarili,
        )
        if basarili:
            self._defter.record(
                user_id=self._user_id,
                day=gun,
                source=_UYANDIRMA_KAYNAGI,
                ref_id=None,
                xp=UYANDIRMA_ODUL_XP,
                points=0,
                stat=Stat.DISIPLIN.value,
            )
            self._dondurma.seviye_odulu(self._profil_getir())
        return basarili
