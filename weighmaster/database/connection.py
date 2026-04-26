"""Database engine and session factory."""
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

from weighmaster.config import DB_PATH
from weighmaster.database.models import Base

_engine = None
_SessionLocal = None


def init_db() -> None:
    global _engine, _SessionLocal
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    _engine = create_engine(
        f"sqlite:///{DB_PATH}",
        connect_args={"check_same_thread": False},
        echo=False,
    )

    @event.listens_for(_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(_engine)
    _run_lightweight_migrations()
    _SessionLocal = sessionmaker(
        bind=_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )

    _seed_if_needed()


def _run_lightweight_migrations() -> None:
    """Add newly introduced columns for existing SQLite databases."""
    if _engine is None:
        return

    def _has_column(conn, table: str, column: str) -> bool:
        rows = conn.exec_driver_sql(f"PRAGMA table_info({table})").fetchall()
        return any(row[1] == column for row in rows)

    needed = {
        "commodities": [
            "price_per_tonne REAL NOT NULL DEFAULT 0.0",
        ],
        "weigh_tickets": [
            "commodity_rate_per_tonne REAL NOT NULL DEFAULT 0.0",
            "commodity_value REAL",
            "oil_distance_km REAL NOT NULL DEFAULT 0.0",
            "oil_rate_per_km REAL NOT NULL DEFAULT 0.0",
            "oil_price REAL NOT NULL DEFAULT 0.0",
            "total_price REAL",
        ],
    }

    with _engine.begin() as conn:
        for table, defs in needed.items():
            for col_def in defs:
                col_name = col_def.split()[0]
                if not _has_column(conn, table, col_name):
                    conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {col_def}")


def _seed_if_needed() -> None:
    from weighmaster.database.seed import seed_commodities
    with get_session() as session:
        from weighmaster.database.models import Commodity
        if session.query(Commodity).count() == 0:
            seed_commodities(session)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    if _SessionLocal is None:
        raise RuntimeError("Database not initialised — call init_db() first")
    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
