"""Migration'ın temiz çalışıp tabloları oluşturduğunu doğrular."""

from sqlalchemy import create_engine, inspect

from leveltodo.infrastructure.persistence.sqlite.migrations import upgrade_to_head


def test_upgrade_creates_tables(db_url):
    upgrade_to_head(db_url)

    engine = create_engine(db_url)
    tables = set(inspect(engine).get_table_names())
    assert {"users", "settings"} <= tables
