"""SQLAlchemy taban sınıfı.

Tüm veritabanı tabloları bu Base'den türer. Alembic, tabloların şemasını
buradan toplanan bilgiyle (Base.metadata) takip eder.
"""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
