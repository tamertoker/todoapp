"""
UYARI:
build_container'a db_url verilebilir (testler geçici bir veritabanı verir);
verilmezse uygulamanın gerçek veri dizinindeki veritabanı kullanılır.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker

from leveltodo.application.bildirim_servisi import BildirimServisi
from leveltodo.application.combo_servisi import ComboServisi
from leveltodo.application.cuzdan_servisi import CuzdanServisi
from leveltodo.application.dondurma_servisi import DondurmaServisi
from leveltodo.application.dusman_servisi import DusmanServisi
from leveltodo.application.etiket_servisi import EtiketServisi
from leveltodo.application.gorev_servisi import GorevServisi
from leveltodo.application.gunluk_servisi import GunlukServisi
from leveltodo.application.hatirlatma_servisi import HatirlatmaServisi
from leveltodo.application.irade_servisi import IradeServisi
from leveltodo.application.istatistik_servisi import IstatistikServisi
from leveltodo.application.kronometre_servisi import KronometreServisi
from leveltodo.application.magaza_servisi import MagazaServisi
from leveltodo.application.mentor_servisi import MentorServisi
from leveltodo.application.rozet_servisi import RozetServisi
from leveltodo.application.rutin_servisi import RutinServisi
from leveltodo.application.seri_servisi import SeriServisi
from leveltodo.application.settings_service import SettingsService
from leveltodo.application.stat_servisi import StatServisi
from leveltodo.application.uyandirma_servisi import UyandirmaServisi
from leveltodo.domain.events import TaskCompleted
from leveltodo.domain.sans import Sans
from leveltodo.domain.time.saat import Saat
from leveltodo.infrastructure.backup.yedekleme import Yedekleyici, db_dosya_yolu
from leveltodo.infrastructure.config import paths
from leveltodo.infrastructure.eventbus.olay_hatti import OlayHatti
from leveltodo.infrastructure.notifications.plyer_kanali import plyer_kanali
from leveltodo.infrastructure.persistence.sqlite.bootstrap_data import ensure_default_user
from leveltodo.infrastructure.persistence.sqlite.cuzdan_repository import SqlCuzdanRepository
from leveltodo.infrastructure.persistence.sqlite.engine import create_engine_and_factory
from leveltodo.infrastructure.persistence.sqlite.etiket_repository import SqlEtiketRepository
from leveltodo.infrastructure.persistence.sqlite.gunluk_repository import SqlGunlukRepository
from leveltodo.infrastructure.persistence.sqlite.irade_repository import SqlIradeRepository
from leveltodo.infrastructure.persistence.sqlite.ledger_repository import SqlLedgerRepository
from leveltodo.infrastructure.persistence.sqlite.magaza_repository import SqlMagazaRepository
from leveltodo.infrastructure.persistence.sqlite.migrations import upgrade_to_head
from leveltodo.infrastructure.persistence.sqlite.models import DEFAULT_USER_ID
from leveltodo.infrastructure.persistence.sqlite.rutin_repository import SqlRutinRepository
from leveltodo.infrastructure.persistence.sqlite.seans_repository import SqlSeansRepository
from leveltodo.infrastructure.persistence.sqlite.settings_repository import SqlSettingsRepository
from leveltodo.infrastructure.persistence.sqlite.stat_repository import SqlStatRepository
from leveltodo.infrastructure.persistence.sqlite.streak_repository import SqlStreakRepository
from leveltodo.infrastructure.persistence.sqlite.task_repository import SqlTaskRepository
from leveltodo.infrastructure.persistence.sqlite.uyandirma_repository import (
    SqlUyandirmaRepository,
)
from leveltodo.infrastructure.saat import AyarlanabilirSaat
from leveltodo.infrastructure.sans import GercekSans


@dataclass
class Container:
    saat: Saat
    olay_hatti: OlayHatti
    engine: Engine
    session_factory: sessionmaker
    settings: SettingsService
    dondurma: DondurmaServisi
    combo: ComboServisi
    dusman: DusmanServisi
    rozet: RozetServisi
    gorevler: GorevServisi
    etiket: EtiketServisi
    stat: StatServisi
    kronometre: KronometreServisi
    seri: SeriServisi
    irade: IradeServisi
    rutin: RutinServisi
    gunluk: GunlukServisi
    yedekleyici: Yedekleyici
    bildirim: BildirimServisi
    hatirlatma: HatirlatmaServisi
    mentor: MentorServisi
    uyandirma: UyandirmaServisi
    istatistik: IstatistikServisi
    cuzdan: CuzdanServisi
    magaza: MagazaServisi


def build_container(
    db_url: str | None = None, saat: Saat | None = None, sans: Sans | None = None
) -> Container:
    url = db_url or paths.db_url()

    # Motoru açmadan ÖNCE: bekleyen bir geri yükleme varsa veritabanını değiştir.
    db_dosyasi = db_dosya_yolu(url)
    Yedekleyici.bekleyen_geri_yukleme_uygula(db_dosyasi)

    upgrade_to_head(url)
    engine, session_factory = create_engine_and_factory(url)
    ensure_default_user(session_factory)

    olay_hatti = OlayHatti()
    aktif_saat = saat or AyarlanabilirSaat()
    aktif_sans = sans or GercekSans()

    settings_repo = SqlSettingsRepository(session_factory)
    settings = SettingsService(settings_repo, DEFAULT_USER_ID)
    dondurma = DondurmaServisi(settings, olay_hatti, aktif_saat)
    combo = ComboServisi(settings)
    rozet = RozetServisi(settings)
    dusman = DusmanServisi(
        settings, aktif_saat, lambda: settings.day_start_hour, olay_hatti
    )
    # Görev tamamlanınca kazanılan XP kadar düşmana hasar (olay tabanlı).
    olay_hatti.subscribe(TaskCompleted, lambda olay: dusman.hasar_ver(olay.xp))

    gorev_repo = SqlTaskRepository(session_factory)
    defter_repo = SqlLedgerRepository(session_factory)
    stat = StatServisi(SqlStatRepository(session_factory))
    seans_repo = SqlSeansRepository(session_factory)
    seans_repo.acik_seanslari_sil(DEFAULT_USER_ID)  # açılışta yarım kalan seansları temizle
    gorevler = GorevServisi(
        gorev_repo=gorev_repo,
        defter_repo=defter_repo,
        saat=aktif_saat,
        olay_hatti=olay_hatti,
        gun_baslangic_getir=lambda: settings.day_start_hour,
        dondurma=dondurma,
        sans=aktif_sans,
        combo=combo,
        rozet=rozet,
        stat_anahtarlari_getir=lambda: stat.anahtarlar(),
        seans_repo=seans_repo,
    )
    etiket = EtiketServisi(SqlEtiketRepository(session_factory))
    kronometre = KronometreServisi(gorev_repo, aktif_saat)

    streak_repo = SqlStreakRepository(session_factory)
    seri = SeriServisi(streak_repo, aktif_saat, lambda: settings.day_start_hour, dondurma)

    irade_repo = SqlIradeRepository(session_factory)
    irade = IradeServisi(
        irade_repo,
        defter_repo,
        aktif_saat,
        lambda: settings.day_start_hour,
        dondurma,
        lambda: gorevler.profil_durumu()[0],
    )

    rutin_repo = SqlRutinRepository(session_factory)
    rutin = RutinServisi(
        rutin_repo,
        defter_repo,
        aktif_saat,
        lambda: settings.day_start_hour,
        dondurma,
        lambda: gorevler.profil_durumu()[0],
    )

    gunluk_repo = SqlGunlukRepository(session_factory)
    gunluk = GunlukServisi(
        gunluk_repo,
        defter_repo,
        aktif_saat,
        lambda: settings.day_start_hour,
        dondurma,
        lambda: gorevler.profil_durumu()[0],
    )

    yedekleyici = Yedekleyici(db_dosyasi)

    bildirim = BildirimServisi(settings, aktif_saat)
    bildirim.kanal_ekle(plyer_kanali)  # OS bildirimi (best-effort)

    hatirlatma = HatirlatmaServisi(
        gorev_repo, bildirim, aktif_saat, lambda: settings.day_start_hour
    )

    uyandirma_repo = SqlUyandirmaRepository(session_factory)
    uyandirma = UyandirmaServisi(
        uyandirma_repo,
        defter_repo,
        settings,
        aktif_saat,
        lambda: settings.day_start_hour,
        dondurma,
        lambda: gorevler.profil_durumu()[0],
    )

    cuzdan_repo = SqlCuzdanRepository(session_factory)
    cuzdan = CuzdanServisi(cuzdan_repo, settings, aktif_saat, lambda: settings.day_start_hour)

    magaza_repo = SqlMagazaRepository(session_factory)
    magaza = MagazaServisi(magaza_repo, defter_repo, aktif_saat, lambda: settings.day_start_hour)

    istatistik = IstatistikServisi(
        defter_repo,
        gorev_repo,
        rutin_repo,
        streak_repo,
        aktif_saat,
        lambda: settings.day_start_hour,
        stat_listesi_getir=lambda: [(b.anahtar, b.etiket) for b in stat.tum_statlar()],
    )

    mentor = MentorServisi(
        defter_repo,
        dusman,
        gorevler,
        bildirim,
        settings,
        aktif_saat,
        lambda: settings.day_start_hour,
        aktif_sans,
    )

    return Container(
        saat=aktif_saat,
        olay_hatti=olay_hatti,
        engine=engine,
        session_factory=session_factory,
        settings=settings,
        dondurma=dondurma,
        combo=combo,
        dusman=dusman,
        rozet=rozet,
        gorevler=gorevler,
        etiket=etiket,
        stat=stat,
        kronometre=kronometre,
        seri=seri,
        irade=irade,
        rutin=rutin,
        gunluk=gunluk,
        yedekleyici=yedekleyici,
        bildirim=bildirim,
        hatirlatma=hatirlatma,
        mentor=mentor,
        uyandirma=uyandirma,
        istatistik=istatistik,
        cuzdan=cuzdan,
        magaza=magaza,
    )
