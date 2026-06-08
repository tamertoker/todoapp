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


@dataclass(frozen=True, slots=True)
class SeansSatiri:
    """Bir görevin tek bir kronometre seansı (görünüm için)."""

    seans_id: str
    baslangic: str  # "HH:MM"
    bitis: str | None  # "HH:MM" ya da None (hâlâ açık)
    sure: int  # saniye


_TELAFI_PENCERE_GUN = 21  # son 3 hafta içindeki kaçırılanlar telafi edilebilir
_SEANS_MIN_ODUL_SN = 60  # bu süreden kısa seanslar ödül vermez (spam önleme)


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
        stat_anahtarlari_getir=None,
        seans_repo=None,
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
        self._seans = seans_repo
        # Tüm stat anahtarları (yerleşik + özel). Verilmezse yalnızca yerleşik 4.
        self._stat_anahtarlari = stat_anahtarlari_getir or (lambda: [s.value for s in Stat])

    def _bugun(self):
        return Gun.olustur(self._saat.simdi(), self._gun_baslangic()).tarih

    def gorev_olustur(
        self,
        baslik: str,
        tekrar: Tekrar,
        ozel_odul: int | None = None,
        stat: str | Stat | None = None,
        parametre: str = "",
        tag_id: str | None = None,
        reminder: str | None = None,
    ) -> str:
        gorev_id = new_id()
        self._gorev.add_template(
            id=gorev_id,
            user_id=self._user_id,
            title=baslik.strip(),
            recurrence=tekrar.value,
            recurrence_param=parametre or None,
            reward_override=ozel_odul,
            stat=str(stat) if stat is not None else None,  # Stat(StrEnum) ya da özel id
            created_at=self._saat.simdi(),
            tag_id=tag_id,
            reminder=reminder,
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

    # — Seanslar (kronometre = ardışık seanslar; her durdurma süreye göre ödül) —
    def seans_baslat(self, instance_id: str) -> None:
        """Kronometreyi başlatır + açık bir seans açar. Başka çalışan görev varsa
        onun seansını kapatıp ödüllendirir (tek anda tek kronometre)."""
        simdi = self._saat.simdi()
        for r in self._gorev.calisan_kayitlar(self._user_id):
            if r.id != instance_id:
                self.seans_durdur(r.id)
        self._gorev.timer_baslat(instance_id, simdi)
        kayit = self._gorev.get_instance(instance_id)
        if self._seans is not None and kayit is not None and kayit.timer_running:
            self._seans.ac(
                id=new_id(),
                instance_id=instance_id,
                user_id=self._user_id,
                day=self._bugun(),
                start_at=simdi,
            )

    def seans_durdur(self, instance_id: str) -> Odul | None:
        """Kronometreyi durdurur, seansı kapatır ve seansın SÜRESİNE göre ödül verir
        (özel ödül seansta kullanılmaz). Kısa seans (<1 dk) ödülsüzdür."""
        kayit = self._gorev.get_instance(instance_id)
        if kayit is None or not kayit.timer_running or kayit.segment_started_at is None:
            return None
        simdi = self._saat.simdi()
        sure = max(0, int((simdi - kayit.segment_started_at).total_seconds()))
        self._gorev.timer_duraklat(instance_id, simdi)  # süreyi committed'a ekler, durdurur
        sablon = self._gorev.get_template(kayit.task_id)
        if sure < _SEANS_MIN_ODUL_SN:
            if self._seans is not None:
                self._seans.kapat(instance_id, simdi, sure, 0, 0)  # kısa seans: ödülsüz
            return None
        odul = odul_hesapla(sure, None)  # süre-temelli
        kritik = self._sans.kritik_mi(KRITIK_OLASILIK)
        carpan = self._combo.carpan(simdi) * (KRITIK_CARPAN if kritik else 1)
        if carpan != 1.0:
            odul = Odul(xp=round(odul.xp * carpan), puan=round(odul.puan * carpan))
        if self._seans is not None:
            self._seans.kapat(instance_id, simdi, sure, odul.xp, odul.puan)
        if (
            sablon is not None
            and sablon.recurrence != "none"
            and kayit.day == self._bugun()
            and self._seans is not None
            and self._seans.gun_seans_sayisi(instance_id, kayit.day) == 1
        ):
            self._gorev_serisi_isle(sablon, kayit.day)  # o günün ilk seansı → seri
        self._defter.record(
            user_id=self._user_id,
            day=self._bugun(),
            source="session",
            ref_id=instance_id,
            xp=odul.xp,
            points=odul.puan,
            stat=sablon.stat if sablon is not None else None,
        )
        combo_tetik = self._combo.tamamlama_bildir(sure, simdi)
        self._rozet.tamamlama_arttir()
        if kritik:
            self._rozet.kritik_isaretle()
        if combo_tetik:
            self._rozet.combo_isaretle()
        self._olay_hatti.publish(
            TaskCompleted(
                occurred_at=simdi,
                instance_id=instance_id,
                xp=odul.xp,
                points=odul.puan,
                kritik=kritik,
                combo_tetik=combo_tetik,
            )
        )
        self._seviye_dondurma_kontrol()
        return odul

    def seanslar(self, instance_id: str, gun=None) -> list[SeansSatiri]:
        if self._seans is None:
            return []
        g = gun or self._bugun()
        return [
            SeansSatiri(
                seans_id=s.id,
                baslangic=s.start_at.strftime("%H:%M"),
                bitis=s.end_at.strftime("%H:%M") if s.end_at is not None else None,
                sure=s.duration,
            )
            for s in self._seans.gun_seanslari(instance_id, g)
        ]

    def seans_sil(self, seans_id: str) -> None:
        """Seansı siler; süresini görevin toplamından düşer VE bu seansta kazanılan
        XP/Puan'ı ters kayıtla geri alır (tutarlılık)."""
        if self._seans is None:
            return
        s = self._seans.getir(seans_id)
        if s is None:
            return
        self._gorev.committed_ekle(s.instance_id, -s.duration)
        if s.reward_xp or s.reward_points:
            kayit = self._gorev.get_instance(s.instance_id)
            sablon = self._gorev.get_template(kayit.task_id) if kayit is not None else None
            self._defter.record(
                user_id=self._user_id,
                day=self._bugun(),
                source="session_revert",
                ref_id=s.instance_id,
                xp=-s.reward_xp,
                points=-s.reward_points,
                stat=sablon.stat if sablon is not None else None,
            )
        self._seans.seans_sil(seans_id)

    def _saat_birlestir(self, gun: date, hhmm: str) -> datetime | None:
        try:
            saat, dakika = hhmm.split(":")
            return datetime(gun.year, gun.month, gun.day, int(saat), int(dakika))
        except (ValueError, AttributeError):
            return None

    def seans_guncelle(self, seans_id: str, baslangic: str, bitis: str) -> bool:
        """Bir seansın başlangıç–bitiş saatini (HH:MM) değiştirir; süreyi ve görevin
        toplamını buna göre günceller. Geçersizse (bitiş ≤ başlangıç) False döner."""
        if self._seans is None:
            return False
        s = self._seans.getir(seans_id)
        if s is None:
            return False
        bas = self._saat_birlestir(s.day, baslangic)
        bit = self._saat_birlestir(s.day, bitis)
        if bas is None or bit is None or bit <= bas:
            return False
        yeni_sure = int((bit - bas).total_seconds())
        self._gorev.committed_ekle(s.instance_id, yeni_sure - s.duration)
        self._seans.guncelle(seans_id, bas, bit, yeni_sure)
        return True

    def seans_manuel_ekle(self, instance_id: str, baslangic: str, bitis: str) -> bool:
        """Elle (sonradan) bir seans ekler: verilen HH:MM aralığıyla, bugüne. Görevin
        toplamına süresini ekler. Geçersizse False."""
        if self._seans is None:
            return False
        gun = self._bugun()
        bas = self._saat_birlestir(gun, baslangic)
        bit = self._saat_birlestir(gun, bitis)
        if bas is None or bit is None or bit <= bas:
            return False
        sure = int((bit - bas).total_seconds())
        self._seans.ekle_kapali(
            id=new_id(),
            instance_id=instance_id,
            user_id=self._user_id,
            day=gun,
            start_at=bas,
            end_at=bit,
            duration=sure,
        )
        self._gorev.committed_ekle(instance_id, sure)
        return True

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

    def stat_durumlari_anahtar(self, anahtarlar: list[str]) -> dict[str, SeviyeDurumu]:
        """Verilen stat anahtarları (özel statlar dahil) için durum — tek sorguda."""
        toplamlar = self._defter.stat_xp_toplamlari(self._user_id)
        return {a: seviye_hesapla(toplamlar.get(a, 0)) for a in anahtarlar}

    def profil_durumu(self) -> tuple[int, UnvanDurumu]:
        """Profil seviyesi (TÜM stat seviyelerinin toplamı — özel statlar dahil)."""
        toplamlar = self._defter.stat_xp_toplamlari(self._user_id)
        profil = sum(
            seviye_hesapla(toplamlar.get(anahtar, 0)).seviye
            for anahtar in self._stat_anahtarlari()
        )
        return profil, unvan_hesapla(profil)

    def _seviye_dondurma_kontrol(self) -> None:
        """XP kazanımından sonra profil seviyesi 3'ün katını geçtiyse dondurma ver."""
        profil, _ = self.profil_durumu()
        self._dondurma.seviye_odulu(profil)

    def gelistirme_xp_ekle(self, stat: str | Stat, miktar: int) -> None:
        """Debug: bir stata doğrudan XP ekler (yalnızca geliştirme/test için)."""
        self._defter.record(
            user_id=self._user_id,
            day=self._bugun(),
            source="debug",
            ref_id=None,
            xp=miktar,
            points=0,
            stat=str(stat),
        )
        self._seviye_dondurma_kontrol()
