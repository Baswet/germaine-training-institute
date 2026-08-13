from flask import Blueprint

earncash_bp = Blueprint("earncash", __name__)

# Each import below registers its routes on earncash_bp. Split into one
# file per original build10/EarnCash/backend/routes/*.py module so the
# 1:1 mapping to the source project stays obvious.
from app.blueprints.earncash import auth_routes  # noqa: E402,F401
from app.blueprints.earncash import user_routes  # noqa: E402,F401
from app.blueprints.earncash import course_routes  # noqa: E402,F401
from app.blueprints.earncash import referral_routes  # noqa: E402,F401
from app.blueprints.earncash import withdrawal_routes  # noqa: E402,F401
from app.blueprints.earncash import notification_routes  # noqa: E402,F401
from app.blueprints.earncash import admin_routes  # noqa: E402,F401
