"""
Central Flask extension instances.

These are created here, unbound, and attached to the app inside the
application factory (app/__init__.py::create_app). This avoids circular
imports between models, blueprints, and the factory.

IMPORTANT: db.create_all() is never called anywhere in this project.
Schema changes are managed exclusively through Flask-Migrate / Alembic
migrations, and no migration is run against a live database as part of
this Step 3 scaffold.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
