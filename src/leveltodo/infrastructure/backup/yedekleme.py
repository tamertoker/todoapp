"""Veri yedekleme ve geri yükleme.

Tüm veri tek bir SQLite dosyasında (leveltodo.db) yaşar. İki yedek biçimi:
- **SQLite kopyası**: dosyanın birebir kopyası — tam sadakatli, geri yüklenebilir.
- **JSON dışa aktarma**: insan-okur, taşınabilir; inceleme/arşiv için (geri yükleme
  SQLite kopyasından yapılır).

Geri yükleme sorunu: uygulama çalışırken veritabanı dosyası açıktır (Windows'ta
kilitli). Çözüm: geri yüklenecek dosya `<db>.restore` olarak işaretlenir; uygulama
bir sonraki açılışında, motoru açmadan ÖNCE bu işareti yerine koyar. Böylece kilit
çakışması olmaz.
"""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
from pathlib import Path

RESTORE_EKI = ".restore"
_URL_ONEK = "sqlite:///"


def db_dosya_yolu(url: str) -> str:
    """'sqlite:///C:/.../x.db' → 'C:/.../x.db'."""
    return url[len(_URL_ONEK):] if url.startswith(_URL_ONEK) else url


class Yedekleyici:
    def __init__(self, db_path: str) -> None:
        self._db = Path(db_path)

    def sqlite_yedek_al(self, hedef: str) -> Path:
        h = Path(hedef)
        h.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self._db, h)
        return h

    def json_disa_aktar(self, hedef: str) -> Path:
        h = Path(hedef)
        h.parent.mkdir(parents=True, exist_ok=True)
        h.write_text(
            json.dumps(self._tum_tablolar(), ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        return h

    def _tum_tablolar(self) -> dict[str, list[dict]]:
        con = sqlite3.connect(self._db)
        con.row_factory = sqlite3.Row
        try:
            tablolar = [
                r[0]
                for r in con.execute(
                    "SELECT name FROM sqlite_master "
                    "WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
            ]
            return {t: [dict(r) for r in con.execute(f'SELECT * FROM "{t}"')] for t in tablolar}
        finally:
            con.close()

    def geri_yukle_isaretle(self, kaynak: str) -> None:
        """Verilen yedek dosyasını bir sonraki açılışta yüklenmek üzere işaretler."""
        if not self._gecerli_yedek(kaynak):
            raise ValueError("Geçersiz yedek dosyası: bu bir LevelTodo veritabanı değil.")
        shutil.copy2(kaynak, str(self._db) + RESTORE_EKI)

    @staticmethod
    def _gecerli_yedek(path: str) -> bool:
        if not Path(path).is_file():
            return False
        try:
            con = sqlite3.connect(path)
            try:
                adlar = {
                    r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")
                }
            finally:
                con.close()
        except sqlite3.DatabaseError:
            return False
        return "users" in adlar or "alembic_version" in adlar

    @staticmethod
    def bekleyen_geri_yukleme_uygula(db_path: str) -> bool:
        """Açılışta (motor açılmadan önce) çağrılır: bekleyen geri yükleme varsa
        veritabanı dosyasının yerine koyar. Yüklendiyse True döner."""
        isaret = Path(str(db_path) + RESTORE_EKI)
        if isaret.exists():
            os.replace(isaret, db_path)  # atomik, varsa üzerine yazar
            return True
        return False
