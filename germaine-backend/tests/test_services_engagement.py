"""Service-layer tests: engagement_service (Step 5) — alumni, graduate
requests, partner enquiries, contact messages, newsletter subscribers."""

import pytest

from app.services import engagement_service
from app.utils.validation import ValidationError


def test_register_alumni_success(db_app):
    with db_app.app_context():
        row = engagement_service.register_alumni({
            "full_name": "John Otieno", "email": "john.otieno@example.com",
            "phone": "254700000000", "consent": True,
        })
        assert row.id is not None
        assert row.email == "john.otieno@example.com"


def test_register_alumni_duplicate_email_rejected(db_app):
    with db_app.app_context():
        payload = {"full_name": "John Otieno", "email": "dupe@example.com",
                   "phone": "254700000000", "consent": True}
        engagement_service.register_alumni(payload)
        with pytest.raises(ValidationError):
            engagement_service.register_alumni(payload)


def test_register_alumni_invalid_graduation_year_rejected(db_app):
    with db_app.app_context():
        payload = {"full_name": "John Otieno", "email": "yeartest@example.com",
                   "phone": "254700000000", "consent": True, "graduation_year": 1800}
        with pytest.raises(ValidationError):
            engagement_service.register_alumni(payload)


def test_request_graduate_profile_success(db_app):
    with db_app.app_context():
        row = engagement_service.request_graduate_profile({
            "employer_name": "Acme Ltd", "email": "hr@acme.example.com",
        })
        assert row.status == "pending"


def test_request_graduate_profile_missing_fields_rejected(db_app):
    with db_app.app_context():
        with pytest.raises(ValidationError):
            engagement_service.request_graduate_profile({})


def test_submit_partner_enquiry_requires_valid_enquiry_type(db_app):
    with db_app.app_context():
        with pytest.raises(ValidationError):
            engagement_service.submit_partner_enquiry({
                "organisation": "Acme", "contact_name": "A", "email": "a@example.com",
                "enquiry_type": "not-a-real-type",
            })


def test_submit_partner_enquiry_success(db_app):
    with db_app.app_context():
        row = engagement_service.submit_partner_enquiry({
            "organisation": "Acme", "contact_name": "A", "email": "a@example.com",
            "enquiry_type": "corporate_training",
        })
        assert row.status == "new"
        assert row.enquiry_type == "corporate_training"


def test_submit_contact_message_success(db_app):
    with db_app.app_context():
        row = engagement_service.submit_contact_message({
            "name": "A", "email": "a@example.com", "message": "Hello",
        })
        assert row.status == "new"


def test_subscribe_newsletter_idempotent(db_app):
    with db_app.app_context():
        row1 = engagement_service.subscribe_newsletter({"email": "sub@example.com", "source_page": "home"})
        row2 = engagement_service.subscribe_newsletter({"email": "SUB@example.com", "source_page": "about"})
        assert row1.id == row2.id

        from app.models import NewsletterSubscriber
        assert NewsletterSubscriber.query.count() == 1


def test_subscribe_newsletter_reactivates_unsubscribed(db_app):
    with db_app.app_context():
        from app.extensions import db
        row = engagement_service.subscribe_newsletter({"email": "resub@example.com"})
        row.is_active = False
        db.session.commit()

        resubscribed = engagement_service.subscribe_newsletter({"email": "resub@example.com"})
        assert resubscribed.is_active is True
