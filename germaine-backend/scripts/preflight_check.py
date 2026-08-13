"""
Startup preflight check used by start-admin.ps1.

Run as: python scripts/preflight_check.py

Performs, in order, exactly the two safety checks the one-click startup
script needs before it is allowed to launch Flask:

  1. A lightweight PostgreSQL connectivity check (a single "SELECT 1",
     never a real query against application tables).
  2. A migration-state check: is the database's current Alembic
     revision the same as the latest migration file on disk?

This script never creates, alters, or drops anything. It is read-only
end to end. Output is a single machine-readable line on stdout so the
calling PowerShell script doesn't have to parse Flask/Alembic log
formatting, which can change between versions:

  NO_DATABASE_URL
      DATABASE_URL is not set in the environment/.env.

  DB_UNAVAILABLE
      Could not open a connection to the configured database.

  MIGRATIONS_PENDING <current_revision_or_none> <head_revision>
      Database is reachable, but its current Alembic revision does not
      match the latest migration file.

  OK <revision>
      Database is reachable and its schema matches the latest
      migration file exactly.

Exit codes: 0 = OK, 2 = NO_DATABASE_URL, 3 = DB_UNAVAILABLE,
4 = MIGRATIONS_PENDING.
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

if not DATABASE_URL:
    print("NO_DATABASE_URL")
    sys.exit(2)

try:
    from sqlalchemy import create_engine, text
except Exception:
    # SQLAlchemy itself isn't importable — treat the same as an
    # unreachable database rather than letting an ImportError traceback
    # leak to the console.
    print("DB_UNAVAILABLE")
    sys.exit(3)

try:
    # "connect_timeout" is a psycopg/libpq-specific connect() keyword —
    # only pass it for postgres URLs so this preflight check itself
    # stays portable (e.g. against a sqlite URL in tests) instead of
    # raising a driver-level TypeError that would be indistinguishable
    # from a real "database unavailable" failure.
    connect_args = {"connect_timeout": 5} if DATABASE_URL.startswith("postgresql") else {}
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
    connection = engine.connect()
except Exception:
    print("DB_UNAVAILABLE")
    sys.exit(3)

try:
    connection.execute(text("SELECT 1"))

    from alembic.runtime.migration import MigrationContext
    from alembic.script import ScriptDirectory
    from alembic.config import Config as AlembicConfig

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    alembic_cfg = AlembicConfig(os.path.join(project_root, "migrations", "alembic.ini"))
    alembic_cfg.set_main_option("script_location", os.path.join(project_root, "migrations"))

    script_dir = ScriptDirectory.from_config(alembic_cfg)
    head_revision = script_dir.get_current_head()

    migration_ctx = MigrationContext.configure(connection)
    current_revision = migration_ctx.get_current_revision()

    if current_revision == head_revision:
        print(f"OK {current_revision}")
        sys.exit(0)
    else:
        print(f"MIGRATIONS_PENDING {current_revision or 'none'} {head_revision}")
        sys.exit(4)
finally:
    connection.close()
