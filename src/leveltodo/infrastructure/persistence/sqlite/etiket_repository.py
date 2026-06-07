"""Etiket (proje) veri deposu."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from leveltodo.infrastructure.persistence.sqlite.models import Tag


class SqlEtiketRepository:
    def __init__(self, session_factory: sessionmaker) -> None:
        self._sf = session_factory

    def ekle(self, *, id: str, user_id: str, name: str, color: str, sort_order: int) -> None:
        with self._sf() as s:
            s.add(Tag(id=id, user_id=user_id, name=name, color=color, sort_order=sort_order))
            s.commit()

    def aktif(self, user_id: str) -> list[Tag]:
        with self._sf() as s:
            stmt = (
                select(Tag)
                .where(Tag.user_id == user_id, Tag.is_active.is_(True))
                .order_by(Tag.sort_order, Tag.created_at)
            )
            return list(s.scalars(stmt))

    def getir(self, tag_id: str) -> Tag | None:
        with self._sf() as s:
            return s.get(Tag, tag_id)

    def pasife_al(self, tag_id: str) -> None:
        with self._sf() as s:
            tag = s.get(Tag, tag_id)
            if tag is not None:
                tag.is_active = False
                s.commit()

    def sonraki_sira(self, user_id: str) -> int:
        with self._sf() as s:
            enbuyuk = s.scalar(select(func.max(Tag.sort_order)).where(Tag.user_id == user_id))
            return (enbuyuk or 0) + 1
