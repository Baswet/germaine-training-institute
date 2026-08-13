"""API-layer tests: alumni + enquiries blueprints (Step 5)."""


def test_alumni_register_success(db_client):
    resp = db_client.post("/api/alumni/register", json={
        "full_name": "John Otieno", "email": "john@example.com",
        "phone": "254700000000", "consent": True,
    })
    assert resp.status_code == 201
    assert resp.get_json()["success"] is True


def test_alumni_register_missing_email_returns_422(db_client):
    resp = db_client.post("/api/alumni/register", json={"full_name": "John Otieno"})
    assert resp.status_code == 422
    assert "email" in resp.get_json()["errors"]


def test_graduate_request_success(db_client):
    resp = db_client.post("/api/enquiries/graduate-requests", json={
        "employer_name": "Acme Ltd", "email": "hr@acme.example.com",
    })
    assert resp.status_code == 201


def test_partner_enquiry_invalid_type_returns_422(db_client):
    resp = db_client.post("/api/enquiries/partner-enquiries", json={
        "organisation": "Acme", "contact_name": "A", "email": "a@example.com",
        "enquiry_type": "bogus",
    })
    assert resp.status_code == 422


def test_partner_enquiry_success(db_client):
    resp = db_client.post("/api/enquiries/partner-enquiries", json={
        "organisation": "Acme", "contact_name": "A", "email": "a@example.com",
        "enquiry_type": "partnership",
    })
    assert resp.status_code == 201


def test_contact_message_success(db_client):
    resp = db_client.post("/api/enquiries/contact-messages", json={
        "name": "A", "email": "a@example.com", "message": "Hello there",
    })
    assert resp.status_code == 201


def test_contact_message_missing_message_returns_422(db_client):
    resp = db_client.post("/api/enquiries/contact-messages", json={
        "name": "A", "email": "a@example.com",
    })
    assert resp.status_code == 422


def test_newsletter_subscribe_success(db_client):
    resp = db_client.post("/api/enquiries/newsletter-subscriptions", json={
        "email": "sub@example.com", "source_page": "home",
    })
    assert resp.status_code == 201


def test_newsletter_subscribe_idempotent_via_api(db_client):
    payload = {"email": "sub2@example.com"}
    r1 = db_client.post("/api/enquiries/newsletter-subscriptions", json=payload)
    r2 = db_client.post("/api/enquiries/newsletter-subscriptions", json=payload)
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.get_json()["data"]["id"] == r2.get_json()["data"]["id"]
