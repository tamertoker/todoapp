"""Görev servisi — çekirdek döngünün beyni.

Görev ekleme, bugünün listesini hazırlama ve görevi tamamlayıp ödül yazma
işlerini yönetir. Saat ve "gün başlangıcı" ayarını kullanarak hangi mantıksal
günde olduğumuzu bilir; her-gün görevlerinin bugünkü kaydını tembelce (lazy)
üretir.

Not: Veritabanı/depo (repository) metotları İngilizce kaldı (add_template,
today_rows, record...) — bunlar yerleşik altyapı terimleridir.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from leveltodo.domain.events import TaskCompleted
from leveltodo.domain.stats.statlar import (
    SeviyeDurumu,
    Stat,
    UnvanDurumu,
    seviye_hesapla,
    unvan_hesapla,
)
from leveltodo.domain.tasks.kurallar import (
    Odul,
    Tekrar,
    canli_sure,
    gunde_olusur_mu,
    odul_hesapla,
)
from leveltodo.domain.time.gun import Gun
from leveltodo.domain.time.saat import Saat
from leveltodo.infrastructure.eventbus.olay_hatti import OlayHatti
from leveltodo.infrastructure.persistence.sqlite.ledger_repository import SqlLedgerRepository
from leveltodo.infrastructure.persistence.sqlite.models import DEFAULT_USER_ID
from leveltodo.infrastructure.persistence.sqlite.task_repository import SqlTaskRepository
from leveltodo.shared.ids import new_id

_TAMAMLAMA_KAYNAGI = "task_completion"


@dataclass(frozen=True, slots=True)
class GorevSatiri:
    """Ekranın bir görev satırını çizmek için ihtiyaç duyduğu sade veri."""

    kayit_id: str
    baslik: str
    durum: str
    tekrar: str
    calisilan_saniye: int
    calisiyor: bool
    segment_baslangici: datetime | None
    odul_xp: int | None
    odul_puan: int | None


class GorevServisi:
    def __init__(
        self,
        gorev_repo: SqlTaskRepository,
        defter_repo: SqlLedgerRepository,
        saat: Saat,
        olay_hatti: OlayHatti,
        gun_baslangic_getir,
        user_id: str = DEFAULT_USER_ID,
    ) -> None:
        self._gorev = gorev_repo
        self._defter = defter_repo
        self._saat = saat
        self._olay_hatti = olay_hatti
        self._gun_baslangic = gun_baslangic_getir
        self._user_id = user_id

    def _bugun(self):
        return Gun.olustur(self._saat.simdi(), self._gun_baslangic()).tarih

    def gorev_olustur(
        self,
        baslik: str,
        tekrar: Tekrar,
        ozel_odul: int | None = None,
        stat: Stat | None = None,
        parametre: str = "",
    ) -> str:
        gorev_id = new_id()
        self._gorev.add_template(
            id=gorev_id,
            user_id=self._user_id,
            title=baslik.strip(),
            recurrence=tekrar.value,
            recurrence_param=parametre or None,
            reward_override=ozel_odul,
            stat=stat.value if stat is not None else None,
            created_at=self._saat.simdi(),
        )
        if tekrar is Tekrar.YOK:
            self._gorev.add_instance(
                id=new_id(),
                task_id=gorev_id,
                user_id=self._user_id,
                day=self._bugun(),
                title=baslik.strip(),
            )
        return gorev_id

    def bugunku_gorevler(self) -> list[GorevSatiri]:
        gun = self._bugun()
        self._gunluk_kayitlari_uret(gun)
        satirlar = self._gorev.today_rows(self._user_id, gun)
        return [
            GorevSatiri(
                kayit_id=kayit.id,
                baslik=kayit.title,
                durum=kayit.status,
                tekrar=tekrar,
                calisilan_saniye=kayit.committed_seconds,
                calisiyor=kayit.timer_running,
                segment_baslangici=kayit.segment_started_at,
                odul_xp=kayit.reward_xp,
                odul_puan=kayit.reward_points,
            )
            for kayit, tekrar in satirlar
        ]

    def _gunluk_kayitlari_uret(self, gun) -> None:
        for sablon in self._gorev.aktif_tekrarli_sablonlar(self._user_id):
            # Çapa, takvim tarihi değil mantıksal oluşturma günü olmalı; böylece
            # gün başlangıç saatinden önce eklenen görev de o gün görünür.
            olusturma_gunu = Gun.olustur(sablon.created_at, self._gun_baslangic()).tarih
            olusur = gunde_olusur_mu(
                Tekrar(sablon.recurrence),
                sablon.recurrence_param or "",
                olusturma_gunu,
                gun,
            )
            if olusur and not self._gorev.instance_exists(sablon.id, gun):
                self._gorev.add_instance(
                    id=new_id(),
                    task_id=sablon.id,
                    user_id=self._user_id,
                    day=gun,
                    title=sablon.title,
                )

    def tamamla(self, kayit_id: str, elle_dakika: int | None = None) -> Odul | None:
        kayit = self._gorev.get_instance(kayit_id)
        if kayit is None:
            return None
        simdi = self._saat.simdi()
        if elle_dakika is not None:
            # Kullanıcı süreyi elle girdi (ör. kronometresiz çalıştı).
            islenmis_saniye = max(0, elle_dakika) * 60
        else:
            # Kronometre çalışıyorsa o anki segmenti de süreye katarak hesapla.
            islenmis_saniye = canli_sure(
                kayit.committed_seconds,
                kayit.segment_started_at if kayit.timer_running else None,
                simdi,
            )
        sablon = self._gorev.get_template(kayit.task_id)
        ozel = sablon.reward_override if sablon is not None else None

        odul = odul_hesapla(islenmis_saniye, ozel)
        ok = self._gorev.complete_instance(
            instance_id=kayit_id,
            committed_seconds=islenmis_saniye,
            reward_xp=odul.xp,
            reward_points=odul.puan,
            completed_at=simdi,
        )
        if not ok:
            return None

        self._defter.record(
            user_id=self._user_id,
            day=self._bugun(),
            source=_TAMAMLAMA_KAYNAGI,
            ref_id=kayit_id,
            xp=odul.xp,
            points=odul.puan,
            stat=sablon.stat if sablon is not None else None,
        )
        self._olay_hatti.publish(
            TaskCompleted(
                occurred_at=simdi,
                instance_id=kayit_id,
                xp=odul.xp,
                points=odul.puan,
            )
        )
        return odul

    def gorev_sil(self, kayit_id: str) -> None:
        kayit = self._gorev.get_instance(kayit_id)
        if kayit is not None:
            self._gorev.deactivate_template(kayit.task_id)

    def toplamlar(self) -> tuple[int, int]:
        return self._defter.totals(self._user_id)

    def stat_durumlari(self) -> dict[Stat, SeviyeDurumu]:
        """Her stat için (seviye, ilerleme) durumu."""
        toplamlar = self._defter.stat_xp_toplamlari(self._user_id)
        return {s: seviye_hesapla(toplamlar.get(s.value, 0)) for s in Stat}

    def profil_durumu(self) -> tuple[int, UnvanDurumu]:
        """Profil seviyesi (stat seviyelerinin toplamı) ve unvan durumu."""
        durumlar = self.stat_durumlari()
        profil = sum(d.seviye for d in durumlar.values())
        return profil, unvan_hesapla(profil)

    def gelistirme_xp_ekle(self, stat: Stat, miktar: int) -> None:
        """Debug: bir stata doğrudan XP ekler (yalnızca geliştirme/test için)."""
        self._defter.record(
            user_id=self._user_id,
            day=self._bugun(),
            source="debug",
            ref_id=None,
            xp=miktar,
            points=0,
            stat=stat.value,
        )
