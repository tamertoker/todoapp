"""Mentor servisi — durumsal mesajlar (dürtme, kışkırtma, amnesti uyarısı).

Periyodik olarak çağrılır (uygulama açıkken zamanlayıcıdan). Üç şeyi değerlendirir,
her birini gün başına en çok bir kez gösterir (ayar deposunda gün işareti tutulur):
- **Mentor dürtmesi**: bir gelişim alanına (stat) eşikten uzun süre dokunulmadıysa.
- **Düşman kışkırtması**: düşük olasılıkla tembelliğe çağıran bir fısıltı.
- **Amnesti uyarısı**: telafi yığını eşiği aşınca "yükü affet" hatırlatması.

Bildirim kapalı/gece sessizliğindeyse o tür gösterilmez ve gün işareti konmaz;
böylece uygun bir ana kadar yeniden denenir.
"""

from __future__ import annotations

from datetime import date

from leveltodo.application.bildirim_servisi import BildirimServisi
from leveltodo.application.dusman_servisi import DusmanServisi
from leveltodo.application.gorev_servisi import GorevServisi
from leveltodo.application.settings_service import SettingsService
from leveltodo.domain.bildirim.bildirim import BildirimKategori
from leveltodo.domain.dusman.dusman import kiskirtma_sec
from leveltodo.domain.mentor.mesajlar import mentor_durtme
from leveltodo.domain.sans import Sans
from leveltodo.domain.stats.statlar import STAT_ETIKET, Stat
from leveltodo.domain.time.gun import Gun
from leveltodo.domain.time.saat import Saat
from leveltodo.infrastructure.persistence.sqlite.ledger_repository import SqlLedgerRepository
from leveltodo.infrastructure.persistence.sqlite.models import DEFAULT_USER_ID

MENTOR_IHMAL_GUN = 3
KISKIRTMA_OLASILIK = 0.15
AMNESTI_ESIK = 10


class MentorServisi:
    SON_DURTME = "mentor_son_durtme_gun"
    SON_KISKIRTMA = "dusman_son_kiskirtma_gun"
    SON_AMNESTI = "amnesti_son_uyari_gun"

    def __init__(
        self,
        defter_repo: SqlLedgerRepository,
        dusman: DusmanServisi,
        gorevler: GorevServisi,
        bildirim: BildirimServisi,
        settings: SettingsService,
        saat: Saat,
        gun_baslangic_getir,
        sans: Sans,
        user_id: str = DEFAULT_USER_ID,
    ) -> None:
        self._defter = defter_repo
        self._dusman = dusman
        self._gorevler = gorevler
        self._bildirim = bildirim
        self._settings = settings
        self._saat = saat
        self._gun_baslangic = gun_baslangic_getir
        self._sans = sans
        self._user_id = user_id

    def _bugun(self) -> date:
        return Gun.olustur(self._saat.simdi(), self._gun_baslangic()).tarih

    def _bugun_yapildi_mi(self, anahtar: str, gun: date) -> bool:
        return str(self._settings.get(anahtar)) == gun.isoformat()

    def periyodik_kontrol(self) -> None:
        gun = self._bugun()
        self._mentor_durtme(gun)
        self._dusman_kiskirtma(gun)
        self._amnesti_uyari(gun)

    def _mentor_durtme(self, gun: date) -> None:
        if self._bugun_yapildi_mi(self.SON_DURTME, gun):
            return
        son_gunler = self._defter.son_stat_gunleri(self._user_id)
        adaylar = [
            (stat, (gun - g).days)
            for stat, g in son_gunler.items()
            if (gun - g).days >= MENTOR_IHMAL_GUN
        ]
        if not adaylar:
            return
        stat, gun_sayi = max(adaylar, key=lambda x: x[1])
        mesaj = mentor_durtme(STAT_ETIKET[Stat(stat)], gun_sayi, gun.toordinal())
        if self._bildirim.bildir(BildirimKategori.DURTME, "Mentor", mesaj):
            self._settings.set(self.SON_DURTME, gun.isoformat())

    def _dusman_kiskirtma(self, gun: date) -> None:
        if self._bugun_yapildi_mi(self.SON_KISKIRTMA, gun):
            return
        if not self._sans.kritik_mi(KISKIRTMA_OLASILIK):
            return
        dusman = self._dusman.durum()[0]
        mesaj = kiskirtma_sec(gun.toordinal())
        if self._bildirim.bildir(BildirimKategori.DURTME, dusman.ad, mesaj):
            self._settings.set(self.SON_KISKIRTMA, gun.isoformat())

    def _amnesti_uyari(self, gun: date) -> None:
        if self._bugun_yapildi_mi(self.SON_AMNESTI, gun):
            return
        if self._gorevler.telafi_sayisi() < AMNESTI_ESIK:
            return
        mesaj = "Kaçan görevler birikti. Telafi ekranından 'Yükü affet' ile sıfırlayabilirsin."
        if self._bildirim.bildir(BildirimKategori.UYARI, "Telafi yığını", mesaj):
            self._settings.set(self.SON_AMNESTI, gun.isoformat())
