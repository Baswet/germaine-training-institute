"""
Admissions blueprint (Step 5).

Exposes the Applicant/Application workflow described in
STEP-2-DATABASE-ARCHITECTURE.md §9, backed by app/services/application_service.py
and app/services/scholarship_service.py.

IMPORTANT: no existing frontend form (apply.html, ai-bootcamp.html's
aiApplyForm) has been rewired to call this blueprint. These are new,
unused-by-the-frontend endpoints — connecting the existing forms to
them is a deliberately separate, future step (per Step 5 instructions,
frontend integration is out of scope here).
"""

from flask import request

from app.blueprints.admissions import admissions_bp
from app.services import application_service, scholarship_service
from app.utils.responses import success


@admissions_bp.route("/applications", methods=["POST"])
def create_application():
    payload = request.get_json(silent=True) or {}
    application = application_service.create_application(payload)
    return success(
        application_service.application_to_dict(application),
        message="Application submitted successfully.",
        status=201,
    )


@admissions_bp.route("/applications/<reference_code>", methods=["GET"])
def get_application_status(reference_code):
    """Read-only status lookup by reference_code, scoped to that one record —
    never a listing (Step 2 §32's "authenticated/applicant-facing" note)."""
    application = application_service.get_application_by_reference_code(reference_code)
    return success(application_service.application_to_dict(application))


@admissions_bp.route("/scholarship-info", methods=["GET"])
def get_scholarship_info():
    return success(scholarship_service.get_scholarship_info())
