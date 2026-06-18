"""Alembic environment for NoYou.

Reads the database URL and ORM metadata straight from the application so there is
a single source of truth:

* ``settings.database_url`` (app.core.config) — supports SQLite for zero-config dev
  and Postgres in production; no URL is hard-coded in alembic.ini.
* ``Base.metadata`` (app.core.database) with every model imported via ``app.models``
  so autogenerate sees the full schema.

``render_as_batch=True`` is enabled so ALTER operations also work on SQLite, which
otherwise cannot ALTER columns in place.
"""
from __future__ import annotations

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Make the application package importable. ``prepend_sys_path = .`` in alembic.ini
# already puts backend/ on sys.path when Alembic is run from there; this import is
# what wires the app's settings + metadata into the migration environment.
from app.core.config import settings
from app.core.database import Base
import app.models  # noqa: F401  (registers every table on Base.metadata)

# Alembic Config object — provides access to values in alembic.ini.
config = context.config

# Inject the runtime database URL from app settings (alembic.ini leaves it blank).
config.set_main_option("sqlalchemy.url", settings.database_url)

# Configure Python logging from the .ini, if present.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for 'autogenerate' support.
target_metadata = Base.metadata


def render_item(type_, obj, autogen_context):
    """Render the custom ``GUID`` column type without an app-internal import.

    ``GUID`` is a SQLAlchemy ``TypeDecorator`` defined in ``app.core.database``.
    By default Alembic would emit ``app.core.database.GUID()`` in the migration
    but not add the matching import, raising ``NameError`` at upgrade time. We
    render it as the underlying portable storage type instead: Postgres' native
    UUID on Postgres, otherwise a 36-char string — exactly what ``GUID`` stores.
    This keeps migrations free of app imports and runnable on SQLite and Postgres.
    """
    from sqlalchemy.dialects.postgresql import UUID as PG_UUID

    from app.core.database import GUID

    if type_ == "type" and isinstance(obj, GUID):
        if autogen_context.dialect.name == "postgresql":
            autogen_context.imports.add(
                "from sqlalchemy.dialects.postgresql import UUID as PG_UUID"
            )
            return "PG_UUID(as_uuid=False)"
        return "sa.String(length=36)"
    # Returning False tells Alembic to fall back to its default rendering.
    return False


def _compare_type(context, inspected_column, metadata_column, inspected_type, metadata_type):
    """Treat the custom ``GUID`` type as unchanged.

    ``GUID`` stores as CHAR(36)/native UUID, so the reflected DB type differs from
    the ``GUID`` object in the model — without this, every autogenerate run emits a
    bogus ``VARCHAR -> GUID`` alter on every id/FK column. Returning False says "no
    change"; returning None defers to Alembic's default comparison for other types.
    """
    from app.core.database import GUID

    if isinstance(metadata_type, GUID):
        return False
    return None


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Emits SQL to the script output instead of connecting to a database. Useful for
    generating a migration SQL file to apply by hand.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=_compare_type,
        compare_server_default=True,
        render_as_batch=True,
        render_item=render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode against a live database connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=_compare_type,
            compare_server_default=True,
            render_as_batch=True,
            render_item=render_item,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
