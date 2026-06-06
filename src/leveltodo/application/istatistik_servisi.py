"""İstatistik servisi — grafik/ısı haritası/rekorlar için veriyi toplar.

Tek bir metrik seçici fikri: "xp", "calisma", "tamamlama" sabit metrikleri + her
sayısal/evet-hayır rutin alanı ("rutin:<id>") birer metriktir. Seçilen metrik ve
gün aralığı için günlük seri döner; ekran bunu ısı haritası ya da çizgi olarak
çizer. Ayrıca kişisel rekorları hesaplar. Saf application: PyQt bilmez.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from leveltodo.domain.rutinler.rutinler import RutinTuru
from leveltodo.domain.stats.statlar import STAT_ETIKET, Stat
from leveltodo.domain.time.gun import Gun
from leveltodo.domain.time.saat import Saat
from leveltodo.infrastructure.persistence.sqlite.ledger_repository import SqlLedgerRepository
from leveltodo.infrastructure.persistence.sqlite.models import DEFAULT_USER_ID
from leveltodo.infrastructure.persistence.sqlite.rutin_repository import SqlRutinRepository
from leveltodo.infrastructure.persistence.sqlite.streak_repository import SqlStreakRepository
from leveltodo.infrastructure.persistence.sqlite.task_repository import SqlTaskRepository

# Gün aralığı kipleri (gün sayısı; bugün dahil geriye)
ARALIK_GUN = {"hafta": 7, "ay": 30, "yil": 365}


@dataclass(frozen=True, slots=True)
class Metrik:
    anahtar: str
    etiket: str
    birim: str  # "XP", "dk", "adet", "" (rutin)


@dataclass(frozen=True, slots=True)
class Rekorlar:
    en_uzun_seri: int
    en_uretken_gun: tuple[date | None, int]
    en_uzun_kronometre_sn: int
    en_cok_gorev_gun: tuple[date | None, int]


class IstatistikServisi:
    def __init__(
        self,
        defter_repo: SqlLedgerRepository,
        gorev_repo: SqlTaskRepository,
        rutin_repo: SqlRutinRepository,
        streak_repo: SqlStreakRepository,
        saat: Saat,
        gun_baslangic_getir,
        user_id: str = DEFAULT_USER_ID,
    ) -> None:
        self._defter = defter_repo
        self._gorev = gorev_repo
        self._rutin = rutin_repo
        self._streak = streak_repo
        self._saat = saat
        self._gun_baslangic = gun_baslangic_getir
        self._user_id = user_id

    def bugun(self) -> date:
        return Gun.olustur(self._saat.simdi(), self._gun_baslangic()).tarih

    def gun_araligi(self, kip: str) -> tuple[date, date]:
        bit = self.bugun()
        bas = bit - timedelta(days=ARALIK_GUN.get(kip, 365) - 1)
        return bas, bit

    def metrik_secenekleri(self) -> list[Metrik]:
        secenekler = [
            Metrik("xp", "Günlük XP", "XP"),
            Metrik("calisma", "Çalışma süresi", "dk"),
            Metrik("tamamlama", "Tamamlanan görev", "adet"),
        ]
        for alan in self._rutin.aktif_alanlar(self._user_id):
            if alan.kind in (RutinTuru.SAYI.value, RutinTuru.EVET_HAYIR.value):
                secenekler.append(Metrik(f"rutin:{alan.id}", alan.name, ""))
        return secenekler

    def gunluk_seri(self, metrik: str, bas: date, bit: date) -> dict[date, int]:
        if metrik == "xp":
            return self._defter.gunluk_xp(self._user_id, bas, bit)
        if metrik == "calisma":
            ham = self._gorev.gunluk_calisma(self._user_id, bas, bit)
            return {gun: sn // 60 for gun, sn in ham.items()}  # dakika
        if metrik == "tamamlama":
            return self._gorev.gunluk_tamamlama(self._user_id, bas, bit)
        if metrik.startswith("rutin:"):
            return self._rutin.gunluk_degerler(metrik.split(":", 1)[1], bas, bit)
        return {}

    def stat_dagilimi(self) -> dict[str, int]:
        toplamlar = self._defter.stat_xp_toplamlari(self._user_id)
        return {STAT_ETIKET[s]: toplamlar.get(s.value, 0) for s in Stat}

    def rekorlar(self) -> Rekorlar:
        seri_best = max(
            (en_iyi for _, en_iyi in self._streak.hepsi(self._user_id).values()),
            default=0,
        )
        gorev_seri = self._gorev.en_uzun_gorev_serisi(self._user_id)
        return Rekorlar(
            en_uzun_seri=max(seri_best, gorev_seri),
            en_uretken_gun=self._defter.en_uretken_gun(self._user_id),
            en_uzun_kronometre_sn=self._gorev.en_uzun_kronometre(self._user_id),
            en_cok_gorev_gun=self._gorev.en_cok_gorev_gun(self._user_id),
        )
