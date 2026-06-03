"""İlk açılış verisi.

Veritabanı boşken, varsayılan kullanıcı satırını oluşturur. Zaten varsa
hiçbir şey yapmaz (tekrar tekrar açılışta sorun olmaz).
"""

from __future__ import annotations

from sqlalchemy.orm import sessionmaker

from leveltodo.infrastructure.persistence.sqlite.models import DEFAULT_USER_ID, User
from leveltodo.shared.ids import new_id  # noqa: F401  (çoklu profil için ileride)


def ensure_default_user(session_factory: sessionmaker) -> None:
    with session_factory() as session:
        if session.get(User, DEFAULT_USER_ID) is None:
            session.add(User(id=DEFAULT_USER_ID, name="Oyuncu"))
            session.commit()
