"""
Admin service (Step 7) — authentication + read/status-update queries
over the existing Phase 1 tables, for the staff administration portal.

Deliberately reuses the exact models/relationships built in Steps 2-5.
No new tables, no duplicate "AdminApplicationModel"-style shadow
entities (Step 7 §14Y) — this module is a thin query/update layer over
the models that already exist.

Status values are never invented here: every allowed value below is
copied directly from the CHECK constraint already defined on the
corresponding model (Step 2 §27):
  - Application.status: submitted / under_review / offered / enrolled
    / rejected / withdrawn
  - GraduateProfileRequest.status: pending / approved / fulfilled / declined
  - PartnerEnquiry.status: new / contacted / closed
  - ContactMessage.status: new / read / responded
Alumni and NewsletterSubscriber have no admin-settable workflow status
in the approved schema (NewsletterSubscriber only has the boolean
is_active, set by the public subscribe/unsubscribe flow) — so no
status-update function exists for either here, per the "do not invent
status values" rule.
"""

from datetime import datetime, timezone

from app.extensions import db
from app.models import (
    AdminUser,
    Applicant,
    Application,
    Alumni,
    EarnCashApplicationCommission,
    EarnCashNotification,
    EarnCashTransaction,
    GraduateProfileRequest,
    PartnerEnquiry,
    ContactMessage,
    NewsletterSubscriber,
)
from app.utils.earncash_helpers import commission_rate
from app.utils.security import verify_password
from app.utils.validation import NotFoundError, ValidationError

APPLICATION_STATUSES = ["submitted", "under_review", "offered", "enrolled", "rejected", "withdrawn"]
GRADUATE_REQUEST_STATUSES = ["pending", "approved", "fulfilled", "declined"]
PARTNER_ENQUIRY_STATUSES = ["new", "contacted", "closed"]
CONTACT_MESSAGE_STATUSES = ["new", "read", "responded"]


# ---------------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------------

def authenticate(email: str, password: str) -> AdminUser | None:
    """Return the matching, active AdminUser if the password is correct, else None.

    Deliberately returns the same generic None for "no such account" and
    "wrong password" — the route layer must not let a caller distinguish
    the two (Step 7 §14W: do not reveal whether an account exists).
    """
    if not email or not password:
        return None
    admin = AdminUser.query.filter_by(email=email.strip().lower()).first()
    if admin is None or not admin.is_active:
        return None
    if not verify_password(password, admin.password_hash):
        return None
    return admin


def record_login(admin: AdminUser) -> None:
    admin.last_login_at = datetime.now(timezone.utc)
    db.session.commit()


# ---------------------------------------------------------------
# DASHBOARD STATISTICS
# ---------------------------------------------------------------

def dashboard_stats() -> dict:
    """Only counts that are genuinely backed by an existing column — nothing invented."""
    app_counts = {s: Application.query.filter_by(status=s).count() for s in APPLICATION_STATUSES}
    return {
        "total_applications": Application.query.count(),
        "applications_by_status": app_counts,
        "scholarship_applications": Application.query.filter_by(application_type="scholarship").count(),
        "general_applications": Application.query.filter_by(application_type="general").count(),
        "programme_inquiries": Application.query.filter_by(application_type="programme_inquiry").count(),
        "alumni_total": Alumni.query.count(),
        "graduate_requests_total": GraduateProfileRequest.query.count(),
        "graduate_requests_pending": GraduateProfileRequest.query.filter_by(status="pending").count(),
        "partnership_enquiries_total": PartnerEnquiry.query.filter_by(enquiry_type="partnership").count(),
        "corporate_training_total": PartnerEnquiry.query.filter_by(enquiry_type="corporate_training").count(),
        "contact_messages_total": ContactMessage.query.count(),
        "contact_messages_new": ContactMessage.query.filter_by(status="new").count(),
        "newsletter_subscribers_total": NewsletterSubscriber.query.count(),
        "newsletter_subscribers_active": NewsletterSubscriber.query.filter_by(is_active=True).count(),
    }


# ---------------------------------------------------------------
# PAGINATION HELPER
# ---------------------------------------------------------------

def _paginate(query, page: int, per_page: int = 25):
    page = max(1, page)
    per_page = min(max(1, per_page), 100)
    total = query.count()
    records = query.offset((page - 1) * per_page).limit(per_page).all()
    pages = max(1, (total + per_page - 1) // per_page)
    # NOTE: deliberately keyed "records", not "items" — Jinja resolves
    # `dict.items` to the dict's own built-in .items() method before
    # falling back to key lookup, which silently breaks `{% for x in
    # result.items %}`. Using "records" avoids that footgun everywhere
    # this pagination dict is rendered.
    return {"records": records, "total": total, "page": page, "per_page": per_page, "pages": pages}


# ---------------------------------------------------------------
# APPLICATIONS (also serves the "Scholarship Applications" view via
# application_type filter — Step 2 §10: no separate scholarships table)
# ---------------------------------------------------------------

def list_applications(status=None, application_type=None, q=None, page=1, per_page=25):
    query = Application.query.join(Applicant)
    if status:
        query = query.filter(Application.status == status)
    if application_type:
        query = query.filter(Application.application_type == application_type)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            db.or_(Applicant.full_name.ilike(like), Applicant.email.ilike(like), Application.reference_code.ilike(like))
        )
    query = query.order_by(Application.submitted_at.desc())
    return _paginate(query, page, per_page)


def get_application(app_id: int) -> Application:
    application = db.session.get(Application, app_id)
    if application is None:
        raise NotFoundError(f"No application found with id {app_id}.")
    return application


def update_application_status(app_id: int, new_status: str) -> Application:
    if new_status not in APPLICATION_STATUSES:
        raise ValidationError({"status": [f"Must be one of: {', '.join(APPLICATION_STATUSES)}."]})
    application = get_application(app_id)
    application.status = new_status
    db.session.commit()
    return application


# ---------------------------------------------------------------
# EARNFASTCASH REFERRAL: TUITION PAYMENT CONFIRMATION
#
# This is the ONLY place a commission can be created for a referred GTI
# application — mirrors the existing, already-shipped rule in
# app/blueprints/earncash/admin_routes.py's verify_enrollment_payment
# (a commission is only ever created after a GTI/EarnCash admin
# confirms real money was received, never on click, application, or
# offer alone).
# ---------------------------------------------------------------

def confirm_application_tuition(app_id: int) -> dict:
    """Admin confirms real tuition payment was received for this
    application. Idempotent: calling it again on an already-confirmed
    application changes nothing and simply reports the existing state.

    A commission is created only when ALL of the following are real:
      - the application actually has a referrer (referred_by_earncash_user_id)
      - the application's programme_mode has a real, published fee_amount
        (never invented — most academic applications have no numeric fee
        here at all, so they simply never generate a commission)
      - no commission has already been created for this application
        (enforced twice: the check below, and the table's own UNIQUE
        constraint on application_id, so a race condition still can't
        double-credit a wallet)
    """
    application = get_application(app_id)

    already_confirmed = application.tuition_confirmed_at is not None
    if not already_confirmed:
        application.tuition_confirmed_at = datetime.now(timezone.utc)

    commission_created = False
    commission_amount = None

    existing_commission = EarnCashApplicationCommission.query.filter_by(application_id=application.id).first()

    if (
        application.referred_by_earncash_user_id
        and application.programme_mode is not None
        and application.programme_mode.fee_amount is not None
        and existing_commission is None
    ):
        fee = float(application.programme_mode.fee_amount)
        commission_amount = round(fee * commission_rate(), 2)

        db.session.add(EarnCashApplicationCommission(
            referrer_id=application.referred_by_earncash_user_id,
            application_id=application.id,
            commission_amount=commission_amount,
        ))

        referrer = application.referred_by_earncash_user
        referrer.wallet = float(referrer.wallet) + commission_amount

        db.session.add(EarnCashTransaction(
            user_id=application.referred_by_earncash_user_id, type="commission", amount=commission_amount,
            description=f"Referral commission for GTI application {application.reference_code}",
        ))
        db.session.add(EarnCashNotification(
            user_id=application.referred_by_earncash_user_id, title="Commission received",
            message=(
                f"You earned KES {commission_amount:.2f} because your referral's application "
                f"({application.reference_code}) had tuition payment confirmed by Germaine Training Institute."
            ),
        ))
        commission_created = True

    db.session.commit()

    return {
        "application": application,
        "already_confirmed": already_confirmed,
        "commission_created": commission_created,
        "commission_amount": commission_amount,
    }


# ---------------------------------------------------------------
# ALUMNI (read-only — no status column exists on this table)
# ---------------------------------------------------------------

def list_alumni(q=None, graduation_year=None, page=1, per_page=25):
    query = Alumni.query
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(db.or_(Alumni.full_name.ilike(like), Alumni.email.ilike(like)))
    if graduation_year:
        query = query.filter(Alumni.graduation_year == graduation_year)
    query = query.order_by(Alumni.registered_at.desc())
    return _paginate(query, page, per_page)


def get_alumni_record(alumni_id: int) -> Alumni:
    record = db.session.get(Alumni, alumni_id)
    if record is None:
        raise NotFoundError(f"No alumni record found with id {alumni_id}.")
    return record


# ---------------------------------------------------------------
# GRADUATE PROFILE REQUESTS
# ---------------------------------------------------------------

def list_graduate_requests(status=None, q=None, page=1, per_page=25):
    query = GraduateProfileRequest.query
    if status:
        query = query.filter(GraduateProfileRequest.status == status)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(db.or_(GraduateProfileRequest.employer_name.ilike(like), GraduateProfileRequest.email.ilike(like)))
    query = query.order_by(GraduateProfileRequest.submitted_at.desc())
    return _paginate(query, page, per_page)


def get_graduate_request(request_id: int) -> GraduateProfileRequest:
    record = db.session.get(GraduateProfileRequest, request_id)
    if record is None:
        raise NotFoundError(f"No graduate profile request found with id {request_id}.")
    return record


def update_graduate_request_status(request_id: int, new_status: str) -> GraduateProfileRequest:
    if new_status not in GRADUATE_REQUEST_STATUSES:
        raise ValidationError({"status": [f"Must be one of: {', '.join(GRADUATE_REQUEST_STATUSES)}."]})
    record = get_graduate_request(request_id)
    record.status = new_status
    db.session.commit()
    return record


# ---------------------------------------------------------------
# PARTNER ENQUIRIES (partnership / corporate_training)
# ---------------------------------------------------------------

def list_partner_enquiries(enquiry_type=None, status=None, q=None, page=1, per_page=25):
    query = PartnerEnquiry.query
    if enquiry_type:
        query = query.filter(PartnerEnquiry.enquiry_type == enquiry_type)
    if status:
        query = query.filter(PartnerEnquiry.status == status)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(db.or_(PartnerEnquiry.organisation.ilike(like), PartnerEnquiry.email.ilike(like)))
    query = query.order_by(PartnerEnquiry.submitted_at.desc())
    return _paginate(query, page, per_page)


def get_partner_enquiry(enquiry_id: int) -> PartnerEnquiry:
    record = db.session.get(PartnerEnquiry, enquiry_id)
    if record is None:
        raise NotFoundError(f"No partner enquiry found with id {enquiry_id}.")
    return record


def update_partner_enquiry_status(enquiry_id: int, new_status: str) -> PartnerEnquiry:
    if new_status not in PARTNER_ENQUIRY_STATUSES:
        raise ValidationError({"status": [f"Must be one of: {', '.join(PARTNER_ENQUIRY_STATUSES)}."]})
    record = get_partner_enquiry(enquiry_id)
    record.status = new_status
    db.session.commit()
    return record


# ---------------------------------------------------------------
# CONTACT MESSAGES
# ---------------------------------------------------------------

def list_contact_messages(status=None, q=None, page=1, per_page=25):
    query = ContactMessage.query
    if status:
        query = query.filter(ContactMessage.status == status)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(db.or_(ContactMessage.name.ilike(like), ContactMessage.email.ilike(like)))
    query = query.order_by(ContactMessage.submitted_at.desc())
    return _paginate(query, page, per_page)


def get_contact_message(message_id: int) -> ContactMessage:
    record = db.session.get(ContactMessage, message_id)
    if record is None:
        raise NotFoundError(f"No contact message found with id {message_id}.")
    return record


def update_contact_message_status(message_id: int, new_status: str) -> ContactMessage:
    if new_status not in CONTACT_MESSAGE_STATUSES:
        raise ValidationError({"status": [f"Must be one of: {', '.join(CONTACT_MESSAGE_STATUSES)}."]})
    record = get_contact_message(message_id)
    record.status = new_status
    db.session.commit()
    return record


# ---------------------------------------------------------------
# NEWSLETTER SUBSCRIBERS (read-only list — no admin-editable fields
# beyond what the public subscribe/unsubscribe flow already governs)
# ---------------------------------------------------------------

def list_newsletter_subscribers(active_only=None, q=None, page=1, per_page=25):
    query = NewsletterSubscriber.query
    if active_only is not None:
        query = query.filter(NewsletterSubscriber.is_active == active_only)
    if q:
        query = query.filter(NewsletterSubscriber.email.ilike(f"%{q.strip()}%"))
    query = query.order_by(NewsletterSubscriber.subscribed_at.desc())
    return _paginate(query, page, per_page)
