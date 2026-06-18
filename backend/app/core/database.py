"""Database engine, session factory, and a cross-database GUID column type.

Defaults to SQLite (zero setup) but works unchanged against Postgres — the only
db-specific detail (UUID storage) is abstracted by the ``GUID`` type below.
"""
from __future__ import annotations

import uuid
from collections.abc import Generator

from sqlalchemy import CHAR, create_engine
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.types import TypeDecorator

from .config import settings

# SQLite needs check_same_thread=False because the scheduler touches the DB from
# a background thread. Harmless for other drivers.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)


class Base(DeclarativeBase):
    pass


class GUID(TypeDecorator):
    """Platform-independent UUID.

    Uses Postgres' native UUID type when available, otherwise stores a 36-char
    string. Values are always returned to Python as ``str`` for consistent JSON.
    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=False))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return str(value)


def gen_uuid() -> str:
    return str(uuid.uuid4())


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
