"""API-layer tests: public blueprint (Step 5)."""

from tests._helpers import seed_minimal_catalogue


def test_get_schools_returns_envelope(db_app, db_client):
    with db_app.app_context():
        seed_minimal_catalogue()
    resp = db_client.get("/api/schools")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert len(data["data"]) == 1
    assert data["data"][0]["slug"] == "health"


def test_get_school_detail_found(db_app, db_client):
    with db_app.app_context():
        seed_minimal_catalogue()
    resp = db_client.get("/api/schools/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["data"]["slug"] == "health"
    assert len(data["data"]["departments"]) == 1


def test_get_school_detail_not_found(db_app, db_client):
    with db_app.app_context():
        seed_minimal_catalogue()
    resp = db_client.get("/api/schools/does-not-exist")
    assert resp.status_code == 404
    data = resp.get_json()
    assert data["success"] is False


def test_list_programmes_with_type_filter(db_app, db_client):
    with db_app.app_context():
        seed_minimal_catalogue()
    resp = db_client.get("/api/programmes?type=academic")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["data"]["total"] == 1
    assert data["data"]["items"][0]["programme_type"] == "academic"


def test_list_programmes_includes_level_class_for_badge_styling(db_app, db_client):
    """Step 7: level_class must be serialized so the frontend catalogue
    bridge can preserve the existing programme-level badge colors."""
    with db_app.app_context():
        seed_minimal_catalogue()
    resp = db_client.get("/api/programmes?type=academic&school=health")
    data = resp.get_json()["data"]
    assert data["items"][0]["level_class"] == "diploma"


def test_list_programmes_invalid_type_returns_422(db_app, db_client):
    with db_app.app_context():
        seed_minimal_catalogue()
    resp = db_client.get("/api/programmes?type=bogus")
    assert resp.status_code == 422
    data = resp.get_json()
    assert data["success"] is False
    assert "errors" in data


def test_get_programme_detail_includes_faqs_and_features(db_app, db_client):
    with db_app.app_context():
        seed_minimal_catalogue()
    resp = db_client.get("/api/programmes/ai-ml")
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert len(data["faqs"]) == 1
    assert len(data["features"]) == 1
    assert data["pricing"]["type"] == "per_mode_fee"


def test_list_programme_categories(db_app, db_client):
    with db_app.app_context():
        seed_minimal_catalogue()
    resp = db_client.get("/api/programme-categories")
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data[0]["slug"] == "ai"
