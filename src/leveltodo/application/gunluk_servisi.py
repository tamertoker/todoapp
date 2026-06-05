"""Gün sonu günlüğü servisi.

Günde tek günlük (üzerine yazılır). Dolu kaydedilince Farkındalık statına XP
yazılır — gün başına bir kez; sonradan boşaltılırsa ters kayıtla geri alınır
(Rutin'deki kuralla aynı). XP miktarı artan eğriden gelir: ilk günlük TABAN,
her ek dolu günlük günüyle bir tık fazla. Bir günün ödülü ilk dolduruşunda
sabitlenir (boşaltıp tekrar doldurmada aynı kalır).

Her gün BİR yansıtma sorusu gösterilir: hazır havuz + kullanıcının kendi
soruları birleşip takvim gününe göre dönüşümlü seçilir.
"""

from __future__ import annotations

from dataclasses import dataclass

from leveltodo.application.dondurma_servisi import DondurmaServisi
from leveltodo.domain.gunluk.gunluk import HAVUZ, gunluk_odulu, gunun_sorusu
from leveltodo.domain.stats.statlar import Stat
from leveltodo.domain.time.gun import Gun
from leveltodo.domain.time.saat import Saat
from leveltodo.infrastructure.persistence.sqlite.gunluk_repository import SqlGunlukRepository
from leveltodo.infrastructure.persistence.sqlite.ledger_repository import SqlLedgerRepository
from leveltodo.infrastructure.persistence.sqlite.models import DEFAULT_USER_ID, ReflectionQuestion
from leveltodo.shared.ids import new_id

_GUNLUK_KAYNAGI = "journal"


@dataclass(frozen=True, slots=True)
class GunlukDurumu:
    """Günlük ekranının bugün için ihtiyaç duyduğu sade veri."""

    soru: str | None
    metin: str
    odul_verildi: bool


@dataclass(frozen=True, slots=True)
class GunlukOzeti:
    """Geçmiş listesinin bir satırı."""

    gun: str
    metin: str


class GunlukServisi:
    def __init__(
        self,
        gunluk_repo: SqlGunlukRepository,
        defter_repo: SqlLedgerRepository,
        saat: Saat,
        gun_baslangic_getir,
        dondurma: DondurmaServisi,
        profil_getir,
        user_id: str = DEFAULT_USER_ID,
    ) -> None:
        self._repo = gunluk_repo
        self._defter = defter_repo
        self._saat = saat
        self._gun_baslangic = gun_baslangic_getir
        self._dondurma = dondurma
        self._profil_getir = profil_getir
        self._user_id = user_id

    def _bugun(self):
        return Gun.olustur(self._saat.simdi(), self._gun_baslangic()).tarih

    def _sorular(self) -> list[str]:
        ek = [s.text for s in self._repo.aktif_sorular(self._user_id)]
        return list(HAVUZ) + ek

    def bugunku_gunluk(self) -> GunlukDurumu:
        gun = self._bugun()
        kayit = self._repo.gun_kaydi(self._user_id, gun)
        return GunlukDurumu(
            soru=gunun_sorusu(self._sorular(), gun),
            metin=kayit.text if kayit is not None else "",
            odul_verildi=kayit.rewarded if kayit is not None else False,
        )

    def _yaz(self, gun, metin: str, reward_xp: int, rewarded: bool) -> None:
        self._repo.yaz(
            id=new_id(),
            user_id=self._user_id,
            day=gun,
            text=metin,
            reward_xp=reward_xp,
            rewarded=rewarded,
        )

    def _defter_yaz(self, gun, xp: int) -> None:
        self._defter.record(
            user_id=self._user_id,
            day=gun,
            source=_GUNLUK_KAYNAGI,
            ref_id=None,
            xp=xp,
            points=0,
            stat=Stat.FARKINDALIK.value,
        )

    def kaydet(self, metin: str) -> bool:
        """Bugünün günlüğünü kaydeder (üzerine yazar) ve ödülü içerik durumuyla
        eşitler. Dolu+ilk kez → ödül ver (True); boşaldı+ödüllüydü → geri al."""
        metin = metin.strip()
        gun = self._bugun()
        onceki = self._repo.gun_kaydi(self._user_id, gun)
        zaten_odullu = onceki.rewarded if onceki is not None else False
        eski_odul = onceki.reward_xp if onceki is not None else 0
        dolu = bool(metin)

        if dolu and not zaten_odullu:
            odul = eski_odul or gunluk_odulu(
                self._repo.odullu_gun_sayisi(self._user_id, gun)
            )
            self._yaz(gun, metin, odul, rewarded=True)
            self._defter_yaz(gun, odul)
            self._dondurma.seviye_odulu(self._profil_getir())
            return True

        if not dolu and zaten_odullu:
            # Boşaldı → ödülü geri al; reward_xp saklı kalır (tekrar dolarsa aynı).
            self._yaz(gun, metin, eski_odul, rewarded=False)
            self._defter_yaz(gun, -eski_odul)
            return False

        # Ödül durumu değişmiyor (yeni ödül verilmedi); yalnızca metni güncelle.
        self._yaz(gun, metin, eski_odul, rewarded=zaten_odullu)
        return False

    def gecmis(self) -> list[GunlukOzeti]:
        return [
            GunlukOzeti(gun=str(k.day), metin=k.text)
            for k in self._repo.gecmis(self._user_id)
        ]

    # — Kullanıcı soruları —
    def kullanici_sorulari(self) -> list[ReflectionQuestion]:
        return self._repo.aktif_sorular(self._user_id)

    def soru_ekle(self, metin: str) -> None:
        metin = metin.strip()
        if metin:
            self._repo.soru_ekle(id=new_id(), user_id=self._user_id, text=metin)

    def soru_sil(self, soru_id: str) -> None:
        self._repo.soru_pasife_al(soru_id)
