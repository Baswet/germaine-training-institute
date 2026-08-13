from flask import Blueprint

alumni_bp = Blueprint("alumni", __name__)

from app.blueprints.alumni import routes  # noqa: E402,F401  (registers routes on import)
