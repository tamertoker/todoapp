"""Gün sonu günlüğü veri deposu (günlük yazıları + kullanıcı soruları)."""

from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from leveltodo.infrastructure.persistence.sqlite.models import JournalEntry, ReflectionQuestion


class SqlGunlukRepository:
    def __init__(self, session_factory: sessionmaker) -> None:
        self._sf = session_factory

    # — Günlük yazıları —
    def gun_kaydi(self, user_id: str, day: date) -> JournalEntry | None:
        with self._sf() as s:
            stmt = select(JournalEntry).where(
                JournalEntry.user_id == user_id, JournalEntry.day == day
            )
            return s.scalar(stmt)

    def yaz(
        self,
        *,
        id: str,
        user_id: str,
        day: date,
        text: str,
        reward_xp: int,
        rewarded: bool,
    ) -> None:
        """Günlüğü ekler ya da üzerine yazar (gün başına tek satır)."""
        with self._sf() as s:
            kayit = s.scalar(
                select(JournalEntry).where(
                    JournalEntry.user_id == user_id, JournalEntry.day == day
                )
            )
            if kayit is None:
                s.add(
                    JournalEntry(
                        id=id,
                        user_id=user_id,
                        day=day,
                        text=text,
                        reward_xp=reward_xp,
                        rewarded=rewarded,
                    )
                )
            else:
                kayit.text = text
                kayit.reward_xp = reward_xp
                kayit.rewarded = rewarded
            s.commit()

    def odullu_gun_sayisi(self, user_id: str, haric_gun: date) -> int:
        """Şu an ödülü duran günlük günü sayısı (verilen gün hariç)."""
        with self._sf() as s:
            return int(
                s.scalar(
                    select(func.count())
                    .select_from(JournalEntry)
                    .where(
                        JournalEntry.user_id == user_id,
                        JournalEntry.rewarded.is_(True),
                        JournalEntry.day != haric_gun,
                    )
                )
            )

    def gecmis(self, user_id: str, limit: int = 60) -> list[JournalEntry]:
        """Dolu günlükler, günü azalan sırada."""
        with self._sf() as s:
            stmt = (
                select(JournalEntry)
                .where(JournalEntry.user_id == user_id, JournalEntry.text != "")
                .order_by(JournalEntry.day.desc())
                .limit(limit)
            )
            return list(s.scalars(stmt))

    # — Kullanıcının kendi yansıtma soruları —
    def aktif_sorular(self, user_id: str) -> list[ReflectionQuestion]:
        with self._sf() as s:
            stmt = (
                select(ReflectionQuestion)
                .where(
                    ReflectionQuestion.user_id == user_id,
                    ReflectionQuestion.is_active.is_(True),
                )
                .order_by(ReflectionQuestion.created_at)
            )
            return list(s.scalars(stmt))

    def soru_ekle(self, *, id: str, user_id: str, text: str) -> None:
        with self._sf() as s:
            s.add(ReflectionQuestion(id=id, user_id=user_id, text=text))
            s.commit()

    def soru_pasife_al(self, soru_id: str) -> None:
        with self._sf() as s:
            soru = s.get(ReflectionQuestion, soru_id)
            if soru is not None:
                soru.is_active = False
                s.commit()
