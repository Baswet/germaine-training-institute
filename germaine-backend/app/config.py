"""
Environment-variable-driven configuration.

No secrets, credentials, or connection strings are hardcoded anywhere in
this file. Real values are supplied via a local, git-ignored .env file
(see .env.example for the placeholder shape) and loaded by python-dotenv
in app/__init__.py before this module's classes are read.

Nothing in this file connects to a database. SQLALCHEMY_DATABASE_URI is
only ever *read* from the environment here — it is not created, seeded,
or migrated against as part of this scaffold.
"""

import os
from datetime import timedelta


def _normalized_database_url() -> str:
    """Read DATABASE_URL and make sure SQLAlchemy picks the psycopg (v3)
    dialect this project is actually built on, not psycopg2.

    requirements.txt only ever installs psycopg[binary] (v3) — psycopg2
    is never installed, deliberately, per API_DOCS.md/DEPLOYMENT.md. But
    a bare "postgresql://" URL (the format .env.production.example always
    documented as needing the "+psycopg" suffix, and the exact format
    Render's managed-Postgres "connectionString" property provides,
    unprefixed) makes SQLAlchemy default to the psycopg2 dialect and
    crash on import — the deploy actually hit this on Render. Rewriting
    only the scheme here means DATABASE_URL can be pasted verbatim from
    any Postgres host's dashboard (Render, Heroku-style, etc.) without
    everyone who ever sets it having to remember to hand-edit the URL.
    A URL that already specifies a driver (or isn't Postgres at all,
    e.g. the sqlite URI TestingConfig uses below) is left untouched.
    """
    url = os.environ.get("DATABASE_URL", "")
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


class BaseConfig:
    """Shared defaults. Subclassed per environment below."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "")

    SQLALCHEMY_DATABASE_URI = _normalized_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
    }

    JSON_SORT_KEYS = False

    # Governs whether service-layer / route error handlers may include
    # extra debug detail in JSON error responses. Always False outside
    # local development.
    DEBUG_ERRORS = False

    # Admin session cookie security (Step 7 §14U). HttpOnly + SameSite=Lax
    # by default in every environment; Secure (HTTPS-only) is forced on
    # everywhere except local development/testing, where there is no TLS.
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    DEBUG_ERRORS = True
    SESSION_COOKIE_SECURE = False  # no local HTTPS in dev


class TestingConfig(BaseConfig):
    """
    Used only by the automated test suite (tests/). Deliberately uses an
    in-memory SQLite URI purely so Flask-SQLAlchemy can be initialized
    and the app factory can be exercised without any network connection,
    credentials, or live PostgreSQL server.

    No table is ever created against this URI (db.create_all() is not
    called anywhere in this codebase) — it exists solely to satisfy
    SQLAlchemy's requirement for *some* configured URI at app-creation
    time.
    """

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "testing-secret-key-not-for-production"
    SESSION_COOKIE_SECURE = False  # Flask's test client does not use HTTPS


class ProductionConfig(BaseConfig):
    DEBUG = False


CONFIG_BY_NAME = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(env_name=None):
    """Resolve a config class from FLASK_ENV / an explicit name. Defaults to development."""
    env_name = env_name or os.environ.get("FLASK_ENV", "development")
    return CONFIG_BY_NAME.get(env_name, DevelopmentConfig)
