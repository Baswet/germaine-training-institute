"""
PostgreSQL-only checks for applicant lead capture: real migration chain,
concurrent requests for one token, and FK delete behaviour.

Skipped unless LEADS_TEST_POSTGRES_URL points at a THROWAWAY database, e.g.
    LEADS_TEST_POSTGRES_URL=postgresql+psycopg://postgres@/gti_test?host=/tmp&port=5433
The database is downgraded to base and re-migrated at the start, so NEVER
point this at a real (staging-with-data or production) database.
"""

import os
import secrets
import threading

import pytest

PG_URL = os.environ.get("LEADS_TEST_POSTGRES_URL")
pytestmark = pytest.mark.skipif(not PG_URL, reason="LEADS_TEST_POSTGRES_URL not set")


@pytest.fixture(scope="module")
def pg_app():
    os.environ["DATABASE_URL"] = PG_URL
    from app import create_app
    from app.config import TestingConfig
    from app.extensions import db
    from flask_migrate import downgrade, upgrade

    class PgTesting(TestingConfig):
        SQLALCHEMY_DATABASE_URI = PG_URL

    import app.config as cfg
    cfg.CONFIG_BY_NAME["pg_leads_testing"] = PgTesting
    app = create_app("pg_leads_testing")
    migrations_dir = os.path.join(os.path.dirname(__file__), "..", "migrations")
    with app.app_context():
        downgrade(directory=migrations_dir, revision="base")
        upgrade(directory=migrations_dir)
        yield app
        db.session.remove()


def test_migration_head_is_lead_revision(pg_app):
    from app.extensions import db
    with pg_app.app_context():
        from alembic.script import ScriptDirectory
        from flask_migrate import Migrate  # noqa: F401
        rev = db.session.execute(db.text("SELECT version_num FROM alembic_version")).scalar()
        assert rev in ("c4d9e2a7b1f0", "e7a3b5c9d1f2")  # leads, or a later additive head
        cols = {r[0] for r in db.session.execute(db.text(
            "SELECT column_name FROM information_schema.columns WHERE table_name='applicant_leads'"))}
        assert {"normalized_phone", "lead_token_hash", "application_id", "follow_up_notes"} <= cols


def test_concurrent_requests_for_one_token_create_exactly_one_lead(pg_app):
    from app.blueprints.admissions import routes
    from app.extensions import db
    from app.models import ApplicantLead
    routes._lead_ip_limiter.reset()
    routes._lead_token_limiter.max_events = 1000
    token = secrets.token_hex(32)
    barrier = threading.Barrier(12)
    codes = []

    def worker(i):
        client = pg_app.test_client()
        barrier.wait()
        resp = client.post("/api/admissions/leads/capture", json={
            "lead_token": token, "applicant_name": f"Concurrent Person {chr(65 + i)}",
            "phone_number": "0712345678"})
        codes.append(resp.status_code)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(12)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    routes._lead_token_limiter.max_events = 15
    assert codes == [200] * 12
    with pg_app.app_context():
        db.session.remove()
        assert ApplicantLead.query.filter_by(
            lead_token_hash=__import__("hashlib").sha256(token.encode()).hexdigest()).count() == 1


def test_check_constraint_rejects_unknown_status(pg_app):
    from sqlalchemy.exc import IntegrityError
    from app.extensions import db
    with pg_app.app_context():
        with pytest.raises(IntegrityError):
            db.session.execute(db.text(
                "INSERT INTO applicant_leads (lead_token_hash, applicant_name, phone_number, normalized_phone, "
                "application_type, lead_status, first_captured_at, last_updated_at, last_activity_at, created_at, "
                "updated_at) VALUES ('x', 'A B C', '1', '254712345678', 'scholarship', 'bogus', now(), now(), "
                "now(), now(), now())"))
        db.session.rollback()


def test_fk_set_null_and_lead_delete_never_touches_application(pg_app):
    from app.extensions import db
    from app.models import Applicant, ApplicantLead, Application, School, Programme
    with pg_app.app_context():
        school = School(slug=f"s{secrets.token_hex(3)}", name="Test School", is_active=True, display_order=0)
        db.session.add(school); db.session.flush()
        prog = Programme(programme_type="academic", slug=f"p{secrets.token_hex(3)}", school_id=school.id,
                         name="Test Programme", level="Diploma", is_active=True)
        db.session.add(prog); db.session.flush()
        applicant = Applicant(full_name="Pg Person", email=f"{secrets.token_hex(4)}@example.test", phone="254700000001")
        db.session.add(applicant); db.session.flush()
        application = Application(reference_code=secrets.token_hex(5).upper(), applicant_id=applicant.id,
                                  programme_id=prog.id, consent=True)
        db.session.add(application); db.session.flush()
        lead = ApplicantLead(lead_token_hash=secrets.token_hex(32), applicant_name="Pg Person",
                             phone_number="700000001", normalized_phone="254700000001",
                             application_type="scholarship", lead_status="application_submitted",
                             application_id=application.id)
        db.session.add(lead); db.session.commit()
        app_id, lead_id = application.id, lead.id

        # Deleting the lead row leaves the application intact
        db.session.execute(db.text("DELETE FROM applicant_leads WHERE id=:i"), {"i": lead_id})
        db.session.commit()
        assert db.session.get(Application, app_id) is not None

        # Deleting an application only nulls a lead's link
        lead2 = ApplicantLead(lead_token_hash=secrets.token_hex(32), applicant_name="Pg Person",
                              phone_number="700000001", normalized_phone="254700000001",
                              application_type="scholarship", lead_status="application_submitted",
                              application_id=app_id)
        db.session.add(lead2); db.session.commit()
        lead2_id = lead2.id
        db.session.execute(db.text("DELETE FROM applications WHERE id=:i"), {"i": app_id})
        db.session.commit()
        db.session.expire_all()
        assert db.session.get(ApplicantLead, lead2_id).application_id is None


def test_downgrade_removes_only_new_tables(pg_app):
    """Downgrading to the live pre-leads head removes only the tables added since."""
    from flask_migrate import downgrade, upgrade
    from app.extensions import db
    migrations_dir = os.path.join(os.path.dirname(__file__), "..", "migrations")
    with pg_app.app_context():
        db.session.remove()
        before = {r[0] for r in db.session.execute(db.text(
            "SELECT tablename FROM pg_tables WHERE schemaname='public'"))}
        db.session.remove()
        downgrade(directory=migrations_dir, revision="e5f2a9c1d7b3")  # live head before leads
        after = {r[0] for r in db.session.execute(db.text(
            "SELECT tablename FROM pg_tables WHERE schemaname='public'"))}
        assert before - after == {"applicant_leads", "applicant_lead_audit_logs", "news_article_meta", "news_events"}
        db.session.remove()
        upgrade(directory=migrations_dir)
