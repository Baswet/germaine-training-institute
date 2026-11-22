from flask import Blueprint

public_bp = Blueprint("public", __name__)

from app.blueprints.public import routes  # noqa: E402,F401  (registers routes on import)
from app.blueprints.public import newsroom_routes  # noqa: E402,F401  (News & Events publication API)
