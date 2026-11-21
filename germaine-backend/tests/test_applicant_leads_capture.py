"""
Applicant lead capture — public endpoint, deduplication and application
linking (master spec §2–§4, §8–§9; test scenarios 1–9).

Runs against the in-memory SQLite `db_client` fixture (same as the rest of
this suite). tests/test_applicant_leads_postgres.py re-runs the concurrency
and migration checks against a real, throwaway PostgreSQL database when one
is configured. No production database is ever used.
"""

import secrets
from unittest import mock

import pytest

from app.blueprints.admissions import routes as admissions_routes
from app.extensions import db
from app.models import Applicant, ApplicantLead, Application
from app.services import lead_service
from app.utils.phone import normalize_kenyan_phone
from tests._helpers import seed_minimal_catalogue

URL = "/api/admissions/leads/capture"


@pytest.fixture(autouse=True)
def _reset_limiters():
    admissions_routes._lead_ip_limiter.reset()
    admissions_routes._lead_token_limiter.reset()
    yield


def new_token():
    return secrets.token_hex(32)


def capture(client, token, **fields):
    body = {"lead_token": token, "applicant_name": "Wanjiru Kamau", "phone_number": "712345678"}
    body.update(fields)
    return client.post(URL, json=body)


# ---------------------------------------------------------------
# Phone normalization
# ---------------------------------------------------------------

@pytest.mark.parametrize("raw", [
    "712345678", "0712345678", "0712 345 678", "+254712345678", "254712345678",
    "+254 712-345-678", "2540712345678", "(0712) 345678",
])
def test_kenyan_formats_normalize_to_one_value(raw):
    assert normalize_kenyan_phone(raw) == "254712345678"


def test_safaricom_01_range_supported():
    assert normalize_kenyan_phone("0110123456") == "254110123456"


@pytest.mark.parametrize("raw", [
    "", "12345", "0812345678", "071234567", "07123456789", "+1 415 555 0100",
    "07a2345678", "254", "25471234567890", "0000000000", None, 712345678,
])
def test_invalid_phone_numbers_rejected(raw):
    assert normalize_kenyan_phone(raw) is None


# ---------------------------------------------------------------
# Test 1 — enter name + phone, abandon: lead is saved
# ---------------------------------------------------------------

def test_1_abandoned_form_still_leaves_a_lead(db_client, db_app):
    resp = capture(db_client, new_token())
    assert resp.status_code == 200
    body = resp.get_json()
    assert body == {"success": True, "data": {"captured": True}, "message": "OK"}
    with db_app.app_context():
        lead = ApplicantLead.query.one()
        assert lead.applicant_name == "Wanjiru Kamau"
        assert lead.normalized_phone == "254712345678"
        assert lead.lead_status == "new_lead"
        assert lead.application_id is None
        assert lead.application_status == "Incomplete"
        assert len(lead.lead_token_hash) == 64  # hash stored, never the raw token


def test_response_never_exposes_lead_data(db_client):
    token = new_token()
    capture(db_client, token)
    resp = capture(db_client, token, email="wk@example.com")
    text = resp.get_data(as_text=True)
    for leaked in ("Wanjiru", "712345678", "wk@example.com", token, '"id"'):
        assert leaked not in text


# ---------------------------------------------------------------
# Test 2 / 7 — continuing / many keystrokes: one record
# ---------------------------------------------------------------

def test_2_continuing_the_form_updates_same_lead_and_adds_details(db_client, db_app):
    token = new_token()
    capture(db_client, token)
    capture(db_client, token, email="WK@Example.com")
    capture(db_client, token, email="wk@example.com", school="health", programme="Diploma in Nursing")
    with db_app.app_context():
        lead = ApplicantLead.query.one()
        assert lead.email == "wk@example.com"
        assert lead.programme == "Diploma in Nursing"
        assert lead.school == "health"


def test_7_repeated_requests_while_typing_create_no_duplicates(db_client, db_app):
    token = new_token()
    for name in ["Wan", "Wanj", "Wanjiru", "Wanjiru K", "Wanjiru Kamau", "Wanjiru Kamau", "Wanjiru Kamau"]:
        capture(db_client, token, applicant_name=name)
    with db_app.app_context():
        assert ApplicantLead.query.count() == 1
        assert ApplicantLead.query.one().applicant_name == "Wanjiru Kamau"


def test_optional_fields_are_not_blanked_by_a_later_request(db_client, db_app):
    token = new_token()
    capture(db_client, token, email="wk@example.com", programme="Diploma in Nursing")
    capture(db_client, token)  # later request omits optional fields
    with db_app.app_context():
        lead = ApplicantLead.query.one()
        assert lead.email == "wk@example.com" and lead.programme == "Diploma in Nursing"


def test_first_captured_at_preserved_and_last_updated_moves(db_client, db_app):
    token = new_token()
    capture(db_client, token)
    with db_app.app_context():
        first = ApplicantLead.query.one().first_captured_at
    capture(db_client, token, applicant_name="Wanjiru Njeri Kamau")
    with db_app.app_context():
        lead = ApplicantLead.query.one()
        assert lead.first_captured_at == first
        assert lead.last_updated_at >= first


# ---------------------------------------------------------------
# Test 3 — phone number corrected
# ---------------------------------------------------------------

def test_3_changing_phone_updates_the_existing_lead(db_client, db_app):
    token = new_token()
    capture(db_client, token, phone_number="712345678")
    capture(db_client, token, phone_number="0722000111")
    with db_app.app_context():
        lead = ApplicantLead.query.one()
        assert lead.normalized_phone == "254722000111"
        assert lead.phone_number == "0722000111"


# ---------------------------------------------------------------
# Test 4 / 8 — revisit; existing lead encountered
# ---------------------------------------------------------------

def test_4_revisit_with_same_browser_token_reuses_lead(db_client, db_app):
    token = new_token()
    capture(db_client, token)
    # ...applicant closes the tab, comes back days later (same localStorage token)
    capture(db_client, token, programme="Diploma in Nursing")
    with db_app.app_context():
        assert ApplicantLead.query.count() == 1


def test_8_same_phone_from_different_browser_is_not_merged_or_overwritten(db_client, db_app):
    capture(db_client, new_token(), applicant_name="Wanjiru Kamau")
    capture(db_client, new_token(), applicant_name="Somebody Else")
    with db_app.app_context():
        leads = ApplicantLead.query.order_by(ApplicantLead.id).all()
        assert [l.applicant_name for l in leads] == ["Wanjiru Kamau", "Somebody Else"]
        # flagged for the admin instead of silently merged
        assert lead_service.possible_duplicates(leads[0]) == [leads[1]]


# ---------------------------------------------------------------
# Test 6 — invalid input is never saved
# ---------------------------------------------------------------

@pytest.mark.parametrize("fields", [
    {"phone_number": "12345"},
    {"phone_number": "0812345678"},
    {"phone_number": ""},
    {"applicant_name": "A"},
    {"applicant_name": "12345"},
    {"applicant_name": "<script>alert(1)</script>"},
    {"lead_token": "short"},
    {"lead_token": None},
    {"application_type": "hacker"},
])
def test_6_invalid_details_are_rejected_and_not_saved(db_client, db_app, fields):
    resp = capture(db_client, new_token(), **fields)
    assert resp.status_code == 422
    with db_app.app_context():
        assert ApplicantLead.query.count() == 0


def test_invalid_optional_email_is_ignored_not_saved(db_client, db_app):
    capture(db_client, new_token(), email="not-an-email")
    with db_app.app_context():
        assert ApplicantLead.query.one().email is None


def test_non_json_and_oversized_bodies_rejected(db_client, db_app):
    assert db_client.post(URL, data="hello", content_type="text/plain").status_code == 400
    big = {"lead_token": new_token(), "applicant_name": "Wanjiru Kamau", "phone_number": "712345678",
           "programme": "x" * 5000}
    assert db_client.post(URL, json=big).status_code == 413
    with db_app.app_context():
        assert ApplicantLead.query.count() == 0


def test_honeypot_submission_is_silently_dropped(db_client, db_app):
    resp = capture(db_client, new_token(), website="http://spam.example")
    assert resp.status_code == 200
    with db_app.app_context():
        assert ApplicantLead.query.count() == 0


def test_throttling_limits_bursts(db_client):
    codes = [capture(db_client, new_token()).status_code for _ in range(35)]
    assert codes[:30] == [200] * 30
    assert 429 in codes[30:]


def test_get_is_not_allowed_on_capture_endpoint(db_client):
    assert db_client.get(URL).status_code == 405


# ---------------------------------------------------------------
# Test 5 — successful submission links the lead
# ---------------------------------------------------------------

def _application_payload(catalogue, **overrides):
    payload = {
        "full_name": "Wanjiru Kamau", "email": "wk@example.com", "phone": "254712345678",
        "programme_id": catalogue["academic"].id, "application_type": "scholarship", "consent": True,
    }
    payload.update(overrides)
    return payload


def test_5_successful_submission_links_lead_by_token(db_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        payload = _application_payload(catalogue)
    token = new_token()
    capture(db_client, token)
    with db_app.app_context():
        first = ApplicantLead.query.one().first_captured_at

    resp = db_client.post("/api/admissions/applications", json={**payload, "lead_token": token})
    assert resp.status_code == 201
    with db_app.app_context():
        lead = ApplicantLead.query.one()
        app_row = Application.query.one()
        assert lead.application_id == app_row.id
        assert lead.lead_status == "application_submitted"
        assert lead.application_status == "Submitted"
        assert lead.first_captured_at == first
        assert lead.email == "wk@example.com"
        assert lead.programme == "Diploma in Nursing"
        assert ApplicantLead.query.count() == 1


def test_submission_without_token_links_by_phone_only_when_unambiguous(db_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        payload = _application_payload(catalogue)
    capture(db_client, new_token(), phone_number="0712345678")
    resp = db_client.post("/api/admissions/applications", json=payload)  # e.g. AI Bootcamp form, no token
    assert resp.status_code == 201
    with db_app.app_context():
        assert ApplicantLead.query.one().lead_status == "application_submitted"


def test_ambiguous_phone_match_does_not_link_anything(db_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        payload = _application_payload(catalogue)
    capture(db_client, new_token(), applicant_name="Wanjiru Kamau")
    capture(db_client, new_token(), applicant_name="Another Person")
    assert db_client.post("/api/admissions/applications", json=payload).status_code == 201
    with db_app.app_context():
        assert all(l.application_id is None for l in ApplicantLead.query.all())


def test_starting_the_form_never_marks_a_lead_submitted(db_client, db_app):
    token = new_token()
    capture(db_client, token, lead_status="application_submitted", application_id=1)
    with db_app.app_context():
        lead = ApplicantLead.query.one()
        assert lead.lead_status == "new_lead" and lead.application_id is None


def test_failed_submission_does_not_link_or_mark_submitted(db_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        payload = _application_payload(catalogue, programme_id=99999)  # invalid programme
    token = new_token()
    capture(db_client, token)
    resp = db_client.post("/api/admissions/applications", json={**payload, "lead_token": token})
    assert resp.status_code == 404
    with db_app.app_context():
        lead = ApplicantLead.query.one()
        assert lead.application_id is None and lead.lead_status == "new_lead"


def test_captures_after_submission_do_not_overwrite_submitted_details(db_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        payload = _application_payload(catalogue)
    token = new_token()
    capture(db_client, token)
    db_client.post("/api/admissions/applications", json={**payload, "lead_token": token})
    capture(db_client, token, applicant_name="Someone Else", phone_number="0722000111")
    with db_app.app_context():
        lead = ApplicantLead.query.one()
        assert lead.applicant_name == "Wanjiru Kamau" and lead.normalized_phone == "254712345678"


def test_lead_linking_failure_never_breaks_the_application(db_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        payload = _application_payload(catalogue)
    with mock.patch.object(lead_service, "link_application", side_effect=RuntimeError("boom")):
        resp = db_client.post("/api/admissions/applications", json={**payload, "lead_token": new_token()})
    assert resp.status_code == 201
    assert resp.get_json()["data"]["reference_code"]
    with db_app.app_context():
        assert Application.query.count() == 1
        assert Applicant.query.count() == 1


# ---------------------------------------------------------------
# Test 9 — lead API failure never affects the form/submission
# ---------------------------------------------------------------

def test_9_capture_failure_returns_503_and_submission_still_works(db_client, db_app):
    with db_app.app_context():
        catalogue = seed_minimal_catalogue()
        payload = _application_payload(catalogue)
    with mock.patch.object(lead_service, "capture_lead", side_effect=RuntimeError("db down")):
        resp = capture(db_client, new_token())
    assert resp.status_code == 503
    assert "db down" not in resp.get_data(as_text=True)  # no internals leaked
    assert db_client.post("/api/admissions/applications", json=payload).status_code == 201


def test_safe_retry_after_failure_creates_one_lead(db_client, db_app):
    token = new_token()
    with mock.patch.object(lead_service, "capture_lead", side_effect=RuntimeError("blip")):
        capture(db_client, token)
    capture(db_client, token)
    capture(db_client, token)
    with db_app.app_context():
        assert ApplicantLead.query.count() == 1
