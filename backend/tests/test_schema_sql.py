from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]


def test_schema_sql_contains_mvp_tables():
    schema_sql = (BACKEND_DIR / "schema.sql").read_text(encoding="utf-8")

    assert "CREATE TABLE IF NOT EXISTS complaints" in schema_sql
    assert "CREATE TABLE IF NOT EXISTS events" in schema_sql
    assert "CREATE TABLE IF NOT EXISTS plugins" in schema_sql


def test_initial_migration_contains_mvp_tables():
    migration_sql = (BACKEND_DIR / "migrations" / "0001_mvp_schema.sql").read_text(
        encoding="utf-8"
    )

    assert "CREATE TABLE IF NOT EXISTS complaints" in migration_sql
    assert "CREATE TABLE IF NOT EXISTS events" in migration_sql
    assert "CREATE TABLE IF NOT EXISTS plugins" in migration_sql
