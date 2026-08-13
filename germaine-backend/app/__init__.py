"""
Flask application factory.

create_app() builds and returns a configured Flask app. It does NOT:
  - call db.create_all()
  - connect to or query a live database
  - run any migration
  - seed any data
  - import any existing frontend data file (school-data.js, ai-courses-data.js)
  - touch, rewire, or redesign any existing HTML/CSS/JS in build10/

It DOES:
  - load environment variables from a local .env (if present)
  - select config by FLASK_ENV (development/testing/production)
  - initialize db (Flask-SQLAlchemy) and migrate (Flask-Migrate) against the app
  - import app.models so all 19 model classes are registered on db.metadata
    (15 Step-2 baseline + 4 Step-7 CMS addition)
  - register the 5 blueprints (public, admissions, alumni, enquiries, admin)
  - register centralized JSON error handlers
"""

import os

from flask import Flask
from dotenv import load_dotenv

# Load .env BEFORE importing config.py, because config.py reads
# DATABASE_URL when it is imported.
load_dotenv()

from app.config import get_config
from app.extensions import db, migrate


def create_app(config_name: str | None = None) -> Flask:
    # Load .env before reading any environment-derived config. Safe to call
    # even if no .env file exists (python-dotenv no-ops in that case).
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(get_config(config_name or os.environ.get("FLASK_ENV")))

    # Fail loudly instead of silently starting with an insecure session
    # signing key. SECRET_KEY defaults to "" in BaseConfig (app/config.py)
    # so this scaffold never has to fabricate a real one — but running
    # with an empty SECRET_KEY outside testing means Flask's signed
    # session cookies (admin login relies on these) are trivially
    # forgeable. TestingConfig always sets its own fixed test key, so
    # this only ever fires for development/production when .env is
    # missing or incomplete.
    if not app.config.get("TESTING") and not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "SECRET_KEY is not set. Copy .env.example to .env and set a "
            "long random value before starting the server — the admin "
            "login's session security depends on it."
        )

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Import registers all 19 models against db.metadata (15 Step-2
        # baseline + 4 Step-7 CMS addition). This is an import only — no
        # query, no create_all(), no connection is made.
        from app import models  # noqa: F401

    _register_blueprints(app)

    from app.utils.errors import register_error_handlers
    register_error_handlers(app)

    from app.utils.cors import register_cors
    register_cors(app)

    from app.cli import register_cli
    register_cli(app)

    return app


def _register_blueprints(app: Flask) -> None:
    from app.blueprints.public import public_bp
    from app.blueprints.admissions import admissions_bp
    from app.blueprints.alumni import alumni_bp
    from app.blueprints.enquiries import enquiries_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.earncash import earncash_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admissions_bp, url_prefix="/api/admissions")
    app.register_blueprint(alumni_bp, url_prefix="/api/alumni")
    app.register_blueprint(enquiries_bp, url_prefix="/api/enquiries")
    # Step 7: server-rendered staff admin portal — HTML pages for humans,
    # not a JSON API, so it deliberately lives outside the "/api/" public
    # namespace. See app/blueprints/admin/routes.py's module docstring.
    app.register_blueprint(admin_bp, url_prefix="/admin")
    # EarnCash integration: previously a fully separate Flask+MySQL app
    # (build10/EarnCash/backend/), now mounted here as its own JSON API
    # namespace so it shares this one server/port/database instead of
    # colliding with it. Its own JWT auth (app/utils/earncash_jwt.py) is
    # unrelated to admin_bp's session-cookie auth above.
    app.register_blueprint(earncash_bp, url_prefix="/api/earncash")
