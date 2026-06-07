from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

from leveltodo.application.combo_servisi import ComboServisi
from leveltodo.application.dondurma_servisi import DondurmaServisi
from leveltodo.application.rozet_servisi import RozetServisi
from leveltodo.domain.events import TaskCompleted
from leveltodo.domain.sans import Sans
from leveltodo.domain.stats.statlar import (
    SeviyeDurumu,
    Stat,
    UnvanDurumu,
    seviye_hesapla,
    unvan_hesapla,
)
from leveltodo.domain.tasks.kurallar import (
    KRITIK_CARPAN,
    KRITIK_OLASILIK,
    TELAFI_CARPAN,
    Odul,
    Tekrar,
    canli_sure,
    gunde_olusur_mu,
    odul_hesapla,
    onceki_olusum,
    sonraki_olusum,
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
    gun: date
    baslik: str
    durum: str
    tekrar: str
    seri: int
    calisilan_saniye: int
    calisiyor: bool
    segment_baslangici: datetime | None
    odul_xp: int | None
    odul_puan: int | None
    etiket_ad: str | None = None
    etiket_renk: str | None = None


@dataclass(frozen=True, slots=True)
class TekrarliGorevOzeti:
    """'Tümü' görünümü için: tekrarlı görevin düzeni ve bir sonraki gelişi."""

    task_id: str
    baslik: str
    tekrar: str
    parametre: str
    seri: int
    sonraki: date | None


_TELAFI_PENCERE_GUN = 21  # son 3 hafta içindeki kaçırılanlar telafi edilebilir


class GorevServisi:
    def __init__(
        self,
        gorev_repo: SqlTaskRepository,
        defter_repo: SqlLedgerRepository,
        saat: Saat,
        olay_hatti: OlayHatti,
        gun_baslangic_getir,
        dondurma: DondurmaServisi,
        sans: Sans,
        combo: ComboServisi,
        rozet: RozetServisi,
        user_id: str = DEFAULT_USER_ID,
    ) -> None:
        self._gorev = gorev_repo
        self._defter = defter_repo
        self._saat = saat
        self._olay_hatti = olay_hatti
        self._gun_baslangic = gun_baslangic_getir
        self._dondurma = dondurma
        self._sans = sans
        self._combo = combo
        self._rozet = rozet
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
        tag_id: str | None = None,
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
            tag_id=tag_id,
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
                gun=kayit.day,
                baslik=kayit.title,
                durum=kayit.status,
                tekrar=tekrar,
                seri=seri,
                calisilan_saniye=kayit.committed_seconds,
                calisiyor=kayit.timer_running,
                segment_baslangici=kayit.segment_started_at,
                odul_xp=kayit.reward_xp,
                odul_puan=kayit.reward_points,
                etiket_ad=etiket_ad,
                etiket_renk=etiket_renk,
            )
            for kayit, tekrar, seri, etiket_ad, etiket_renk in satirlar
        ]

    def tum_tekrarli_gorevler(self) -> list[TekrarliGorevOzeti]:
        """'Tümü' görünümü: bugün görünmeyenler dahil tüm tekrarlı görevler."""
        bugun = self._bugun()
        ozetler: list[TekrarliGorevOzeti] = []
        for sablon in self._gorev.aktif_tekrarli_sablonlar(self._user_id):
            olusturma = Gun.olustur(sablon.created_at, self._gun_baslangic()).tarih
            sonraki = sonraki_olusum(
                Tekrar(sablon.recurrence), sablon.recurrence_param or "", olusturma, bugun
            )
            ozetler.append(
                TekrarliGorevOzeti(
                    task_id=sablon.id,
                    baslik=sablon.title,
                    tekrar=sablon.recurrence,
                    parametre=sablon.recurrence_param or "",
                    seri=sablon.streak_count,
                    sonraki=sonraki,
                )
            )
        return ozetler

    def telafi_gorevleri(self) -> list[GorevSatiri]:
        """Son 3 hafta içinde kaçırılan tekrarlı oluşumlar; kronometreyle
        yapılabilsin diye bekleyen kayıt olarak hazırlanır (yoksa üretilir)."""
        bugun = self._bugun()
        pencere_basi = bugun - timedelta(days=_TELAFI_PENCERE_GUN)
        for sablon in self._gorev.aktif_tekrarli_sablonlar(self._user_id):
            olusturma = Gun.olustur(sablon.created_at, self._gun_baslangic()).tarih
            gun = max(pencere_basi, olusturma)
            while gun < bugun:  # bugün hariç, geçmiş günler
                olusur = gunde_olusur_mu(
                    Tekrar(sablon.recurrence), sablon.recurrence_param or "", olusturma, gun
                )
                if (
                    olusur
                    and not self._gorev.done_instance_var_mi(sablon.id, gun)
                    and not self._gorev.instance_exists(sablon.id, gun)
                ):
                    self._gorev.add_instance(
                        id=new_id(),
                        task_id=sablon.id,
                        user_id=self._user_id,
                        day=gun,
                        title=sablon.title,
                    )
                gun += timedelta(days=1)

        satirlar = self._gorev.gecmis_bekleyen_satirlar(self._user_id, bugun, pencere_basi)
        return [
            GorevSatiri(
                kayit_id=kayit.id,
                gun=kayit.day,
                baslik=kayit.title,
                durum=kayit.status,
                tekrar=tekrar,
                seri=seri,
                calisilan_saniye=kayit.committed_seconds,
                calisiyor=kayit.timer_running,
                segment_baslangici=kayit.segment_started_at,
                odul_xp=kayit.reward_xp,
                odul_puan=kayit.reward_points,
                etiket_ad=etiket_ad,
                etiket_renk=etiket_renk,
            )
            for kayit, tekrar, seri, etiket_ad, etiket_renk in satirlar
        ]

    def baslik_onerileri(self) -> list[str]:
        return self._gorev.baslik_onerileri(self._user_id)

    def sablon_oneri(self, baslik: str):
        """Verilen başlıklı son görev şablonu (autofill için). Yoksa None."""
        return self._gorev.son_sablon_baslikli(self._user_id, baslik)

    def telafi_sayisi(self) -> int:
        return len(self.telafi_gorevleri())

    def telafi_amnesti_uygula(self) -> int:
        """Kaçan görev yığınını affeder: penceredeki bekleyen geçmiş kayıtları
        ödülsüz kapatır. Kaç kaydın affedildiğini döner."""
        self.telafi_gorevleri()  # eksik geçmiş kayıtları önce üret
        bugun = self._bugun()
        pencere_basi = bugun - timedelta(days=_TELAFI_PENCERE_GUN)
        return self._gorev.gecmis_bekleyenleri_amnesti(
            self._user_id, bugun, pencere_basi, self._saat.simdi()
        )

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

    def _gorev_serisi_isle(self, sablon, gun) -> None:
        """Göreve özel seri: önceki planlı oluşum tamamlandıysa +1, yoksa 1'e döner."""
        olusturma = Gun.olustur(sablon.created_at, self._gun_baslangic()).tarih
        onceki = onceki_olusum(
            Tekrar(sablon.recurrence), sablon.recurrence_param or "", olusturma, gun
        )
        if onceki is not None and sablon.streak_last_day == onceki:
            yeni_seri = sablon.streak_count + 1
        elif sablon.streak_count > 0 and self._dondurma.kullan():
            # Boşluk var ama bir dondurma harcanarak seri korunuyor.
            yeni_seri = sablon.streak_count + 1
        else:
            yeni_seri = 1
        self._gorev.gorev_serisi_guncelle(sablon.id, yeni_seri, gun)

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

        telafi_mi = kayit.day < self._bugun()  # geçmiş günü telafi ediyoruz
        odul = odul_hesapla(islenmis_saniye, ozel)
        kritik = self._sans.kritik_mi(KRITIK_OLASILIK)
        carpan = self._combo.carpan(simdi) * (KRITIK_CARPAN if kritik else 1)
        if telafi_mi:
            carpan *= TELAFI_CARPAN
        if carpan != 1.0:
            odul = Odul(xp=round(odul.xp * carpan), puan=round(odul.puan * carpan))
        ok = self._gorev.complete_instance(
            instance_id=kayit_id,
            committed_seconds=islenmis_saniye,
            reward_xp=odul.xp,
            reward_points=odul.puan,
            completed_at=simdi,
        )
        if not ok:
            return None

        # Seri yalnızca BUGÜNKÜ oluşum tamamlanınca ilerler; telafi (geçmiş gün)
        # ödül verir ama seriyi değiştirmez.
        if sablon is not None and sablon.recurrence != "none" and kayit.day == self._bugun():
            self._gorev_serisi_isle(sablon, kayit.day)

        self._defter.record(
            user_id=self._user_id,
            day=self._bugun(),
            source=_TAMAMLAMA_KAYNAGI,
            ref_id=kayit_id,
            xp=odul.xp,
            points=odul.puan,
            stat=sablon.stat if sablon is not None else None,
        )
        combo_tetik = self._combo.tamamlama_bildir(islenmis_saniye, simdi)
        self._rozet.tamamlama_arttir()
        if kritik:
            self._rozet.kritik_isaretle()
        if combo_tetik:
            self._rozet.combo_isaretle()
        self._olay_hatti.publish(
            TaskCompleted(
                occurred_at=simdi,
                instance_id=kayit_id,
                xp=odul.xp,
                points=odul.puan,
                kritik=kritik,
                combo_tetik=combo_tetik,
            )
        )
        self._seviye_dondurma_kontrol()
        return odul

    def gorev_sil(self, kayit_id: str) -> None:
        kayit = self._gorev.get_instance(kayit_id)
        if kayit is not None:
            self._gorev.deactivate_template(kayit.task_id)

    def sablon_sil(self, task_id: str) -> None:
        """'Tümü' görünümünden doğrudan tekrarlı görevi (şablonu) kaldırır."""
        self._gorev.deactivate_template(task_id)

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

    def _seviye_dondurma_kontrol(self) -> None:
        """XP kazanımından sonra profil seviyesi 3'ün katını geçtiyse dondurma ver."""
        profil, _ = self.profil_durumu()
        self._dondurma.seviye_odulu(profil)

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
        self._seviye_dondurma_kontrol()
