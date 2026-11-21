"""
Applicant Leads admin section (master spec §5–§7; test scenarios 10–13),
plus stats, search/filter/sort, CSRF and authorization checks.
"""

import secrets
from datetime import datetime, timedelta, timezone

import pytest

from app.blueprints.admissions import routes as admissions_routes
from app.extensions import db
from app.models import Applicant, ApplicantLead, ApplicantLeadAuditLog, Application
from tests._helpers import create_admin_user, get_csrf_from, login_admin, seed_minimal_catalogue


@pytest.fixture(autouse=True)
def _reset_limiters():
    admissions_routes._lead_ip_limiter.reset()
    admissions_routes._lead_token_limiter.reset()
    yield


def _lead(name="Wanjiru Kamau", phone="254712345678", status="new_lead", application_id=None, **kw):
    lead = ApplicantLead(
        lead_token_hash=secrets.token_hex(32), applicant_name=name, phone_number=phone[3:],
        normalized_phone=phone, lead_status=status, application_id=application_id,
        application_type="scholarship", **kw,
    )
    db.session.add(lead)
    db.session.commit()
    return lead


def _submitted_application(catalogue):
    applicant = Applicant(full_name="Wanjiru Kamau", email="wk@example.com", phone="254712345678")
    db.session.add(applicant)
    db.session.flush()
    application = Application(reference_code="REFLEAD01", applicant_id=applicant.id,
                              programme_id=catalogue["academic"].id, consent=True, status="submitted")
    db.session.add(application)
    db.session.commit()
    return application


@pytest.fixture()
def admin_client(db_client, db_app):
    with db_app.app_context():
        create_admin_user()
    login_admin(db_client)
    return db_client


def _csrf(client, path="/admin/leads"):
    return get_csrf_from(client.get(path))


# ---------------------------------------------------------------
# Test 12 — unauthorized access denied
# ---------------------------------------------------------------

@pytest.mark.parametrize("method,path", [
    ("get", "/admin/leads"),
    ("get", "/admin/leads/1"),
    ("get", "/admin/leads/1/delete"),
    ("post", "/admin/leads/1/delete"),
    ("post", "/admin/leads/1/follow-up"),
    ("post", "/admin/leads/1/anonymise"),
])
def test_12_unauthenticated_users_are_denied(db_client, db_app, method, path):
    with db_app.app_context():
        _lead()
    resp = getattr(db_client, method)(path, data={"confirm": "yes"})
    assert resp.status_code == 302
    assert "/admin/login" in resp.headers["Location"]
    with db_app.app_context():
        assert ApplicantLead.query.count() == 1


def test_12_deactivated_admin_is_denied(db_client, db_app):
    with db_app.app_context():
        admin = create_admin_user()
        _lead()
    login_admin(db_client)
    with db_app.app_context():
        db.session.merge(admin).is_active = False
        db.session.commit()
    assert db_client.get("/admin/leads").status_code == 302


def test_no_public_api_exposes_leads(db_client):
    for path in ("/api/admissions/leads", "/api/admissions/leads/1", "/api/leads"):
        assert db_client.get(path).status_code in (404, 405)


def test_state_changes_require_csrf(admin_client, db_app):
    with db_app.app_context():
        lead_id = _lead().id
    assert admin_client.post(f"/admin/leads/{lead_id}/delete", data={"confirm": "yes"}).status_code == 403
    assert admin_client.post(f"/admin/leads/{lead_id}/follow-up",
                             data={"lead_status": "contacted", "csrf_token": "wrong"}).status_code == 403
    with db_app.app_context():
        lead = db.session.get(ApplicantLead, lead_id)
        assert lead is not None and lead.lead_status == "new_lead"


# ---------------------------------------------------------------
# Dashboard listing, stats, search, filters, sort
# ---------------------------------------------------------------

def test_list_shows_columns_stats_and_contact_actions(admin_client, db_app):
    with db_app.app_context():
        _lead(email="wk@example.com", programme="Diploma in Nursing")
    resp = admin_client.get("/admin/leads")
    html = resp.get_data(as_text=True)
    assert resp.status_code == 200
    for text in ("Applicant Leads", "Total Leads", "New Leads Today", "Contacted Leads", "Interested Applicants",
                 "Incomplete Applications", "Completed Applications", "Wanjiru Kamau", "+254712345678",
                 "wk@example.com", "Diploma in Nursing", "Incomplete", "New Lead",
                 'href="tel:+254712345678"', 'href="https://wa.me/254712345678"', "Delete"):
        assert text in html, text


def test_stats_come_from_real_rows(db_app):
    from app.services import lead_service
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        application = _submitted_application(catalogue)
        old = datetime.now(timezone.utc) - timedelta(days=3)
        _lead(name="Old Lead Person", first_captured_at=old)
        _lead(name="Interested Person", status="interested", phone="254722000111")
        _lead(name="Called Person", status="contacted", phone="254733000111",
              contacted_at=datetime.now(timezone.utc))
        _lead(name="Done Person", status="application_submitted", application_id=application.id,
              phone="254744000111")
        stats = lead_service.lead_stats()
    assert stats == {"total": 4, "new_today": 3, "contacted": 2, "interested": 1,
                     "incomplete": 3, "completed": 1, "not_contacted": 1}


def test_search_by_name_and_by_phone_formats(admin_client, db_app):
    with db_app.app_context():
        _lead(name="Wanjiru Kamau", phone="254712345678")
        _lead(name="Otieno Odhiambo", phone="254722999888")
    def names(q):
        html = admin_client.get("/admin/leads", query_string={"q": q}).get_data(as_text=True)
        return ("Wanjiru" in html, "Otieno" in html)
    assert names("wanjiru") == (True, False)
    assert names("0722 999") == (False, True)
    assert names("+254712345678") == (True, False)
    assert names("345678") == (True, False)


def test_filters_and_sort(admin_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        application = _submitted_application(catalogue)
        _lead(name="Alpha First", first_captured_at=datetime.now(timezone.utc) - timedelta(days=2))
        _lead(name="Beta Second", status="interested", phone="254722000111")
        _lead(name="Gamma Third", status="application_submitted", application_id=application.id,
              phone="254733000111")
    get = lambda **qs: admin_client.get("/admin/leads", query_string=qs).get_data(as_text=True)
    html = get(lead_status="interested")
    assert "Beta Second" in html and "Alpha First" not in html
    html = get(app_status="submitted")
    assert "Gamma Third" in html and "Alpha First" not in html and "Beta Second" not in html
    html = get(app_status="incomplete")
    assert "Gamma Third" not in html and "Alpha First" in html
    html = get(uncontacted="1")
    assert "Alpha First" in html and "Beta Second" not in html
    newest, oldest = get(sort="newest"), get(sort="oldest")
    assert newest.index("Alpha First") > newest.index("Beta Second")
    assert oldest.index("Alpha First") < oldest.index("Beta Second")


def test_detail_view_and_possible_duplicates(admin_client, db_app):
    with db_app.app_context():
        lead_id = _lead().id
        _lead(name="Same Phone Other")
    html = admin_client.get(f"/admin/leads/{lead_id}").get_data(as_text=True)
    assert "Captured Information" in html and "Possible Duplicates" in html and "Same Phone Other" in html
    assert "Call Applicant" in html and "WhatsApp Applicant" in html
    assert admin_client.get("/admin/leads/999999").status_code == 404


def test_html_is_escaped(admin_client, db_app):
    with db_app.app_context():
        _lead(name="Test Person", programme="<script>alert(1)</script>")
    html = admin_client.get("/admin/leads").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


# ---------------------------------------------------------------
# Test 13 — follow-up status + notes persist
# ---------------------------------------------------------------

def test_13_follow_up_changes_persist_after_refresh(admin_client, db_app):
    with db_app.app_context():
        lead_id = _lead().id
    token = _csrf(admin_client, f"/admin/leads/{lead_id}")
    resp = admin_client.post(f"/admin/leads/{lead_id}/follow-up", data={
        "csrf_token": token, "lead_status": "interested", "contacted_at": "2026-11-20T10:30",
        "follow_up_notes": "Called; interested in the January intake.",
    })
    assert resp.status_code == 302
    html = admin_client.get(f"/admin/leads/{lead_id}").get_data(as_text=True)
    assert "Called; interested in the January intake." in html
    assert 'value="2026-11-20T10:30"' in html
    assert '<option value="interested" selected' in html
    # notes can be updated again
    admin_client.post(f"/admin/leads/{lead_id}/follow-up", data={
        "csrf_token": token, "lead_status": "follow_up_required", "follow_up_notes": "Call back Monday.",
    })
    with db_app.app_context():
        lead = db.session.get(ApplicantLead, lead_id)
        assert lead.lead_status == "follow_up_required"
        assert lead.follow_up_notes == "Call back Monday."
        assert lead.contacted_at == datetime(2026, 11, 20, 7, 30) or \
            lead.contacted_at.replace(tzinfo=None) == datetime(2026, 11, 20, 7, 30)  # 10:30 EAT = 07:30 UTC
        actions = [a.action for a in ApplicantLeadAuditLog.query.filter_by(lead_id=lead_id)]
        assert actions.count("follow_up_update") == 2


def test_marking_contacted_records_contact_date_automatically(admin_client, db_app):
    with db_app.app_context():
        lead_id = _lead().id
    admin_client.post(f"/admin/leads/{lead_id}/follow-up",
                      data={"csrf_token": _csrf(admin_client), "lead_status": "contacted"})
    with db_app.app_context():
        assert db.session.get(ApplicantLead, lead_id).contacted_at is not None


def test_admin_cannot_mark_incomplete_lead_as_submitted(admin_client, db_app):
    with db_app.app_context():
        lead_id = _lead().id
    admin_client.post(f"/admin/leads/{lead_id}/follow-up",
                      data={"csrf_token": _csrf(admin_client), "lead_status": "application_submitted"})
    with db_app.app_context():
        assert db.session.get(ApplicantLead, lead_id).lead_status == "new_lead"


@pytest.mark.parametrize("bad", ["bogus", "2099-01-01", "1999-01-01"])
def test_invalid_status_or_dates_rejected(admin_client, db_app, bad):
    with db_app.app_context():
        lead_id = _lead().id
    field = "lead_status" if bad == "bogus" else "contacted_at"
    admin_client.post(f"/admin/leads/{lead_id}/follow-up", data={"csrf_token": _csrf(admin_client), field: bad})
    with db_app.app_context():
        lead = db.session.get(ApplicantLead, lead_id)
        assert lead.lead_status == "new_lead" and lead.contacted_at is None


# ---------------------------------------------------------------
# Test 10 / 11 — deletion
# ---------------------------------------------------------------

def test_10_deleting_incomplete_lead_affects_nothing_else(admin_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        application = _submitted_application(catalogue)
        app_id = application.id
        keep = _lead(name="Keep This One", phone="254722000111").id
        target = _lead(name="Delete This One").id
    confirm = admin_client.get(f"/admin/leads/{target}/delete").get_data(as_text=True)
    assert "Delete This One" in confirm and "+254712345678" in confirm
    resp = admin_client.post(f"/admin/leads/{target}/delete",
                             data={"csrf_token": _csrf(admin_client), "confirm": "yes"})
    assert resp.status_code == 302
    with db_app.app_context():
        assert db.session.get(ApplicantLead, target) is None
        assert db.session.get(ApplicantLead, keep) is not None
        assert db.session.get(Application, app_id) is not None
        assert Applicant.query.count() == 1
        log = ApplicantLeadAuditLog.query.filter_by(lead_id=target, action="delete").one()
        assert "712345678" not in (log.detail or "")  # no full phone retained


def test_delete_requires_explicit_confirmation(admin_client, db_app):
    with db_app.app_context():
        lead_id = _lead().id
    admin_client.post(f"/admin/leads/{lead_id}/delete", data={"csrf_token": _csrf(admin_client)})
    with db_app.app_context():
        assert db.session.get(ApplicantLead, lead_id) is not None


def test_repeated_delete_requests_are_safe(admin_client, db_app):
    with db_app.app_context():
        lead_id = _lead().id
    token = _csrf(admin_client)
    first = admin_client.post(f"/admin/leads/{lead_id}/delete", data={"csrf_token": token, "confirm": "yes"},
                              follow_redirects=True)
    second = admin_client.post(f"/admin/leads/{lead_id}/delete", data={"csrf_token": token, "confirm": "yes"},
                               follow_redirects=True)
    assert first.status_code == 200 and b"Lead deleted" in first.data
    assert second.status_code == 200 and b"already been deleted" in second.data
    with db_app.app_context():
        assert ApplicantLeadAuditLog.query.filter_by(lead_id=lead_id, action="delete").count() == 1


def test_11_linked_lead_shows_warning_and_application_survives(admin_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        application = _submitted_application(catalogue)
        app_id = application.id
        lead_id = _lead(status="application_submitted", application_id=app_id).id
    confirm = admin_client.get(f"/admin/leads/{lead_id}/delete").get_data(as_text=True)
    assert "linked to a submitted application" in confirm and "REFLEAD01" in confirm
    assert 'name="confirm_linked"' in confirm

    # Without the extra acknowledgement: refused
    resp = admin_client.post(f"/admin/leads/{lead_id}/delete",
                             data={"csrf_token": _csrf(admin_client), "confirm": "yes"}, follow_redirects=True)
    assert b"linked to a submitted application" in resp.data
    with db_app.app_context():
        assert db.session.get(ApplicantLead, lead_id) is not None

    # With acknowledgement: lead removed, application untouched
    admin_client.post(f"/admin/leads/{lead_id}/delete",
                      data={"csrf_token": _csrf(admin_client), "confirm": "yes", "confirm_linked": "yes"})
    with db_app.app_context():
        assert db.session.get(ApplicantLead, lead_id) is None
        app_row = db.session.get(Application, app_id)
        assert app_row is not None and app_row.status == "submitted" and app_row.reference_code == "REFLEAD01"
        assert Applicant.query.count() == 1


def test_deleting_an_application_only_unlinks_the_lead(db_app):
    """FK is ON DELETE SET NULL; at ORM level nothing cascades to the lead either."""
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        application = _submitted_application(catalogue)
        lead_id = _lead(status="application_submitted", application_id=application.id).id
        db.session.execute(db.text("PRAGMA foreign_keys=ON"))
        db.session.execute(db.text("DELETE FROM applications WHERE id = :i"), {"i": application.id})
        db.session.commit()
        db.session.expire_all()
        lead = db.session.get(ApplicantLead, lead_id)
        assert lead is not None


def test_anonymise_keeps_row_and_application_but_removes_personal_data(admin_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        app_id = _submitted_application(catalogue).id
        lead_id = _lead(status="application_submitted", application_id=app_id,
                        email="wk@example.com", follow_up_notes="Private note").id
    admin_client.post(f"/admin/leads/{lead_id}/anonymise", data={"csrf_token": _csrf(admin_client), "confirm": "yes"})
    with db_app.app_context():
        lead = db.session.get(ApplicantLead, lead_id)
        assert lead.anonymized_at is not None and lead.application_id == app_id
        assert "Wanjiru" not in lead.applicant_name and lead.email is None and lead.follow_up_notes is None
        assert "712345678" not in lead.normalized_phone + lead.phone_number
        assert Application.query.count() == 1
    html = admin_client.get(f"/admin/leads/{lead_id}").get_data(as_text=True)
    assert "wa.me" not in html and "tel:" not in html


def test_existing_admin_pages_still_render_with_nav_link(admin_client):
    for path in ("/admin/", "/admin/applications", "/admin/scholarships"):
        resp = admin_client.get(path)
        assert resp.status_code == 200
        assert b"Applicant Leads" in resp.data
