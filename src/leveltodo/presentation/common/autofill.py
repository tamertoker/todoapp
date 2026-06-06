"""Autofill — bir metin kutusuna önceki girişlerden öneri ve seçince doldurma.

Kullanıcı bir alana (ör. gelir açıklaması, görev başlığı) yazdıkça, daha önce
girdiği değerler aşağıda öneri olarak çıkar. Bir öneriye tıklayınca `secildi`
geri çağrısı tetiklenir; çağıran taraf o değere ait son kaydı bulup ilgili diğer
alanları (tutar, ayarlar…) doldurur. Öneri listesi `yenile()` ile tazelenir.
"""

from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtCore import QStringListModel, Qt
from PyQt6.QtWidgets import QCompleter, QLineEdit


class AutoFill:
    def __init__(
        self,
        alan: QLineEdit,
        oneri_getir: Callable[[], list[str]],
        secildi: Callable[[str], None] | None = None,
    ) -> None:
        self._oneri_getir = oneri_getir
        self._comp = QCompleter(alan)
        self._comp.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._comp.setFilterMode(Qt.MatchFlag.MatchContains)
        self._comp.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        alan.setCompleter(self._comp)
        if secildi is not None:
            self._comp.activated.connect(secildi)
        self.yenile()

    def yenile(self) -> None:
        self._comp.setModel(QStringListModel(self._oneri_getir(), self._comp))
