"""Service-layer tests: admin_service.confirm_application_tuition
(EarnFastCash <-> GTI referral bridge, Phase B Part 1).

Covers the ONLY code path that may ever create an
EarnCashApplicationCommission row — real referrer + real published fee
+ not already confirmed. No commission is ever invented for an
application with no referrer, no fee, or an already-confirmed payment.
"""

from decimal import Decimal

import pytest

from app.extensions import db
from app.models import Applicant, Application, EarnCashApplicationCommission, EarnCashTransaction, EarnCashNotification
from app.services import admin_service
from app.utils.validation import NotFoundError
from tests._helpers import seed_minimal_catalogue, create_earncash_user


_UNSET = object()


def _make_application(catalogue, referrer=None, programme_mode_id=_UNSET, programme_id=None):
    applicant = Applicant(full_name="Ref Applicant", email="ref.applicant@example.com", phone="254799999999")
    db.session.add(applicant)
    db.session.flush()
    application = Application(
        reference_code="REFTEST01",
        applicant_id=applicant.id,
        programme_id=programme_id or catalogue["ai_programme"].id,
        programme_mode_id=catalogue["mode"].id if programme_mode_id is _UNSET else programme_mode_id,
        application_type="programme_inquiry",
        consent=True,
        status="submitted",
        referred_by_earncash_user_id=referrer.id if referrer else None,
    )
    db.session.add(application)
    db.session.commit()
    return application


def test_confirm_tuition_with_referrer_and_fee_creates_commission(db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        referrer = create_earncash_user(referral_code="ECREF0010")
        application = _make_application(catalogue, referrer=referrer)

        result = admin_service.confirm_application_tuition(application.id)

        assert result["already_confirmed"] is False
        assert result["commission_created"] is True
        # mode fee_amount is 145000, default EARNCASH_COMMISSION_RATE is 0.10
        assert result["commission_amount"] == pytest.approx(14500.00)

        commission = EarnCashApplicationCommission.query.filter_by(application_id=application.id).first()
        assert commission is not None
        assert commission.referrer_id == referrer.id
        assert float(commission.commission_amount) == pytest.approx(14500.00)

        db.session.refresh(referrer)
        assert float(referrer.wallet) == pytest.approx(14500.00)

        assert EarnCashTransaction.query.filter_by(user_id=referrer.id, type="commission").count() == 1
        assert EarnCashNotification.query.filter_by(user_id=referrer.id).count() == 1

        app_row = db.session.get(Application, application.id)
        assert app_row.tuition_confirmed_at is not None


def test_confirm_tuition_is_idempotent_no_double_commission(db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        referrer = create_earncash_user(referral_code="ECREF0011")
        application = _make_application(catalogue, referrer=referrer)

        first = admin_service.confirm_application_tuition(application.id)
        assert first["commission_created"] is True

        second = admin_service.confirm_application_tuition(application.id)
        assert second["already_confirmed"] is True
        assert second["commission_created"] is False

        assert EarnCashApplicationCommission.query.filter_by(application_id=application.id).count() == 1
        db.session.refresh(referrer)
        assert float(referrer.wallet) == pytest.approx(14500.00)  # not doubled


def test_confirm_tuition_without_referrer_creates_no_commission(db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        application = _make_application(catalogue, referrer=None)

        result = admin_service.confirm_application_tuition(application.id)

        assert result["commission_created"] is False
        assert result["commission_amount"] is None
        assert EarnCashApplicationCommission.query.count() == 0
        app_row = db.session.get(Application, application.id)
        assert app_row.tuition_confirmed_at is not None  # payment still recorded


def test_confirm_tuition_with_referrer_but_no_fee_creates_no_commission(db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        referrer = create_earncash_user(referral_code="ECREF0012")
        # academic programme has no programme_mode at all -> no numeric fee anywhere
        application = _make_application(
            catalogue, referrer=referrer, programme_mode_id=None, programme_id=catalogue["academic"].id
        )

        result = admin_service.confirm_application_tuition(application.id)

        assert result["commission_created"] is False
        assert result["commission_amount"] is None
        assert EarnCashApplicationCommission.query.count() == 0
        db.session.refresh(referrer)
        assert float(referrer.wallet) == 0


def test_confirm_tuition_unknown_application_raises_not_found(db_app):
    with db_app.app_context():
        seed_minimal_catalogue()
        with pytest.raises(NotFoundError):
            admin_service.confirm_application_tuition(999999)
