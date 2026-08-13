from flask import Blueprint

enquiries_bp = Blueprint("enquiries", __name__)

from app.blueprints.enquiries import routes  # noqa: E402,F401  (registers routes on import)
