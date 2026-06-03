"""Test ortak ayarları.

- Qt'yi başsız (headless) çalıştırmak için offscreen platformu seçilir; böylece
  testler ekran açmadan, Codespaces dahil her yerde koşar.
- db_url fixture'ı her teste geçici, izole bir SQLite veritabanı verir; gerçek
  kullanıcı verisine asla dokunulmaz.
"""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest


@pytest.fixture
def db_url(tmp_path) -> str:
    return f"sqlite:///{tmp_path / 'test.db'}"
