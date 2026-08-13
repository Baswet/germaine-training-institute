"""
Database interaction tests (Step 5) — relationships, transaction
rollback, and constraint enforcement. Runs against in-memory SQLite via
the db_app fixture (see conftest.py); never touches the real Postgres
instance used in Step 4.
"""

import pytest
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import School, Department, Programme, ProgrammeMode, ProgrammeFAQ, ProgrammeFeature, Applicant
from tests._helpers import seed_minimal_catalogue


def test_deleting_programme_cascades_to_modes_faqs_features(db_app):
    with db_app.app_context():
        data = seed_minimal_catalogue()
        programme_id = data["ai_programme"].id
        assert ProgrammeMode.query.filter_by(programme_id=programme_id).count() == 1
        assert ProgrammeFAQ.query.filter_by(programme_id=programme_id).count() == 1
        assert ProgrammeFeature.query.filter_by(programme_id=programme_id).count() == 1

        db.session.delete(data["ai_programme"])
        db.session.commit()

        assert ProgrammeMode.query.filter_by(programme_id=programme_id).count() == 0
        assert ProgrammeFAQ.query.filter_by(programme_id=programme_id).count() == 0
        assert ProgrammeFeature.query.filter_by(programme_id=programme_id).count() == 0


def test_deleting_school_cascades_to_departments(db_app):
    with db_app.app_context():
        data = seed_minimal_catalogue()
        school_id = data["school"].id
        assert Department.query.filter_by(school_id=school_id).count() == 1

        # the academic programme FKs to this school/department, remove it first
        db.session.delete(data["academic"])
        db.session.commit()

        db.session.delete(data["school"])
        db.session.commit()

        assert Department.query.filter_by(school_id=school_id).count() == 0


def test_unique_email_constraint_enforced_on_applicants(db_app):
    with db_app.app_context():
        db.session.add(Applicant(full_name="A", email="dup@example.com", phone="254700000000"))
        db.session.commit()

        db.session.add(Applicant(full_name="B", email="dup@example.com", phone="254711111111"))
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        assert Applicant.query.count() == 1


def test_check_constraint_enforced_on_programme_type(db_app):
    with db_app.app_context():
        bad = Programme(programme_type="not_a_real_type", slug="bad-programme", name="Bad")
        db.session.add(bad)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        assert Programme.query.filter_by(slug="bad-programme").count() == 0


def test_transaction_rollback_leaves_no_partial_data(db_app):
    with db_app.app_context():
        try:
            db.session.add(Applicant(full_name="Ghost", email="ghost@example.com", phone="254700000000"))
            db.session.flush()  # assigns an id, but does not commit
            raise RuntimeError("Simulated failure mid-transaction")
        except RuntimeError:
            db.session.rollback()

        assert Applicant.query.filter_by(email="ghost@example.com").count() == 0


def test_programme_department_school_relationship_chain(db_app):
    with db_app.app_context():
        data = seed_minimal_catalogue()
        programme = Programme.query.filter_by(slug="diploma-in-nursing").first()
        assert programme.department.name == "Nursing"
        assert programme.department.school.slug == "health"
        assert programme.school.slug == "health"
