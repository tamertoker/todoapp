"""Görev şablonları ve görev kayıtları (instance) için veri deposu.

Okuma metotları, veritabanından çekilen kayıtları döndürür (yalnızca sütun
değerleri okunur, güvenli). Yazma metotları işi tek bir oturum içinde yapar:
kaydı bul, değiştir, kaydet.
"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import sessionmaker

from leveltodo.infrastructure.persistence.sqlite.models import Task, TaskInstance


class SqlTaskRepository:
    def __init__(self, session_factory: sessionmaker) -> None:
        self._sf = session_factory

    # — Şablonlar —
    def add_template(
        self,
        *,
        id: str,
        user_id: str,
        title: str,
        recurrence: str,
        recurrence_param: str | None,
        reward_override: int | None,
        stat: str | None,
        created_at: datetime,
    ) -> None:
        with self._sf() as s:
            s.add(
                Task(
                    id=id,
                    user_id=user_id,
                    title=title,
                    recurrence=recurrence,
                    recurrence_param=recurrence_param,
                    reward_override=reward_override,
                    stat=stat,
                    created_at=created_at,
                )
            )
            s.commit()

    def get_template(self, task_id: str) -> Task | None:
        with self._sf() as s:
            return s.get(Task, task_id)

    def deactivate_template(self, task_id: str) -> None:
        with self._sf() as s:
            task = s.get(Task, task_id)
            if task is not None:
                task.is_active = False
                s.commit()

    def aktif_tekrarli_sablonlar(self, user_id: str) -> list[Task]:
        """Tek seferlik olmayan (tekrar eden), aktif tüm görev şablonları."""
        with self._sf() as s:
            stmt = select(Task).where(
                Task.user_id == user_id,
                Task.is_active.is_(True),
                Task.recurrence != "none",
            )
            return list(s.scalars(stmt))

    # — Kayıtlar (instance) —
    def add_instance(
        self, *, id: str, task_id: str, user_id: str, day: date, title: str
    ) -> None:
        with self._sf() as s:
            s.add(TaskInstance(id=id, task_id=task_id, user_id=user_id, day=day, title=title))
            s.commit()

    def instance_exists(self, task_id: str, day: date) -> bool:
        with self._sf() as s:
            stmt = select(TaskInstance.id).where(
                TaskInstance.task_id == task_id, TaskInstance.day == day
            )
            return s.scalar(stmt) is not None

    def get_instance(self, instance_id: str) -> TaskInstance | None:
        with self._sf() as s:
            return s.get(TaskInstance, instance_id)

    def today_rows(self, user_id: str, day: date) -> list[tuple[TaskInstance, str, int]]:
        """Bugünün listesi. Her satır (kayıt, tekrar-tipi, göreve-özel-seri)."""
        with self._sf() as s:
            stmt = (
                select(TaskInstance, Task.recurrence, Task.streak_count)
                .join(Task, Task.id == TaskInstance.task_id)
                .where(
                    TaskInstance.user_id == user_id,
                    Task.is_active.is_(True),
                    or_(
                        and_(Task.recurrence != "none", TaskInstance.day == day),
                        and_(Task.recurrence == "none", TaskInstance.status == "pending"),
                    ),
                )
                .order_by(TaskInstance.status.desc(), TaskInstance.title)
            )
            return [(inst, rec, seri) for inst, rec, seri in s.execute(stmt).all()]

    def gorev_serisi_guncelle(self, task_id: str, yeni_seri: int, son_gun: date) -> None:
        with self._sf() as s:
            task = s.get(Task, task_id)
            if task is not None:
                task.streak_count = yeni_seri
                task.streak_last_day = son_gun
                s.commit()

    # — Telafi (catchup) —
    def done_instance_var_mi(self, task_id: str, day: date) -> bool:
        with self._sf() as s:
            stmt = select(TaskInstance.id).where(
                TaskInstance.task_id == task_id,
                TaskInstance.day == day,
                TaskInstance.status == "done",
            )
            return s.scalar(stmt) is not None

    def gecmis_bekleyen_satirlar(
        self, user_id: str, bugun: date, pencere_basi: date
    ) -> list[tuple[TaskInstance, str, int]]:
        """Geçmiş günlere ait, henüz yapılmamış tekrarlı görev kayıtları (telafi)."""
        with self._sf() as s:
            stmt = (
                select(TaskInstance, Task.recurrence, Task.streak_count)
                .join(Task, Task.id == TaskInstance.task_id)
                .where(
                    TaskInstance.user_id == user_id,
                    Task.is_active.is_(True),
                    Task.recurrence != "none",
                    TaskInstance.status == "pending",
                    TaskInstance.day < bugun,
                    TaskInstance.day >= pencere_basi,
                )
                .order_by(TaskInstance.day.desc(), TaskInstance.title)
            )
            return [(inst, rec, seri) for inst, rec, seri in s.execute(stmt).all()]

    def gecmis_bekleyenleri_amnesti(
        self, user_id: str, bugun: date, pencere_basi: date, simdi: datetime
    ) -> int:
        """Telafi penceresindeki tüm bekleyen geçmiş kayıtları ödülsüz 'yapıldı'
        işaretler (yük affı). Böylece listeden çıkar ve yeniden üretilmez."""
        with self._sf() as s:
            stmt = (
                select(TaskInstance)
                .join(Task, Task.id == TaskInstance.task_id)
                .where(
                    TaskInstance.user_id == user_id,
                    Task.is_active.is_(True),
                    Task.recurrence != "none",
                    TaskInstance.status == "pending",
                    TaskInstance.day < bugun,
                    TaskInstance.day >= pencere_basi,
                )
            )
            kayitlar = list(s.scalars(stmt))
            for inst in kayitlar:
                inst.status = "done"
                inst.reward_xp = 0
                inst.reward_points = 0
                inst.completed_at = simdi
                inst.timer_running = False
                inst.segment_started_at = None
            s.commit()
            return len(kayitlar)

    def complete_instance(
        self,
        *,
        instance_id: str,
        committed_seconds: int,
        reward_xp: int,
        reward_points: int,
        completed_at: datetime,
    ) -> bool:
        """Kaydı 'yapıldı' işaretler. Zaten yapılmışsa False döner (çift ödül yok)."""
        with self._sf() as s:
            inst = s.get(TaskInstance, instance_id)
            if inst is None or inst.status == "done":
                return False
            inst.status = "done"
            inst.committed_seconds = committed_seconds
            inst.reward_xp = reward_xp
            inst.reward_points = reward_points
            inst.completed_at = completed_at
            inst.timer_running = False
            inst.segment_started_at = None
            s.commit()
            return True

    # — İstatistik toplama —
    def gunluk_calisma(self, user_id: str, bas: date, bit: date) -> dict[date, int]:
        """Aralıktaki her gün için toplam çalışma saniyesi {gun: saniye}."""
        with self._sf() as s:
            stmt = (
                select(
                    TaskInstance.day,
                    func.coalesce(func.sum(TaskInstance.committed_seconds), 0),
                )
                .where(
                    TaskInstance.user_id == user_id,
                    TaskInstance.day >= bas,
                    TaskInstance.day <= bit,
                )
                .group_by(TaskInstance.day)
            )
            return {gun: int(sn) for gun, sn in s.execute(stmt).all()}

    def gunluk_tamamlama(self, user_id: str, bas: date, bit: date) -> dict[date, int]:
        """Aralıktaki her gün tamamlanan görev sayısı {gun: adet}."""
        with self._sf() as s:
            stmt = (
                select(TaskInstance.day, func.count())
                .where(
                    TaskInstance.user_id == user_id,
                    TaskInstance.status == "done",
                    TaskInstance.day >= bas,
                    TaskInstance.day <= bit,
                )
                .group_by(TaskInstance.day)
            )
            return {gun: int(adet) for gun, adet in s.execute(stmt).all()}

    def en_uzun_kronometre(self, user_id: str) -> int:
        with self._sf() as s:
            return int(
                s.scalar(
                    select(func.coalesce(func.max(TaskInstance.committed_seconds), 0)).where(
                        TaskInstance.user_id == user_id
                    )
                )
            )

    def en_uzun_gorev_serisi(self, user_id: str) -> int:
        with self._sf() as s:
            return int(
                s.scalar(
                    select(func.coalesce(func.max(Task.streak_count), 0)).where(
                        Task.user_id == user_id
                    )
                )
            )

    def en_cok_gorev_gun(self, user_id: str) -> tuple[date | None, int]:
        with self._sf() as s:
            stmt = (
                select(TaskInstance.day, func.count().label("c"))
                .where(TaskInstance.user_id == user_id, TaskInstance.status == "done")
                .group_by(TaskInstance.day)
                .order_by(func.count().desc())
                .limit(1)
            )
            satir = s.execute(stmt).first()
            return (satir[0], int(satir[1])) if satir else (None, 0)

    # — Kronometre —
    def calisan_kayitlar(self, user_id: str) -> list[TaskInstance]:
        with self._sf() as s:
            stmt = select(TaskInstance).where(
                TaskInstance.user_id == user_id, TaskInstance.timer_running.is_(True)
            )
            return list(s.scalars(stmt))

    def timer_baslat(self, kayit_id: str, simdi: datetime) -> None:
        with self._sf() as s:
            inst = s.get(TaskInstance, kayit_id)
            if inst is not None and inst.status == "pending" and not inst.timer_running:
                inst.timer_running = True
                inst.segment_started_at = simdi
                s.commit()

    def timer_duraklat(self, kayit_id: str, simdi: datetime) -> None:
        """Çalışan segmenti kaydedilmiş süreye ekler ve durdurur."""
        with self._sf() as s:
            inst = s.get(TaskInstance, kayit_id)
            if inst is not None and inst.timer_running and inst.segment_started_at is not None:
                inst.committed_seconds += max(
                    0, int((simdi - inst.segment_started_at).total_seconds())
                )
                inst.timer_running = False
                inst.segment_started_at = None
                s.commit()

    def timer_checkpoint(self, simdi: datetime, user_id: str) -> None:
        """Çalışan kronometrenin o ana kadarki süresini DB'ye yazar ama durdurmaz.
        Böylece çökme olursa en fazla son checkpoint'ten beri geçen süre kaybolur."""
        with self._sf() as s:
            stmt = select(TaskInstance).where(
                TaskInstance.user_id == user_id, TaskInstance.timer_running.is_(True)
            )
            for inst in s.scalars(stmt):
                if inst.segment_started_at is not None:
                    inst.committed_seconds += max(
                        0, int((simdi - inst.segment_started_at).total_seconds())
                    )
                    inst.segment_started_at = simdi
            s.commit()

    def timer_kurtar(self, user_id: str) -> int:
        """Açılışta yarım kalmış kronometreleri durdurur. Çökme/kapanma süresini
        sayamayacağımız için askıdaki segment atılır; kaydedilmiş süre korunur."""
        with self._sf() as s:
            stmt = select(TaskInstance).where(
                TaskInstance.user_id == user_id, TaskInstance.timer_running.is_(True)
            )
            kayitlar = list(s.scalars(stmt))
            for inst in kayitlar:
                inst.timer_running = False
                inst.segment_started_at = None
            s.commit()
            return len(kayitlar)
