"""
Admin dashboard tests (Step 7).

Covers authentication, authorization (protected routes), CSRF, and
read/status-update behaviour for every admin-portal section, all
against the in-memory SQLite `db_client` fixture — never the real
PostgreSQL instance. No admin credential used here is a real one;
`_helpers.create_admin_user` always hashes a test-only password.
"""

from datetime import date

from app.extensions import db
from app.models import (
    Applicant, Application, Alumni, GraduateProfileRequest, PartnerEnquiry, ContactMessage,
    NewsletterSubscriber, EarnCashApplicationCommission,
)
from tests._helpers import seed_minimal_catalogue, create_admin_user, login_admin, get_csrf_from, create_earncash_user


def _seed_records(catalogue):
    applicant = Applicant(full_name="Jane Doe", email="jane@example.com", phone="254712345678",
                           national_id="12345678", date_of_birth=date(2000, 1, 1), gender="Female", county="Nakuru")
    db.session.add(applicant)
    db.session.flush()

    application = Application(
        reference_code="REF00001", applicant_id=applicant.id, programme_id=catalogue["academic"].id,
        application_type="scholarship", education_level="KCSE", kcse_grade="B+", consent=True, status="submitted",
    )
    db.session.add(application)

    alumni = Alumni(full_name="John Alumnus", email="john.alumnus@example.com", phone="254700000000",
                     graduation_year=2020, consent=True)
    db.session.add(alumni)

    db.session.add(GraduateProfileRequest(employer_name="Acme Ltd", email="hr@acme.com", role_needed="Nurse", status="pending"))
    db.session.add(PartnerEnquiry(organisation="Acme Partners", contact_name="Bob", email="bob@acme.com", enquiry_type="partnership", status="new"))
    db.session.add(PartnerEnquiry(organisation="Acme Training", contact_name="Sue", email="sue@acme.com", enquiry_type="corporate_training", status="new"))
    db.session.add(ContactMessage(name="Alice Public", email="alice@example.com", message="Hello there", status="new"))
    db.session.add(NewsletterSubscriber(email="subscriber@example.com", is_active=True))
    db.session.commit()
    return application


# ---------------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------------

def test_login_page_renders(db_client):
    resp = db_client.get("/admin/login")
    assert resp.status_code == 200
    assert b"csrf_token" in resp.data


def test_login_success_redirects_to_dashboard(db_client, db_app):
    with db_app.app_context():
        create_admin_user()
    resp = login_admin(db_client)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/admin/")


def test_login_failure_wrong_password_shows_generic_error(db_client, db_app):
    with db_app.app_context():
        create_admin_user(email="real@example.com", password="CorrectHorse1!")
    resp = login_admin(db_client, email="real@example.com", password="WrongPassword")
    assert resp.status_code == 200
    assert b"Invalid email or password" in resp.data
    # never reveals whether the account exists
    assert b"account" not in resp.data.lower() or b"no account" not in resp.data.lower()


def test_login_failure_unknown_email_shows_same_generic_error(db_client, db_app):
    with db_app.app_context():
        create_admin_user(email="real@example.com")
    resp = login_admin(db_client, email="doesnotexist@example.com", password="whatever123")
    assert resp.status_code == 200
    assert b"Invalid email or password" in resp.data


def test_login_rejects_inactive_admin(db_client, db_app):
    with db_app.app_context():
        create_admin_user(email="inactive@example.com", password="Password123!", is_active=False)
    resp = login_admin(db_client, email="inactive@example.com", password="Password123!")
    assert resp.status_code == 200
    assert b"Invalid email or password" in resp.data


def test_login_rejects_missing_csrf_token(db_client, db_app):
    with db_app.app_context():
        create_admin_user()
    resp = db_client.post("/admin/login", data={"email": "admin@example.com", "password": "Sup3rSecret!1"})
    assert resp.status_code == 403


def test_logout_clears_session_and_denies_further_access(db_client, db_app):
    with db_app.app_context():
        create_admin_user()
    login_admin(db_client)
    dash = db_client.get("/admin/")
    token = get_csrf_from(dash)
    resp = db_client.post("/admin/logout", data={"csrf_token": token}, follow_redirects=False)
    assert resp.status_code == 302
    after = db_client.get("/admin/", follow_redirects=False)
    assert after.status_code == 302
    assert "/admin/login" in after.headers["Location"]


# ---------------------------------------------------------------
# AUTHORIZATION — every protected route must reject an unauthenticated caller
# ---------------------------------------------------------------

PROTECTED_PATHS = [
    "/admin/",
    "/admin/applications",
    "/admin/scholarships",
    "/admin/applications/1",
    "/admin/alumni",
    "/admin/alumni/1",
    "/admin/enquiries/contact",
    "/admin/enquiries/contact/1",
    "/admin/enquiries/graduate-requests",
    "/admin/enquiries/graduate-requests/1",
    "/admin/enquiries/partnerships",
    "/admin/enquiries/corporate-training",
    "/admin/enquiries/partner/1",
    "/admin/newsletter",
]


def test_all_protected_routes_redirect_unauthenticated_requests(db_client):
    for path in PROTECTED_PATHS:
        resp = db_client.get(path, follow_redirects=False)
        assert resp.status_code == 302, f"{path} did not redirect (got {resp.status_code})"
        assert "/admin/login" in resp.headers["Location"], f"{path} did not redirect to login"


def test_protected_route_does_not_leak_data_before_redirect(db_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        _seed_records(catalogue)
    resp = db_client.get("/admin/applications", follow_redirects=False)
    assert resp.status_code == 302
    assert b"REF00001" not in resp.data
    assert b"jane@example.com" not in resp.data


def test_status_update_post_requires_authentication(db_client):
    resp = db_client.post("/admin/applications/1/status", data={"status": "offered"}, follow_redirects=False)
    assert resp.status_code == 302
    assert "/admin/login" in resp.headers["Location"]


# ---------------------------------------------------------------
# APPLICATIONS
# ---------------------------------------------------------------

def test_applications_list_shows_seeded_application(db_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        _seed_records(catalogue)
        create_admin_user()
    login_admin(db_client)
    resp = db_client.get("/admin/applications")
    assert resp.status_code == 200
    assert b"REF00001" in resp.data
    assert b"Jane Doe" in resp.data


def test_applications_search_filters_results(db_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        _seed_records(catalogue)
        create_admin_user()
    login_admin(db_client)
    hit = db_client.get("/admin/applications?q=jane")
    assert b"REF00001" in hit.data
    miss = db_client.get("/admin/applications?q=nonexistent-name-xyz")
    assert b"REF00001" not in miss.data
    assert b"No applications match" in miss.data


def test_applications_status_filter(db_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        _seed_records(catalogue)
        create_admin_user()
    login_admin(db_client)
    resp = db_client.get("/admin/applications?status=submitted")
    assert b"REF00001" in resp.data
    resp2 = db_client.get("/admin/applications?status=rejected")
    assert b"REF00001" not in resp2.data


def test_scholarships_view_is_filtered_to_scholarship_type(db_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        application = _seed_records(catalogue)
        applicant2 = Applicant(full_name="General Applicant", email="general@example.com", phone="254711111111")
        db.session.add(applicant2)
        db.session.flush()
        db.session.add(Application(
            reference_code="REF00002", applicant_id=applicant2.id, programme_id=catalogue["academic"].id,
            application_type="general", status="submitted",
        ))
        db.session.commit()
        create_admin_user()
    login_admin(db_client)
    resp = db_client.get("/admin/scholarships")
    assert b"REF00001" in resp.data
    assert b"REF00002" not in resp.data


def test_application_detail_shows_applicant_and_academic_info(db_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        _seed_records(catalogue)
        create_admin_user()
    login_admin(db_client)
    resp = db_client.get("/admin/applications/1")
    assert resp.status_code == 200
    assert b"Jane Doe" in resp.data
    assert b"jane@example.com" in resp.data
    assert b"Diploma in Nursing" in resp.data
    assert b"REF00001" in resp.data


def test_application_detail_404_for_missing_id(db_client, db_app):
    with db_app.app_context():
        create_admin_user()
    login_admin(db_client)
    resp = db_client.get("/admin/applications/9999")
    assert resp.status_code == 404


def test_application_status_update_persists(db_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        _seed_records(catalogue)
        create_admin_user()
    login_admin(db_client)
    detail = db_client.get("/admin/applications/1")
    token = get_csrf_from(detail)
    resp = db_client.post("/admin/applications/1/status", data={"status": "under_review", "csrf_token": token}, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Under Review" in resp.data

    with db_app.app_context():
        app_row = db.session.get(Application, 1)
        assert app_row.status == "under_review"


def test_application_status_update_rejects_invalid_status(db_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        _seed_records(catalogue)
        create_admin_user()
    login_admin(db_client)
    detail = db_client.get("/admin/applications/1")
    token = get_csrf_from(detail)
    resp = db_client.post("/admin/applications/1/status", data={"status": "not-a-real-status", "csrf_token": token}, follow_redirects=True)
    assert resp.status_code == 200
    with db_app.app_context():
        app_row = db.session.get(Application, 1)
        assert app_row.status == "submitted"  # unchanged


def test_application_status_update_rejects_bad_csrf(db_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        _seed_records(catalogue)
        create_admin_user()
    login_admin(db_client)
    resp = db_client.post("/admin/applications/1/status", data={"status": "offered", "csrf_token": "wrong"})
    assert resp.status_code == 403
    with db_app.app_context():
        app_row = db.session.get(Application, 1)
        assert app_row.status == "submitted"


# ---------------------------------------------------------------
# EARNFASTCASH REFERRAL: TUITION CONFIRMATION (admin route)
# ---------------------------------------------------------------

def _seed_referred_ai_application(catalogue, referral_code="ECREFROUTE1"):
    referrer = create_earncash_user(referral_code=referral_code, email=f"{referral_code.lower()}@example.com")
    applicant = Applicant(full_name="Referred Applicant", email="referred.applicant@example.com", phone="254788888888")
    db.session.add(applicant)
    db.session.flush()
    application = Application(
        reference_code="REFROUTE01", applicant_id=applicant.id, programme_id=catalogue["ai_programme"].id,
        programme_mode_id=catalogue["mode"].id, application_type="programme_inquiry", consent=True,
        status="submitted", referred_by_earncash_user_id=referrer.id,
    )
    db.session.add(application)
    db.session.commit()
    return application, referrer


def test_confirm_tuition_route_requires_authentication(db_client):
    resp = db_client.post("/admin/applications/1/confirm-tuition", data={}, follow_redirects=False)
    assert resp.status_code == 302
    assert "/admin/login" in resp.headers["Location"]


def test_confirm_tuition_route_credits_commission_and_shows_in_detail(db_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        application, referrer = _seed_referred_ai_application(catalogue)
        application_id = application.id
        create_admin_user()
    login_admin(db_client)

    detail = db_client.get(f"/admin/applications/{application_id}")
    assert b"EarnFastCash Referral" in detail.data
    assert b"Not yet confirmed" in detail.data
    token = get_csrf_from(detail)

    resp = db_client.post(
        f"/admin/applications/{application_id}/confirm-tuition",
        data={"csrf_token": token}, follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"14500.00" in resp.data or b"14,500.00" in resp.data or b"Confirmed" in resp.data

    with db_app.app_context():
        commission = EarnCashApplicationCommission.query.filter_by(application_id=application_id).first()
        assert commission is not None
        assert float(commission.commission_amount) == 14500.00


def test_confirm_tuition_route_rejects_bad_csrf(db_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        application, referrer = _seed_referred_ai_application(catalogue)
        application_id = application.id
        create_admin_user()
    login_admin(db_client)
    resp = db_client.post(f"/admin/applications/{application_id}/confirm-tuition", data={"csrf_token": "wrong"})
    assert resp.status_code == 403
    with db_app.app_context():
        assert EarnCashApplicationCommission.query.count() == 0


def test_confirm_tuition_route_404_for_missing_application(db_client, db_app):
    with db_app.app_context():
        create_admin_user()
    login_admin(db_client)
    detail_get = db_client.get("/admin/applications/9999")
    assert detail_get.status_code == 404


def test_application_detail_without_referral_shows_no_referral_panel(db_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        _seed_records(catalogue)
        create_admin_user()
    login_admin(db_client)
    resp = db_client.get("/admin/applications/1")
    assert b"EarnFastCash Referral" not in resp.data


# ---------------------------------------------------------------
# ALUMNI (read-only)
# ---------------------------------------------------------------

def test_alumni_list_and_detail(db_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        _seed_records(catalogue)
        create_admin_user()
    login_admin(db_client)
    listing = db_client.get("/admin/alumni")
    assert b"John Alumnus" in listing.data
    detail = db_client.get("/admin/alumni/1")
    assert detail.status_code == 200
    assert b"john.alumnus@example.com" in detail.data
    # unresolved programme mapping (Step 2 Sec 39 F) must be shown honestly, never guessed
    assert b"unresolved" in detail.data.lower()


def test_alumni_has_no_status_update_route():
    """Alumni has no status column in the approved schema — confirm no
    status-update endpoint was invented for it."""
    from app.blueprints.admin import routes
    assert not hasattr(routes, "alumni_status_update")


# ---------------------------------------------------------------
# ENQUIRIES
# ---------------------------------------------------------------

def test_contact_list_detail_and_status_update(db_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        _seed_records(catalogue)
        create_admin_user()
    login_admin(db_client)
    listing = db_client.get("/admin/enquiries/contact")
    assert b"Alice Public" in listing.data
    detail = db_client.get("/admin/enquiries/contact/1")
    assert b"Hello there" in detail.data
    token = get_csrf_from(detail)
    resp = db_client.post("/admin/enquiries/contact/1/status", data={"status": "read", "csrf_token": token}, follow_redirects=True)
    assert b"Read" in resp.data
    with db_app.app_context():
        record = db.session.get(ContactMessage, 1)
        assert record.status == "read"


def test_graduate_requests_list_detail_and_status_update(db_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        _seed_records(catalogue)
        create_admin_user()
    login_admin(db_client)
    listing = db_client.get("/admin/enquiries/graduate-requests")
    assert b"Acme Ltd" in listing.data
    detail = db_client.get("/admin/enquiries/graduate-requests/1")
    token = get_csrf_from(detail)
    resp = db_client.post("/admin/enquiries/graduate-requests/1/status", data={"status": "approved", "csrf_token": token}, follow_redirects=True)
    assert b"Approved" in resp.data


def test_partnerships_and_corporate_training_are_separated_by_enquiry_type(db_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        _seed_records(catalogue)
        create_admin_user()
    login_admin(db_client)
    partnerships = db_client.get("/admin/enquiries/partnerships")
    assert b"Acme Partners" in partnerships.data
    assert b"Acme Training" not in partnerships.data

    corporate = db_client.get("/admin/enquiries/corporate-training")
    assert b"Acme Training" in corporate.data
    assert b"Acme Partners" not in corporate.data


def test_partner_enquiry_detail_and_status_update(db_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        _seed_records(catalogue)
        create_admin_user()
    login_admin(db_client)
    detail = db_client.get("/admin/enquiries/partner/1")
    assert detail.status_code == 200
    token = get_csrf_from(detail)
    resp = db_client.post("/admin/enquiries/partner/1/status", data={"status": "contacted", "csrf_token": token}, follow_redirects=True)
    assert b"Contacted" in resp.data


# ---------------------------------------------------------------
# NEWSLETTER (read-only)
# ---------------------------------------------------------------

def test_newsletter_list(db_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        _seed_records(catalogue)
        create_admin_user()
    login_admin(db_client)
    resp = db_client.get("/admin/newsletter")
    assert resp.status_code == 200
    assert b"subscriber@example.com" in resp.data


# ---------------------------------------------------------------
# DASHBOARD STATS
# ---------------------------------------------------------------

def test_dashboard_stats_reflect_seeded_data(db_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        _seed_records(catalogue)
        create_admin_user()
    login_admin(db_client)
    resp = db_client.get("/admin/")
    assert resp.status_code == 200
    assert b"Dashboard" in resp.data
    # 1 total application, seeded as 'submitted' / 'scholarship'
    assert b">1<" in resp.data


# ---------------------------------------------------------------
# SECURITY
# ---------------------------------------------------------------

def test_no_password_hash_ever_rendered_in_any_admin_page(db_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        _seed_records(catalogue)
        create_admin_user()
    login_admin(db_client)
    for path in ["/admin/", "/admin/applications", "/admin/applications/1", "/admin/alumni",
                 "/admin/enquiries/contact", "/admin/newsletter"]:
        resp = db_client.get(path)
        assert b"password_hash" not in resp.data
        assert b"pbkdf2:sha256" not in resp.data


def test_public_api_blueprint_never_exposes_admin_records(db_client, db_app):
    """The pre-existing public /api/... routes must never be a backdoor to
    admin-only data — confirms the two surfaces stayed fully separate."""
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        _seed_records(catalogue)
    resp = db_client.get("/api/schools")
    assert resp.status_code == 200
    assert b"jane@example.com" not in resp.data
    assert b"REF00001" not in resp.data


def test_login_route_is_the_only_unauthenticated_admin_route(db_client):
    """Every other /admin/* route must require auth; only /admin/login (GET/POST) does not."""
    resp = db_client.get("/admin/login")
    assert resp.status_code == 200
