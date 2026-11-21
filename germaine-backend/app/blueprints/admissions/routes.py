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

import logging

from flask import current_app, request

from app.blueprints.admissions import admissions_bp
from app.services import application_service, lead_service, scholarship_service
from app.utils.rate_limit import SlidingWindowLimiter
from app.utils.responses import error, success
from app.utils.validation import ValidationError

log = logging.getLogger(__name__)

# Lead capture throttling (per worker process — see app/utils/rate_limit.py).
# The browser debounces and only sends when name+phone are valid and changed,
# so a real applicant sends a handful of requests per minute at most.
_lead_ip_limiter = SlidingWindowLimiter(max_events=30, window_seconds=60)
_lead_token_limiter = SlidingWindowLimiter(max_events=15, window_seconds=60)
_LEAD_MAX_BODY_BYTES = 4096


@admissions_bp.route("/applications", methods=["POST"])
def create_application():
    payload = request.get_json(silent=True) or {}
    application = application_service.create_application(payload)
    # Applicant lead linking runs only AFTER the application has been
    # committed, and can never fail or alter the submission: any error here
    # is logged and swallowed, and the applicant still gets their 201.
    try:
        lead_service.link_application(application, payload)
    except Exception:  # noqa: BLE001 — lead linking must never break a submission
        from app.extensions import db
        db.session.rollback()
        log.exception("Applicant lead linking failed for application id=%s", application.id)
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


@admissions_bp.route("/leads/capture", methods=["POST"])
def capture_lead():
    """Real-time applicant lead capture (apply.html, via assets/js/lead-capture.js).

    Public and unauthenticated by design, so it reveals nothing: the response
    never contains any lead data, id or whether the lead already existed.
    """
    if request.content_length is not None and request.content_length > _LEAD_MAX_BODY_BYTES:
        return error("Request too large.", status=413)
    raw = request.get_data(cache=True)
    if len(raw) > _LEAD_MAX_BODY_BYTES:
        return error("Request too large.", status=413)

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return error("Invalid request.", status=400)

    # remote_addr only: X-Forwarded-For is client-controlled and would let a
    # bot rotate its throttling key. Under cPanel/Passenger, REMOTE_ADDR is
    # the real client address.
    ip = request.remote_addr or "unknown"
    token = payload.get("lead_token") if isinstance(payload.get("lead_token"), str) else ""
    if not _lead_ip_limiter.hit(ip) or (token and not _lead_token_limiter.hit(token[:128])):
        return error("Too many requests. Please slow down.", status=429)

    # Honeypot: real browsers never fill this field (it isn't rendered).
    # Answer exactly like a success so bots learn nothing.
    if payload.get("website"):
        return success({"captured": True}, message="OK")

    try:
        lead_service.capture_lead(payload)
    except ValidationError as err:
        return error("Validation failed.", status=422, errors=err.errors)
    except Exception:  # noqa: BLE001
        current_app.logger.exception("Applicant lead capture failed")
        return error("Could not save right now.", status=503)
    return success({"captured": True}, message="OK")
