from flask import Blueprint

admin_bp = Blueprint("admin", __name__)

from app.blueprints.admin import routes  # noqa: E402,F401  (registers routes on import)
from app.blueprints.admin import cms_routes  # noqa: E402,F401  (Step 7 CMS: content/news/media/academics routes)
