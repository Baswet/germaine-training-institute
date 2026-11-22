"""Service-layer tests: application_service (Step 5)."""

import pytest

from app.services import application_service
from app.utils.validation import ValidationError, NotFoundError
from tests._helpers import seed_minimal_catalogue, create_earncash_user


def _base_payload(programme_id, **overrides):
    payload = {
        "full_name": "Jane Wanjiru",
        "email": "jane.wanjiru@example.com",
        "phone": "254712345678",
        "programme_id": programme_id,
        "consent": True,
    }
    payload.update(overrides)
    return payload


def test_create_application_success_academic(db_app):
    with db_app.app_context():
        data = seed_minimal_catalogue()
        app_row = application_service.create_application(_base_payload(data["academic"].id))
        assert app_row.id is not None
        assert app_row.reference_code
        assert app_row.application_type == "scholarship"
        assert app_row.status == "submitted"
        assert app_row.programme_mode_id is None


def test_create_application_reference_code_not_sequential_id(db_app):
    with db_app.app_context():
        data = seed_minimal_catalogue()
        app_row = application_service.create_application(_base_payload(data["academic"].id))
        assert str(app_row.id) not in app_row.reference_code or len(app_row.reference_code) > len(str(app_row.id)) + 3
        assert app_row.reference_code.startswith("GTI-")


def test_create_application_missing_required_fields_raises(db_app):
    with db_app.app_context():
        data = seed_minimal_catalogue()
        with pytest.raises(ValidationError) as exc_info:
            application_service.create_application({"programme_id": data["academic"].id})
        assert "full_name" in exc_info.value.errors
        assert "email" in exc_info.value.errors
        assert "phone" in exc_info.value.errors


def test_create_application_invalid_email_raises(db_app):
    with db_app.app_context():
        data = seed_minimal_catalogue()
        payload = _base_payload(data["academic"].id, email="not-an-email")
        with pytest.raises(ValidationError) as exc_info:
            application_service.create_application(payload)
        assert "email" in exc_info.value.errors


def test_create_application_unknown_programme_raises_not_found(db_app):
    with db_app.app_context():
        seed_minimal_catalogue()
        with pytest.raises(NotFoundError):
            application_service.create_application(_base_payload(999999))


def test_create_application_academic_with_mode_id_rejected(db_app):
    with db_app.app_context():
        data = seed_minimal_catalogue()
        payload = _base_payload(data["academic"].id, programme_mode_id=data["mode"].id)
        with pytest.raises(ValidationError) as exc_info:
            application_service.create_application(payload)
        assert "programme_mode_id" in exc_info.value.errors


def test_create_application_ai_bootcamp_with_valid_mode(db_app):
    with db_app.app_context():
        data = seed_minimal_catalogue()
        payload = _base_payload(data["ai_programme"].id, programme_mode_id=data["mode"].id)
        app_row = application_service.create_application(payload)
        assert app_row.programme_mode_id == data["mode"].id


def test_create_application_mode_from_other_programme_rejected(db_app):
    with db_app.app_context():
        data = seed_minimal_catalogue()
        # academic programme has no modes; use a bogus mode id that doesn't belong to the AI programme
        payload = _base_payload(data["ai_programme"].id, programme_mode_id=999999)
        with pytest.raises(ValidationError) as exc_info:
            application_service.create_application(payload)
        assert "programme_mode_id" in exc_info.value.errors


def test_applicant_matched_by_email_not_duplicated(db_app):
    with db_app.app_context():
        data = seed_minimal_catalogue()
        from app.models import Applicant

        app1 = application_service.create_application(_base_payload(data["academic"].id))
        app2 = application_service.create_application(
            _base_payload(data["ai_programme"].id, programme_mode_id=data["mode"].id,
                          full_name="Jane W.", email="JANE.WANJIRU@example.com")
        )
        assert app1.applicant_id == app2.applicant_id
        assert Applicant.query.count() == 1


def test_invalid_application_type_rejected(db_app):
    with db_app.app_context():
        data = seed_minimal_catalogue()
        payload = _base_payload(data["academic"].id, application_type="not-a-real-type")
        with pytest.raises(ValidationError) as exc_info:
            application_service.create_application(payload)
        assert "application_type" in exc_info.value.errors


def test_get_application_by_reference_code(db_app):
    with db_app.app_context():
        data = seed_minimal_catalogue()
        created = application_service.create_application(_base_payload(data["academic"].id))
        found = application_service.get_application_by_reference_code(created.reference_code)
        assert found.id == created.id


def test_get_application_by_unknown_reference_code_raises(db_app):
    with db_app.app_context():
        seed_minimal_catalogue()
        with pytest.raises(NotFoundError):
            application_service.get_application_by_reference_code("GTI-000000-XXXX")


# ---------------------------------------------------------------
# EarnFastCash referral attribution (Phase B, Part 1)
# ---------------------------------------------------------------

def test_create_application_with_valid_referral_code_is_attributed(db_app):
    with db_app.app_context():
        data = seed_minimal_catalogue()
        referrer = create_earncash_user(referral_code="ECREF0001")
        payload = _base_payload(
            data["ai_programme"].id, programme_mode_id=data["mode"].id, referral_code="ecref0001"
        )
        app_row = application_service.create_application(payload)
        assert app_row.referred_by_earncash_user_id == referrer.id


def test_create_application_with_unknown_referral_code_not_blocked(db_app):
    with db_app.app_context():
        data = seed_minimal_catalogue()
        payload = _base_payload(data["academic"].id, referral_code="NOTREALCODE")
        app_row = application_service.create_application(payload)
        assert app_row.id is not None
        assert app_row.referred_by_earncash_user_id is None


def test_create_application_with_no_referral_code_has_no_attribution(db_app):
    with db_app.app_context():
        data = seed_minimal_catalogue()
        app_row = application_service.create_application(_base_payload(data["academic"].id))
        assert app_row.referred_by_earncash_user_id is None


def test_create_application_referral_code_from_suspended_earncash_user_ignored(db_app):
    with db_app.app_context():
        data = seed_minimal_catalogue()
        referrer = create_earncash_user(referral_code="ECREF0002")
        referrer.status = "suspended"
        from app.extensions import db
        db.session.commit()
        payload = _base_payload(data["academic"].id, referral_code="ECREF0002")
        app_row = application_service.create_application(payload)
        assert app_row.referred_by_earncash_user_id is None


# --- Full Scholarship is for Academic School programmes only ------------------

def test_scholarship_rejected_for_non_academic_programme(db_app):
    with db_app.app_context():
        data = seed_minimal_catalogue()
        payload = _base_payload(data["ai_programme"].id, application_type="scholarship")
        with pytest.raises(ValidationError) as exc_info:
            application_service.create_application(payload)
        assert "programme_id" in exc_info.value.errors
        assert "Academic School" in exc_info.value.errors["programme_id"][0]


def test_scholarship_allowed_for_academic_programme(db_app):
    with db_app.app_context():
        data = seed_minimal_catalogue()
        row = application_service.create_application(
            _base_payload(data["academic"].id, application_type="scholarship"))
        assert row.application_type == "scholarship"


def test_general_application_for_non_academic_programme_unaffected(db_app):
    with db_app.app_context():
        data = seed_minimal_catalogue()
        row = application_service.create_application(
            _base_payload(data["ai_programme"].id, application_type="general"))
        assert row.application_type == "general"


def test_scholarship_rejected_for_languages_school(db_app):
    with db_app.app_context():
        data = seed_minimal_catalogue()
        data["school"].name = "School of Languages"
        from app.extensions import db
        db.session.commit()
        with pytest.raises(ValidationError):
            application_service.create_application(
                _base_payload(data["academic"].id, application_type="scholarship"))
