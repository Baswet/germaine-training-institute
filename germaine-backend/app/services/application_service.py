"""
Application service (Step 5).

Implements the workflow described in STEP-2-DATABASE-ARCHITECTURE.md §9:
applicants are matched primarily by their unique email address; an
application always references a programme and, only for AI Bootcamp
programmes, a programme mode. `reference_code` is generated independently
of the sequential id (app/utils/reference_code.py), never exposing it
publicly.

This service does NOT touch, replace, or call the existing frontend's
`fetch()` to germaineinstitute.com/application/clients/add — that
remains a separate, unresolved item (Step 2 §39 item E).
"""

from datetime import date, datetime

from app.extensions import db
from app.models import Applicant, Application, EarnCashUser, Programme, ProgrammeMode
from app.utils.reference_code import generate_reference_code
from app.utils.validation import NotFoundError, Validator, ValidationError

ALLOWED_APPLICATION_TYPES = {"scholarship", "general", "programme_inquiry"}
ALLOWED_STATUSES = {"submitted", "under_review", "offered", "enrolled", "rejected", "withdrawn"}
_MAX_REFERENCE_CODE_ATTEMPTS = 5


def create_application(payload: dict) -> Application:
    v = Validator()
    v.require(payload, "full_name", "Full name")
    v.max_length(payload, "full_name", 200, "Full name")
    v.require(payload, "email", "Email")
    v.email(payload, "email", "Email")
    v.max_length(payload, "email", 200, "Email")
    v.require(payload, "phone", "Phone")
    v.max_length(payload, "phone", 20, "Phone")
    v.require(payload, "programme_id", "Programme")
    v.is_bool(payload, "consent", "Consent")
    if "application_type" in payload and payload["application_type"] is not None:
        v.one_of(payload, "application_type", ALLOWED_APPLICATION_TYPES, "Application type")
    v.finish()

    programme = db.session.get(Programme, payload["programme_id"])
    if programme is None or not programme.is_active:
        raise NotFoundError(f"No active programme found with id {payload['programme_id']}.")

    # GTI-SCHOLARSHIP-ACADEMIC: the Full Scholarship (and the bursary letter
    # issued with it) is offered for Academic School programmes only, using
    # the existing classification programme_type == 'academic'. Applied only
    # when the request explicitly says "scholarship", so the general,
    # driving-school, AI-bootcamp and short-course flows are unaffected.
    if (payload.get("application_type") or "").strip().lower() == "scholarship" \
            and (programme.programme_type or "").strip().lower() != "academic":
        raise ValidationError({"programme_id": [
            "The Full Scholarship is available for Academic School programmes only. "
            "Please choose a course from one of the Academic Schools."
        ]})

    programme_mode = None
    programme_mode_id = payload.get("programme_mode_id")
    if programme_mode_id is not None:
        if programme.programme_type == "academic":
            raise ValidationError({"programme_mode_id": ["Academic programmes do not have selectable modes."]})
        programme_mode = db.session.get(ProgrammeMode, programme_mode_id)
        if programme_mode is None or programme_mode.programme_id != programme.id:
            raise ValidationError({"programme_mode_id": ["This mode does not belong to the selected programme."]})

    try:
        applicant = _get_or_create_applicant(payload)

        reference_code = _generate_unique_reference_code()

        application = Application(
            reference_code=reference_code,
            applicant_id=applicant.id,
            programme_id=programme.id,
            programme_mode_id=programme_mode.id if programme_mode else None,
            application_type=payload.get("application_type") or "scholarship",
            education_level=payload.get("education_level"),
            kcse_grade=payload.get("kcse_grade"),
            consent=bool(payload.get("consent", False)),
            status="submitted",
            referred_by_earncash_user_id=_resolve_referral(payload.get("referral_code")),
        )
        db.session.add(application)
        db.session.commit()
        return application
    except Exception:
        db.session.rollback()
        raise


def _resolve_referral(referral_code):
    """Best-effort EarnFastCash referral attribution (Part 1 of the
    EarnFastCash <-> GTI integration). A referral code is never required
    and an invalid/unknown one never blocks or errors the application —
    it simply results in no attribution, exactly like a visitor who
    arrived with no referral link at all. Only a real, active EarnCash
    user's id is ever stored; nothing is invented."""
    if not referral_code or not isinstance(referral_code, str):
        return None
    code = referral_code.strip().upper()
    if not code:
        return None
    referrer = EarnCashUser.query.filter_by(referral_code=code, status="active").first()
    return referrer.id if referrer else None


def _get_or_create_applicant(payload: dict) -> Applicant:
    """Matched primarily by unique email (Step 2 §9, corrected wording). Fills in
    previously-missing fields on an existing record; never overwrites fields that
    already have a value."""
    email = payload["email"].strip().lower()
    applicant = Applicant.query.filter_by(email=email).first()

    if applicant is None:
        applicant = Applicant(
            full_name=payload["full_name"],
            email=email,
            phone=payload["phone"],
            national_id=payload.get("national_id"),
            date_of_birth=_parse_date(payload.get("date_of_birth")),
            gender=payload.get("gender"),
            county=payload.get("county"),
        )
        db.session.add(applicant)
        db.session.flush()
        return applicant

    if not applicant.national_id and payload.get("national_id"):
        applicant.national_id = payload["national_id"]
    if not applicant.date_of_birth and payload.get("date_of_birth"):
        applicant.date_of_birth = _parse_date(payload.get("date_of_birth"))
    if not applicant.gender and payload.get("gender"):
        applicant.gender = payload["gender"]
    if not applicant.county and payload.get("county"):
        applicant.county = payload["county"]
    if payload.get("full_name"):
        applicant.full_name = payload["full_name"]
    if payload.get("phone"):
        applicant.phone = payload["phone"]

    db.session.flush()
    return applicant


def _parse_date(value):
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _generate_unique_reference_code() -> str:
    for _ in range(_MAX_REFERENCE_CODE_ATTEMPTS):
        code = generate_reference_code()
        if Application.query.filter_by(reference_code=code).first() is None:
            return code
    raise RuntimeError("Could not generate a unique reference code after several attempts.")


def get_application_by_reference_code(reference_code: str) -> Application:
    application = Application.query.filter_by(reference_code=reference_code).first()
    if application is None:
        raise NotFoundError(f"No application found with reference code '{reference_code}'.")
    return application


def application_to_dict(application: Application, include_applicant: bool = False) -> dict:
    data = {
        "reference_code": application.reference_code,
        "programme": {"slug": application.programme.slug, "name": application.programme.name},
        "programme_mode": application.programme_mode.mode_key if application.programme_mode else None,
        "application_type": application.application_type,
        "status": application.status,
        "submitted_at": application.submitted_at.isoformat() if application.submitted_at else None,
    }
    if include_applicant:
        data["applicant"] = {
            "full_name": application.applicant.full_name,
            "email": application.applicant.email,
        }
    return data
