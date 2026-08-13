"""
Engagement service (Step 5) — Alumni, Graduate Profile Requests, Partner
Enquiries, Contact Messages, Newsletter Subscribers.

These five approved Phase-1 tables (Step 2 §11-14) are all simple,
single-table, validated inserts with no cross-entity workflow — grouped
into one service module rather than five near-identical files.
"""

from app.extensions import db
from app.models import Alumni, GraduateProfileRequest, PartnerEnquiry, ContactMessage, NewsletterSubscriber
from app.utils.validation import Validator, ValidationError

ALLOWED_ENQUIRY_TYPES = {"partnership", "corporate_training"}


def register_alumni(payload: dict) -> Alumni:
    v = Validator()
    v.require(payload, "full_name", "Full name").max_length(payload, "full_name", 200, "Full name")
    v.require(payload, "email", "Email").email(payload, "email", "Email").max_length(payload, "email", 200, "Email")
    v.require(payload, "phone", "Phone").max_length(payload, "phone", 20, "Phone")
    v.is_bool(payload, "consent", "Consent")
    year = payload.get("graduation_year")
    if year is not None and not (isinstance(year, int) and 1990 <= year <= 2100):
        v._add("graduation_year", "Graduation year must be a whole number between 1990 and 2100.")
    v.finish()

    email = payload["email"].strip().lower()
    if Alumni.query.filter_by(email=email).first() is not None:
        raise ValidationError({"email": ["An alumni record with this email already exists."]})

    try:
        row = Alumni(
            full_name=payload["full_name"],
            email=email,
            phone=payload["phone"],
            programme_id=payload.get("programme_id"),
            graduation_year=year,
            organisation=payload.get("organisation"),
            engagement_interests=payload.get("engagement_interests"),
            consent=bool(payload.get("consent", False)),
        )
        db.session.add(row)
        db.session.commit()
        return row
    except Exception:
        db.session.rollback()
        raise


def request_graduate_profile(payload: dict) -> GraduateProfileRequest:
    v = Validator()
    v.require(payload, "employer_name", "Employer name").max_length(payload, "employer_name", 200, "Employer name")
    v.require(payload, "email", "Email").email(payload, "email", "Email").max_length(payload, "email", 200, "Email")
    v.finish()

    try:
        row = GraduateProfileRequest(
            employer_name=payload["employer_name"],
            company=payload.get("company"),
            email=payload["email"].strip().lower(),
            phone=payload.get("phone"),
            role_needed=payload.get("role_needed"),
            message=payload.get("message"),
            status="pending",
        )
        db.session.add(row)
        db.session.commit()
        return row
    except Exception:
        db.session.rollback()
        raise


def submit_partner_enquiry(payload: dict) -> PartnerEnquiry:
    v = Validator()
    v.require(payload, "organisation", "Organisation").max_length(payload, "organisation", 200, "Organisation")
    v.require(payload, "contact_name", "Contact name").max_length(payload, "contact_name", 200, "Contact name")
    v.require(payload, "email", "Email").email(payload, "email", "Email").max_length(payload, "email", 200, "Email")
    v.require(payload, "enquiry_type", "Enquiry type").one_of(payload, "enquiry_type", ALLOWED_ENQUIRY_TYPES, "Enquiry type")
    v.finish()

    try:
        row = PartnerEnquiry(
            organisation=payload["organisation"],
            contact_name=payload["contact_name"],
            email=payload["email"].strip().lower(),
            phone=payload.get("phone"),
            enquiry_type=payload["enquiry_type"],
            message=payload.get("message"),
            status="new",
        )
        db.session.add(row)
        db.session.commit()
        return row
    except Exception:
        db.session.rollback()
        raise


def submit_contact_message(payload: dict) -> ContactMessage:
    v = Validator()
    v.require(payload, "name", "Name").max_length(payload, "name", 200, "Name")
    v.require(payload, "email", "Email").email(payload, "email", "Email").max_length(payload, "email", 200, "Email")
    v.require(payload, "message", "Message")
    v.finish()

    try:
        row = ContactMessage(
            name=payload["name"],
            email=payload["email"].strip().lower(),
            subject=payload.get("subject"),
            message=payload["message"],
            status="new",
        )
        db.session.add(row)
        db.session.commit()
        return row
    except Exception:
        db.session.rollback()
        raise


def subscribe_newsletter(payload: dict) -> NewsletterSubscriber:
    v = Validator()
    v.require(payload, "email", "Email").email(payload, "email", "Email").max_length(payload, "email", 200, "Email")
    v.finish()

    email = payload["email"].strip().lower()
    existing = NewsletterSubscriber.query.filter_by(email=email).first()
    if existing is not None:
        if not existing.is_active:
            try:
                existing.is_active = True
                existing.unsubscribed_at = None
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise
        return existing

    try:
        row = NewsletterSubscriber(
            email=email,
            source_page=payload.get("source_page"),
            consent=bool(payload.get("consent", True)),
            is_active=True,
        )
        db.session.add(row)
        db.session.commit()
        return row
    except Exception:
        db.session.rollback()
        raise
