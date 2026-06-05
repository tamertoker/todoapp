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
from leveltodo.application.dondurma_servisi import DondurmaServisi
from leveltodo.application.dusman_servisi import DusmanServisi
from leveltodo.application.gorev_servisi import GorevServisi
from leveltodo.application.gunluk_servisi import GunlukServisi
from leveltodo.application.irade_servisi import IradeServisi
from leveltodo.application.kronometre_servisi import KronometreServisi
from leveltodo.application.rozet_servisi import RozetServisi
from leveltodo.application.rutin_servisi import RutinServisi
from leveltodo.application.seri_servisi import SeriServisi
from leveltodo.application.settings_service import SettingsService
from leveltodo.domain.events import TaskCompleted
from leveltodo.domain.sans import Sans
from leveltodo.domain.time.saat import Saat
from leveltodo.infrastructure.backup.yedekleme import Yedekleyici, db_dosya_yolu
from leveltodo.infrastructure.config import paths
from leveltodo.infrastructure.eventbus.olay_hatti import OlayHatti
from leveltodo.infrastructure.notifications.plyer_kanali import plyer_kanali
from leveltodo.infrastructure.persistence.sqlite.bootstrap_data import ensure_default_user
from leveltodo.infrastructure.persistence.sqlite.engine import create_engine_and_factory
from leveltodo.infrastructure.persistence.sqlite.gunluk_repository import SqlGunlukRepository
from leveltodo.infrastructure.persistence.sqlite.irade_repository import SqlIradeRepository
from leveltodo.infrastructure.persistence.sqlite.ledger_repository import SqlLedgerRepository
from leveltodo.infrastructure.persistence.sqlite.migrations import upgrade_to_head
from leveltodo.infrastructure.persistence.sqlite.models import DEFAULT_USER_ID
from leveltodo.infrastructure.persistence.sqlite.rutin_repository import SqlRutinRepository
from leveltodo.infrastructure.persistence.sqlite.settings_repository import SqlSettingsRepository
from leveltodo.infrastructure.persistence.sqlite.streak_repository import SqlStreakRepository
from leveltodo.infrastructure.persistence.sqlite.task_repository import SqlTaskRepository
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
    kronometre: KronometreServisi
    seri: SeriServisi
    irade: IradeServisi
    rutin: RutinServisi
    gunluk: GunlukServisi
    yedekleyici: Yedekleyici
    bildirim: BildirimServisi


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
    dondurma = DondurmaServisi(settings)
    combo = ComboServisi(settings)
    rozet = RozetServisi(settings)
    dusman = DusmanServisi(settings, aktif_saat, lambda: settings.day_start_hour)
    # Görev tamamlanınca kazanılan XP kadar düşmana hasar (olay tabanlı).
    olay_hatti.subscribe(TaskCompleted, lambda olay: dusman.hasar_ver(olay.xp))

    gorev_repo = SqlTaskRepository(session_factory)
    defter_repo = SqlLedgerRepository(session_factory)
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
    )
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
        kronometre=kronometre,
        seri=seri,
        irade=irade,
        rutin=rutin,
        gunluk=gunluk,
        yedekleyici=yedekleyici,
        bildirim=bildirim,
    )
