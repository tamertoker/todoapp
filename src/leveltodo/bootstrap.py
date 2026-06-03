"""Bağımlılıkları birleştirme noktası (composition root).

Uygulamanın tüm parçaları burada elle birbirine bağlanır: veritabanı, saat,
olay veriyolu, ayar servisi. Ayrı bir DI framework'ü yoktur — yapıcıları
(constructor) elle çağırmak bu ölçek için yeterli ve en sade yol.

build_container'a db_url verilebilir (testler geçici bir veritabanı verir);
verilmezse uygulamanın gerçek veri dizinindeki veritabanı kullanılır.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker

from leveltodo.application.settings_service import SettingsService
from leveltodo.domain.time.clock import IClock
from leveltodo.infrastructure.clock import SystemClock
from leveltodo.infrastructure.config import paths
from leveltodo.infrastructure.eventbus.bus import EventBus
from leveltodo.infrastructure.persistence.sqlite.bootstrap_data import ensure_default_user
from leveltodo.infrastructure.persistence.sqlite.engine import create_engine_and_factory
from leveltodo.infrastructure.persistence.sqlite.migrations import upgrade_to_head
from leveltodo.infrastructure.persistence.sqlite.models import DEFAULT_USER_ID
from leveltodo.infrastructure.persistence.sqlite.settings_repository import SqlSettingsRepository


@dataclass
class Container:
    clock: IClock
    event_bus: EventBus
    engine: Engine
    session_factory: sessionmaker
    settings: SettingsService


def build_container(db_url: str | None = None, clock: IClock | None = None) -> Container:
    url = db_url or paths.db_url()

    upgrade_to_head(url)
    engine, session_factory = create_engine_and_factory(url)
    ensure_default_user(session_factory)

    settings_repo = SqlSettingsRepository(session_factory)
    settings = SettingsService(settings_repo, DEFAULT_USER_ID)

    return Container(
        clock=clock or SystemClock(),
        event_bus=EventBus(),
        engine=engine,
        session_factory=session_factory,
        settings=settings,
    )
