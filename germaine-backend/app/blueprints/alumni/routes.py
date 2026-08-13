"""
Alumni blueprint (Step 5).

Exposes alumni registration (Step 2 §11), backed by
app/services/engagement_service.py.

IMPORTANT: alumni.html's real form has not been rewired to call this
blueprint — frontend integration remains a separate, future step.
"""

from flask import request

from app.blueprints.alumni import alumni_bp
from app.services import engagement_service
from app.utils.responses import success


@alumni_bp.route("/register", methods=["POST"])
def register_alumni():
    payload = request.get_json(silent=True) or {}
    row = engagement_service.register_alumni(payload)
    return success(
        {"id": row.id, "email": row.email},
        message="Alumni registration received.",
        status=201,
    )
