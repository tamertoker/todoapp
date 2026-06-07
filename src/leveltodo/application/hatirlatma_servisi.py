"""Görev hatırlatma servisi.

Bir göreve hatırlatma saati (HH:MM) atanmışsa, o saat geldiğinde (ve görev bugün
geçerliyse) bir HATIRLATMA bildirimi gönderir — gün başına en çok bir kez. Periyodik
olarak (zamanlayıcıdan, dakikada bir) çağrılır.
"""

from __future__ import annotations

from leveltodo.application.bildirim_servisi import BildirimServisi
from leveltodo.domain.bildirim.bildirim import BildirimKategori
from leveltodo.domain.tasks.kurallar import Tekrar, gunde_olusur_mu
from leveltodo.domain.time.gun import Gun
from leveltodo.domain.time.saat import Saat
from leveltodo.infrastructure.persistence.sqlite.models import DEFAULT_USER_ID
from leveltodo.infrastructure.persistence.sqlite.task_repository import SqlTaskRepository


def _dakika(hhmm: str) -> int | None:
    try:
        saat, dakika = hhmm.split(":")
        return int(saat) * 60 + int(dakika)
    except (ValueError, AttributeError):
        return None


class HatirlatmaServisi:
    def __init__(
        self,
        gorev_repo: SqlTaskRepository,
        bildirim: BildirimServisi,
        saat: Saat,
        gun_baslangic_getir,
        user_id: str = DEFAULT_USER_ID,
    ) -> None:
        self._gorev = gorev_repo
        self._bildirim = bildirim
        self._saat = saat
        self._gun_baslangic = gun_baslangic_getir
        self._user_id = user_id

    def kontrol(self) -> None:
        simdi = self._saat.simdi()
        bugun = Gun.olustur(simdi, self._gun_baslangic()).tarih
        su_an_dk = simdi.hour * 60 + simdi.minute
        for sablon in self._gorev.hatirlatmali_sablonlar(self._user_id):
            if sablon.reminder_last == bugun:
                continue  # bugün zaten hatırlatıldı
            hedef_dk = _dakika(sablon.reminder or "")
            if hedef_dk is None or su_an_dk < hedef_dk:
                continue  # saat henüz gelmedi
            if sablon.recurrence != "none":
                olusturma = Gun.olustur(sablon.created_at, self._gun_baslangic()).tarih
                if not gunde_olusur_mu(
                    Tekrar(sablon.recurrence), sablon.recurrence_param or "", olusturma, bugun
                ):
                    continue  # bu görev bugün geçerli değil
            gosterildi = self._bildirim.bildir(
                BildirimKategori.HATIRLATMA, "Hatırlatma", f"Görev: {sablon.title}"
            )
            if gosterildi:  # bastırıldıysa (gece sessizliği) gün işareti konmaz, sonra denenir
                self._gorev.reminder_last_yaz(sablon.id, bugun)
