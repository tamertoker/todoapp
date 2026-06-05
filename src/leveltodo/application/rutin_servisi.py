"""Rutin servisi.

Kullanıcının tanımladığı günlük ölçütleri (su, sayfa, spor…) yönetir: alan
ekle/sil, bugünün değerini gir. Bir alanın günlük hedefi tutturulduğunda — gün
başına en çok bir kez — o alana atanmış stata `reward_xp` kadar XP yazılır.
Ödül bir kez verildikten sonra değer düşse de geri alınmaz (defter bozulmaz).
"""

from __future__ import annotations

from dataclasses import dataclass

from leveltodo.application.dondurma_servisi import DondurmaServisi
from leveltodo.domain.rutinler.rutinler import RutinTuru, Yon, hedef_tuttu_mu
from leveltodo.domain.stats.statlar import Stat
from leveltodo.domain.time.gun import Gun
from leveltodo.domain.time.saat import Saat
from leveltodo.infrastructure.persistence.sqlite.ledger_repository import SqlLedgerRepository
from leveltodo.infrastructure.persistence.sqlite.models import DEFAULT_USER_ID
from leveltodo.infrastructure.persistence.sqlite.rutin_repository import SqlRutinRepository
from leveltodo.shared.ids import new_id

_RUTIN_KAYNAGI = "routine"


@dataclass(frozen=True, slots=True)
class RutinSatiri:
    """Ekranın bir rutin satırını çizmek için ihtiyaç duyduğu sade veri."""

    field_id: str
    ad: str
    tur: RutinTuru
    yon: Yon | None
    hedef: int | None
    stat: str
    odul_xp: int
    bugun_deger: int | None
    bugun_metin: str | None
    odul_verildi: bool


class RutinServisi:
    def __init__(
        self,
        rutin_repo: SqlRutinRepository,
        defter_repo: SqlLedgerRepository,
        saat: Saat,
        gun_baslangic_getir,
        dondurma: DondurmaServisi,
        profil_getir,
        user_id: str = DEFAULT_USER_ID,
    ) -> None:
        self._repo = rutin_repo
        self._defter = defter_repo
        self._saat = saat
        self._gun_baslangic = gun_baslangic_getir
        self._dondurma = dondurma
        self._profil_getir = profil_getir
        self._user_id = user_id

    def _bugun(self):
        return Gun.olustur(self._saat.simdi(), self._gun_baslangic()).tarih

    def alan_ekle(
        self,
        ad: str,
        tur: RutinTuru,
        stat: Stat | None = None,
        odul_xp: int = 0,
        yon: Yon | None = None,
        hedef: int | None = None,
    ) -> None:
        sayi = tur is RutinTuru.SAYI
        metin = tur is RutinTuru.METIN  # metin: hedefsiz/ödülsüz, sadece takip
        self._repo.alan_ekle(
            id=new_id(),
            user_id=self._user_id,
            name=ad.strip(),
            kind=tur.value,
            direction=(yon or Yon.EN_AZ).value if sayi else None,
            target=hedef if sayi else None,
            reward_xp=0 if metin else odul_xp,
            stat="" if metin else stat.value,
            sort_order=self._repo.sonraki_sira(self._user_id),
        )

    def alan_sil(self, field_id: str) -> None:
        """Alanı pasife alır — geçmiş değerler ve kazanılan XP bozulmaz."""
        self._repo.alan_pasife_al(field_id)

    def bugunku_alanlar(self) -> list[RutinSatiri]:
        gun = self._bugun()
        satirlar: list[RutinSatiri] = []
        for alan in self._repo.aktif_alanlar(self._user_id):
            kayit = self._repo.gun_kaydi(alan.id, gun)
            satirlar.append(
                RutinSatiri(
                    field_id=alan.id,
                    ad=alan.name,
                    tur=RutinTuru(alan.kind),
                    yon=Yon(alan.direction) if alan.direction else None,
                    hedef=alan.target,
                    stat=alan.stat,
                    odul_xp=alan.reward_xp,
                    bugun_deger=kayit.value if kayit is not None else None,
                    bugun_metin=kayit.value_text if kayit is not None else None,
                    odul_verildi=kayit.rewarded if kayit is not None else False,
                )
            )
        return satirlar

    def metin_gir(self, field_id: str, metin: str) -> None:
        """METIN alanının bugünkü notunu kaydeder (üzerine yazar). Ödül yok."""
        self._repo.deger_yaz(
            id=new_id(),
            field_id=field_id,
            user_id=self._user_id,
            day=self._bugun(),
            value=0,
            value_text=metin.strip(),
            rewarded=False,
        )

    def deger_gir(self, field_id: str, deger: int) -> bool:
        """Bugünün değerini kaydeder (üzerine yazar) ve ödülü hedef durumuyla
        eşitler: hedef ilk kez tutarsa ödül verir (True döner); hedef artık
        tutmuyorsa daha önce verilen ödülü ters kayıtla geri alır. 'Gün başına
        bir kez' korunur — hedef tutmaya devam ettiği sürece tekrar ödül yazmaz."""
        alan = self._repo.alan_getir(field_id)
        if alan is None:
            return False
        gun = self._bugun()
        onceki = self._repo.gun_kaydi(field_id, gun)
        zaten_odullu = onceki.rewarded if onceki is not None else False

        tutuyor = hedef_tuttu_mu(
            RutinTuru(alan.kind),
            deger,
            Yon(alan.direction) if alan.direction else None,
            alan.target,
        )
        self._repo.deger_yaz(
            id=new_id(),
            field_id=field_id,
            user_id=self._user_id,
            day=gun,
            value=deger,
            rewarded=tutuyor,
        )

        if tutuyor and not zaten_odullu:
            self._defter.record(
                user_id=self._user_id,
                day=gun,
                source=_RUTIN_KAYNAGI,
                ref_id=field_id,
                xp=alan.reward_xp,
                points=0,
                stat=alan.stat,
            )
            self._dondurma.seviye_odulu(self._profil_getir())
            return True
        if not tutuyor and zaten_odullu:
            # Hedef artık tutmuyor → daha önce verilen ödülü ters kayıtla geri al.
            self._defter.record(
                user_id=self._user_id,
                day=gun,
                source=_RUTIN_KAYNAGI,
                ref_id=field_id,
                xp=-alan.reward_xp,
                points=0,
                stat=alan.stat,
            )
        return False
