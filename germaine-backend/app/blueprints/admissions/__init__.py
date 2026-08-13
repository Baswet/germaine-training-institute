from flask import Blueprint

admissions_bp = Blueprint("admissions", __name__)

from app.blueprints.admissions import routes  # noqa: E402,F401  (registers routes on import)
