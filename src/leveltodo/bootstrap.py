"""Bağımlılıkları birleştirme noktası (composition root).

Uygulamanın tüm parçaları burada elle birbirine bağlanır: veritabanı, saat,
olay hattı, ayar servisi, görev servisi. Ayrı bir DI framework'ü yoktur —
yapıcıları (constructor) elle çağırmak bu ölçek için yeterli ve en sade yol.

build_container'a db_url verilebilir (testler geçici bir veritabanı verir);
verilmezse uygulamanın gerçek veri dizinindeki veritabanı kullanılır.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker

from leveltodo.application.gorev_servisi import GorevServisi
from leveltodo.application.kronometre_servisi import KronometreServisi
from leveltodo.application.settings_service import SettingsService
from leveltodo.domain.time.saat import Saat
from leveltodo.infrastructure.config import paths
from leveltodo.infrastructure.eventbus.olay_hatti import OlayHatti
from leveltodo.infrastructure.persistence.sqlite.bootstrap_data import ensure_default_user
from leveltodo.infrastructure.persistence.sqlite.engine import create_engine_and_factory
from leveltodo.infrastructure.persistence.sqlite.ledger_repository import SqlLedgerRepository
from leveltodo.infrastructure.persistence.sqlite.migrations import upgrade_to_head
from leveltodo.infrastructure.persistence.sqlite.models import DEFAULT_USER_ID
from leveltodo.infrastructure.persistence.sqlite.settings_repository import SqlSettingsRepository
from leveltodo.infrastructure.persistence.sqlite.task_repository import SqlTaskRepository
from leveltodo.infrastructure.saat import AyarlanabilirSaat


@dataclass
class Container:
    saat: Saat
    olay_hatti: OlayHatti
    engine: Engine
    session_factory: sessionmaker
    settings: SettingsService
    gorevler: GorevServisi
    kronometre: KronometreServisi


def build_container(db_url: str | None = None, saat: Saat | None = None) -> Container:
    url = db_url or paths.db_url()

    upgrade_to_head(url)
    engine, session_factory = create_engine_and_factory(url)
    ensure_default_user(session_factory)

    olay_hatti = OlayHatti()
    aktif_saat = saat or AyarlanabilirSaat()

    settings_repo = SqlSettingsRepository(session_factory)
    settings = SettingsService(settings_repo, DEFAULT_USER_ID)

    gorev_repo = SqlTaskRepository(session_factory)
    defter_repo = SqlLedgerRepository(session_factory)
    gorevler = GorevServisi(
        gorev_repo=gorev_repo,
        defter_repo=defter_repo,
        saat=aktif_saat,
        olay_hatti=olay_hatti,
        gun_baslangic_getir=lambda: settings.day_start_hour,
    )
    kronometre = KronometreServisi(gorev_repo, aktif_saat)

    return Container(
        saat=aktif_saat,
        olay_hatti=olay_hatti,
        engine=engine,
        session_factory=session_factory,
        settings=settings,
        gorevler=gorevler,
        kronometre=kronometre,
    )
