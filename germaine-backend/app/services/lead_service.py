"""
Applicant lead service — real-time lead capture, application linking, and
admin follow-up management.

Public side (capture_lead / link_application) is called from the admissions
blueprint. It never returns lead data to the public caller.

Identity and deduplication
--------------------------
  * A lead is identified ONLY by its browser lead token (SHA-256 stored,
    UNIQUE). The insert uses INSERT .. ON CONFLICT DO NOTHING followed by a
    row lock (SELECT .. FOR UPDATE on PostgreSQL), so any number of
    simultaneous/retried requests for one token converge on one row.
  * Phone number and name are never used to merge two tokens: two browsers
    typing the same number stay two leads, flagged in the dashboard as
    possible duplicates (same normalized phone). This is how "do not merge
    different people" and "do not overwrite without verification" are met.
  * Once a lead is linked to a submitted application (or anonymised), later
    captures with the same token only bump last_activity_at; they never
    overwrite the details recorded for that application.
"""

import hashlib
import logging
import re
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from app.extensions import db
from app.models import ApplicantLead, ApplicantLeadAuditLog
from app.models.applicant_lead import LEAD_STATUSES
from app.utils.phone import mask_phone, normalize_kenyan_phone
from app.utils.validation import EMAIL_RE, NotFoundError, ValidationError

log = logging.getLogger(__name__)

EAT = timezone(timedelta(hours=3))  # Africa/Nairobi — no DST

TOKEN_RE = re.compile(r"^[A-Za-z0-9_-]{32,128}$")
# Letters (any script), spaces, apostrophes, hyphens, dots. At least 3 letters.
NAME_RE = re.compile(r"^[^\W\d_]+(?:[ '.\-][^\W\d_]*)*\.?$", re.UNICODE)

ALLOWED_APPLICATION_TYPES = {"scholarship", "general", "programme_inquiry"}
SUBMITTED_STATUS = "application_submitted"
CONTACTED_LIKE_STATUSES = {"contacted", "interested", "follow_up_required", "not_interested"}
MAX_NOTES = 5000


def _now():
    return datetime.now(timezone.utc)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _clean(value, max_len):
    if not isinstance(value, str):
        return None
    value = " ".join(value.split())
    return value[:max_len] if value else None


def is_valid_token(token) -> bool:
    return isinstance(token, str) and bool(TOKEN_RE.match(token))


def validate_name(name) -> str | None:
    name = _clean(name, 200)
    if not name or len(name) > 120 or not NAME_RE.match(name):
        return None
    if sum(ch.isalpha() for ch in name) < 3:
        return None
    return name


# ---------------------------------------------------------------
# PUBLIC: CAPTURE
# ---------------------------------------------------------------

def capture_lead(payload: dict) -> ApplicantLead:
    """Create or update the lead for this browser's token. Raises
    ValidationError (422) on invalid input; nothing invalid is ever saved."""
    errors = {}
    token = payload.get("lead_token")
    if not is_valid_token(token):
        errors["lead_token"] = ["Invalid session token."]
    name = validate_name(payload.get("applicant_name"))
    if not name:
        errors["applicant_name"] = ["Please enter a valid name."]
    raw_phone = _clean(payload.get("phone_number"), 30)
    normalized = normalize_kenyan_phone(raw_phone) if raw_phone else None
    if not normalized:
        errors["phone_number"] = ["Please enter a valid Kenyan phone number."]
    email = _clean(payload.get("email"), 200)
    if email:
        email = email.lower()
        if not EMAIL_RE.match(email):
            email = None  # optional field: an invalid email is ignored, not saved
    application_type = payload.get("application_type") or "scholarship"
    if application_type not in ALLOWED_APPLICATION_TYPES:
        errors["application_type"] = ["Invalid application type."]
    if errors:
        raise ValidationError(errors)

    programme = _clean(payload.get("programme"), 255)
    school = _clean(payload.get("school"), 120)
    source_page = _clean(payload.get("source_page"), 120)
    token_hash = hash_token(token)
    now = _now()

    try:
        _insert_if_absent(token_hash, {
            "lead_token_hash": token_hash,
            "applicant_name": name,
            "phone_number": raw_phone,
            "normalized_phone": normalized,
            "email": email,
            "programme": programme,
            "school": school,
            "application_type": application_type,
            "source_page": source_page,
            "lead_status": "new_lead",
            "first_captured_at": now,
            "last_updated_at": now,
            "last_activity_at": now,
            "created_at": now,
            "updated_at": now,
        })

        lead = (
            db.session.query(ApplicantLead)
            .filter(ApplicantLead.lead_token_hash == token_hash)
            .with_for_update()
            .one()
        )

        lead.last_activity_at = now
        if lead.application_id is None and lead.anonymized_at is None:
            changed = False
            for attr, value in (
                ("applicant_name", name),
                ("phone_number", raw_phone),
                ("normalized_phone", normalized),
                ("email", email),
                ("programme", programme),
                ("school", school),
                ("source_page", source_page),
            ):
                # Optional fields are only ever filled/corrected, never blanked
                # by a later request that happens to omit them.
                if value is not None and getattr(lead, attr) != value:
                    setattr(lead, attr, value)
                    changed = True
            if changed:
                lead.last_updated_at = now
        db.session.commit()
        return lead
    except Exception:
        db.session.rollback()
        raise


def _insert_if_absent(token_hash: str, values: dict) -> None:
    dialect = db.engine.dialect.name
    if dialect == "postgresql":
        stmt = pg_insert(ApplicantLead.__table__).values(**values).on_conflict_do_nothing(
            index_elements=["lead_token_hash"]
        )
    elif dialect == "sqlite":
        stmt = sqlite_insert(ApplicantLead.__table__).values(**values).on_conflict_do_nothing(
            index_elements=["lead_token_hash"]
        )
    else:  # pragma: no cover — project only runs on PostgreSQL / SQLite (tests)
        if ApplicantLead.query.filter_by(lead_token_hash=token_hash).first():
            return
        stmt = ApplicantLead.__table__.insert().values(**values)
    db.session.execute(stmt)


# ---------------------------------------------------------------
# PUBLIC: LINK TO A SUCCESSFULLY SUBMITTED APPLICATION
# ---------------------------------------------------------------

def link_application(application, payload: dict) -> ApplicantLead | None:
    """Called only AFTER the application has been committed successfully.
    Identifies the lead by this browser's token; if no token was sent (e.g.
    the AI Bootcamp form), falls back to the normalized phone number only
    when exactly one open lead has it. Never creates a lead, never touches
    the application row."""
    now = _now()
    lead = None
    token = payload.get("lead_token")
    if is_valid_token(token):
        lead = (
            ApplicantLead.query.filter_by(lead_token_hash=hash_token(token))
            .with_for_update()
            .first()
        )
    if lead is None:
        normalized = normalize_kenyan_phone(payload.get("phone") or "")
        if normalized:
            candidates = (
                ApplicantLead.query.filter(
                    ApplicantLead.normalized_phone == normalized,
                    ApplicantLead.application_id.is_(None),
                    ApplicantLead.anonymized_at.is_(None),
                )
                .limit(2)
                .all()
            )
            if len(candidates) == 1:
                lead = candidates[0]
    if lead is None or lead.anonymized_at is not None:
        return None
    if lead.application_id is not None and lead.application_id != application.id:
        return None  # already linked to a different application: never re-point it

    lead.application_id = application.id
    lead.lead_status = SUBMITTED_STATUS
    lead.last_activity_at = now
    if not lead.email and payload.get("email"):
        lead.email = _clean(str(payload["email"]).lower(), 200)
    if not lead.programme and getattr(application, "programme", None) is not None:
        lead.programme = application.programme.name
    db.session.commit()
    return lead


# ---------------------------------------------------------------
# ADMIN: STATS / LIST / DETAIL
# ---------------------------------------------------------------

def _start_of_today_utc():
    now_eat = datetime.now(EAT)
    return now_eat.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc)


def lead_stats() -> dict:
    q = ApplicantLead.query
    contacted_filter = db.or_(
        ApplicantLead.contacted_at.isnot(None),
        ApplicantLead.lead_status.in_(CONTACTED_LIKE_STATUSES),
    )
    return {
        "total": q.count(),
        "new_today": q.filter(ApplicantLead.first_captured_at >= _start_of_today_utc()).count(),
        "contacted": q.filter(contacted_filter).count(),
        "interested": q.filter(ApplicantLead.lead_status == "interested").count(),
        "incomplete": q.filter(ApplicantLead.application_id.is_(None)).count(),
        "completed": q.filter(ApplicantLead.application_id.isnot(None)).count(),
        "not_contacted": q.filter(
            ApplicantLead.contacted_at.is_(None),
            ApplicantLead.lead_status == "new_lead",
        ).count(),
    }


def list_leads(q=None, lead_status=None, app_status=None, sort="newest", uncontacted=False,
               page=1, per_page=25):
    query = ApplicantLead.query
    if q:
        q = q.strip()
        digits = re.sub(r"\D", "", q)
        if digits and len(digits) >= 3 and not re.search(r"[^\d\s+\-()]", q):
            if digits.startswith("254"):
                digits = digits[3:]
            digits = digits.lstrip("0") or digits
            query = query.filter(ApplicantLead.normalized_phone.contains(digits))
        else:
            query = query.filter(ApplicantLead.applicant_name.ilike(f"%{q}%"))
    if lead_status in LEAD_STATUSES:
        query = query.filter(ApplicantLead.lead_status == lead_status)
    if app_status == "submitted":
        query = query.filter(ApplicantLead.application_id.isnot(None))
    elif app_status == "incomplete":
        query = query.filter(ApplicantLead.application_id.is_(None))
    if uncontacted:
        query = query.filter(ApplicantLead.contacted_at.is_(None), ApplicantLead.lead_status == "new_lead")
    order = ApplicantLead.first_captured_at.asc() if sort == "oldest" else ApplicantLead.first_captured_at.desc()
    query = query.order_by(order, ApplicantLead.id.desc())

    page = max(1, page or 1)
    per_page = min(max(1, per_page), 100)
    total = query.count()
    records = query.offset((page - 1) * per_page).limit(per_page).all()
    return {"records": records, "total": total, "page": page, "per_page": per_page,
            "pages": max(1, (total + per_page - 1) // per_page)}


def get_lead(lead_id: int) -> ApplicantLead:
    lead = db.session.get(ApplicantLead, lead_id)
    if lead is None:
        raise NotFoundError("Lead not found.")
    return lead


def possible_duplicates(lead: ApplicantLead):
    if lead.anonymized_at is not None:
        return []
    return (
        ApplicantLead.query.filter(
            ApplicantLead.normalized_phone == lead.normalized_phone,
            ApplicantLead.id != lead.id,
            ApplicantLead.anonymized_at.is_(None),
        )
        .order_by(ApplicantLead.first_captured_at.desc())
        .limit(10)
        .all()
    )


def audit_entries(lead_id: int):
    return (
        ApplicantLeadAuditLog.query.filter_by(lead_id=lead_id)
        .order_by(ApplicantLeadAuditLog.created_at.desc())
        .limit(50)
        .all()
    )


# ---------------------------------------------------------------
# ADMIN: FOLLOW-UP / DELETE / ANONYMISE
# ---------------------------------------------------------------

def _audit(lead_id, admin, action, detail=None):
    db.session.add(ApplicantLeadAuditLog(
        lead_id=lead_id, admin_user_id=admin.id if admin else None,
        action=action, detail=(detail or "")[:500] or None,
    ))


def parse_contacted_at(value: str | None):
    """Accepts 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM' (an <input type=date/datetime-local>
    value), interpreted as Nairobi time. Returns aware UTC datetime or None."""
    if not value:
        return None
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(value.strip(), fmt).replace(tzinfo=EAT)
        except ValueError:
            continue
        if fmt == "%Y-%m-%d":
            parsed = parsed.replace(hour=12)
        result = parsed.astimezone(timezone.utc)
        if result > _now() + timedelta(days=1):
            raise ValidationError({"contacted_at": ["Contact date cannot be in the future."]})
        if result.year < 2020:
            raise ValidationError({"contacted_at": ["Contact date is not valid."]})
        return result
    raise ValidationError({"contacted_at": ["Contact date is not valid."]})


def update_follow_up(lead_id: int, admin, status: str | None, contacted_at_raw: str | None,
                     notes: str | None) -> ApplicantLead:
    lead = get_lead(lead_id)
    changes = []

    if status and status != lead.lead_status:
        if status not in LEAD_STATUSES:
            raise ValidationError({"lead_status": ["Invalid follow-up status."]})
        if status == SUBMITTED_STATUS and lead.application_id is None:
            raise ValidationError({"lead_status": [
                "'Application Submitted' is set automatically when the applicant actually submits "
                "their application. It cannot be set for an incomplete lead."
            ]})
        changes.append(f"status {lead.lead_status} -> {status}")
        lead.lead_status = status

    contacted_at = parse_contacted_at(contacted_at_raw)
    if contacted_at is not None and contacted_at != lead.contacted_at:
        lead.contacted_at = contacted_at
        changes.append("contact date recorded")
    elif lead.contacted_at is None and status == "contacted":
        lead.contacted_at = _now()
        changes.append("contact date recorded (now)")

    if notes is not None:
        notes = notes.strip()[:MAX_NOTES] or None
        if notes != lead.follow_up_notes:
            lead.follow_up_notes = notes
            changes.append("notes updated")

    if changes:
        _audit(lead.id, admin, "follow_up_update", "; ".join(changes))
    db.session.commit()
    return lead


def delete_lead(lead_id: int, admin, acknowledge_linked: bool = False) -> dict:
    """Deletes ONLY the applicant_leads row. The linked application (if any),
    its applicant, documents, PDFs, payments and every other record are never
    touched: the FK lives on this table and no cascade exists. Idempotent: a
    repeated request for an already-deleted lead reports already_deleted."""
    lead = db.session.get(ApplicantLead, lead_id)
    if lead is None:
        return {"deleted": False, "already_deleted": True}
    if lead.application_id is not None and not acknowledge_linked:
        raise ValidationError({"confirm_linked": [
            "This lead is linked to a submitted application. Tick the confirmation box to delete "
            "the lead record (the application itself will be kept)."
        ]})
    detail = f"phone {mask_phone(lead.normalized_phone)}"
    if lead.application_id is not None:
        detail += f"; was linked to application id {lead.application_id} (application kept)"
    _audit(lead.id, admin, "delete", detail)
    db.session.delete(lead)
    db.session.commit()
    return {"deleted": True, "already_deleted": False}


def anonymize_lead(lead_id: int, admin) -> ApplicantLead:
    """Retention alternative to deletion: strips personal data but keeps the
    row (status, dates, application link) for admissions statistics."""
    lead = get_lead(lead_id)
    if lead.anonymized_at is not None:
        return lead
    _audit(lead.id, admin, "anonymise", f"phone {mask_phone(lead.normalized_phone)}")
    lead.applicant_name = "Anonymised applicant"
    lead.phone_number = "removed"
    lead.normalized_phone = "removed"
    lead.email = None
    lead.follow_up_notes = None
    # Detach from the browser token so the old browser can't re-attach to this row.
    lead.lead_token_hash = hash_token(secrets.token_urlsafe(32))
    lead.anonymized_at = _now()
    db.session.commit()
    return lead
