"""API-layer tests: admissions blueprint (Step 5)."""

from tests._helpers import seed_minimal_catalogue


def _seed(db_app):
    with db_app.app_context():
        return seed_minimal_catalogue()["academic"].id


def test_create_application_success(db_app, db_client):
    programme_id = _seed(db_app)
    resp = db_client.post("/api/admissions/applications", json={
        "full_name": "Jane Wanjiru", "email": "jane@example.com",
        "phone": "254712345678", "programme_id": programme_id, "consent": True,
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["success"] is True
    assert data["data"]["reference_code"].startswith("GTI-")
    assert data["data"]["status"] == "submitted"


def test_create_application_missing_fields_returns_422(db_app, db_client):
    _seed(db_app)
    resp = db_client.post("/api/admissions/applications", json={})
    assert resp.status_code == 422
    data = resp.get_json()
    assert data["success"] is False
    assert "full_name" in data["errors"]


def test_create_application_unknown_programme_returns_404(db_app, db_client):
    _seed(db_app)
    resp = db_client.post("/api/admissions/applications", json={
        "full_name": "Jane Wanjiru", "email": "jane@example.com",
        "phone": "254712345678", "programme_id": 999999, "consent": True,
    })
    assert resp.status_code == 404


def test_get_application_status_by_reference_code(db_app, db_client):
    programme_id = _seed(db_app)
    create_resp = db_client.post("/api/admissions/applications", json={
        "full_name": "Jane Wanjiru", "email": "jane2@example.com",
        "phone": "254712345678", "programme_id": programme_id, "consent": True,
    })
    ref_code = create_resp.get_json()["data"]["reference_code"]

    status_resp = db_client.get(f"/api/admissions/applications/{ref_code}")
    assert status_resp.status_code == 200
    assert status_resp.get_json()["data"]["reference_code"] == ref_code


def test_get_application_status_unknown_reference_code_returns_404(db_app, db_client):
    _seed(db_app)
    resp = db_client.get("/api/admissions/applications/GTI-000000-ZZZZ")
    assert resp.status_code == 404


def test_get_scholarship_info(db_app, db_client):
    _seed(db_app)
    resp = db_client.get("/api/admissions/scholarship-info")
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["application_type"] == "scholarship"
    assert "full_name" in data["required_fields"]
