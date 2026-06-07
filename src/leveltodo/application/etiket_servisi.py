"""Etiket (proje) servisi — görevlere takılan renkli etiketleri yönetir."""

from __future__ import annotations

from leveltodo.domain.etiket.etiket import renk_sec
from leveltodo.infrastructure.persistence.sqlite.etiket_repository import SqlEtiketRepository
from leveltodo.infrastructure.persistence.sqlite.models import DEFAULT_USER_ID, Tag
from leveltodo.shared.ids import new_id


class EtiketServisi:
    def __init__(self, etiket_repo: SqlEtiketRepository, user_id: str = DEFAULT_USER_ID) -> None:
        self._repo = etiket_repo
        self._user_id = user_id

    def etiketler(self) -> list[Tag]:
        return self._repo.aktif(self._user_id)

    def etiket_ekle(self, ad: str, renk: str | None = None) -> str | None:
        """Yeni etiket; renk verilmezse paletten sıradaki atanır. Etiket id'sini döner."""
        ad = ad.strip()
        if not ad:
            return None
        sira = self._repo.sonraki_sira(self._user_id)
        tag_id = new_id()
        self._repo.ekle(
            id=tag_id,
            user_id=self._user_id,
            name=ad,
            color=renk or renk_sec(sira - 1),
            sort_order=sira,
        )
        return tag_id

    def etiket_sil(self, tag_id: str) -> None:
        self._repo.pasife_al(tag_id)

    def etiket_getir(self, tag_id: str) -> Tag | None:
        return self._repo.getir(tag_id)
