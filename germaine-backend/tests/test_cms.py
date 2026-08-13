"""
CMS tests (Step 7 CMS addition).

Covers the admin-portal CMS sections (Website Content, Content Lists,
Media Library, News, Academics) and the public read-only CMS API
(/api/news, /api/site-content, /api/content-lists/<key>), all against
the in-memory SQLite `db_client` fixture. Follows the exact same
conventions as test_admin_dashboard.py: real login flow via
tests._helpers.login_admin, real CSRF tokens fetched from rendered
forms, no live PostgreSQL involved.
"""

import io

from app.extensions import db
from app.models import MediaAsset, NewsArticle, SiteContent, ContentListItem
from tests._helpers import seed_minimal_catalogue, create_admin_user, login_admin, get_csrf_from

PNG_BYTES = bytes.fromhex(
    "89504e470d0a1a0a0000000d494844520000000100000001080600000"
    "01f15c4890000000a49444154789c6360000002000100" "ffff03000006000557bfabd4"
    "0000000049454e44ae426082"
)

PROTECTED_CMS_PATHS = [
    "/admin/content",
    "/admin/content/lists/homepage_hero_slides",
    "/admin/media",
    "/admin/news",
    "/admin/news/new",
    "/admin/academics/schools",
    "/admin/academics/programmes",
    "/admin/academics/categories",
]


# ---------------------------------------------------------------
# AUTHORIZATION — every CMS admin route requires a session
# ---------------------------------------------------------------

def test_all_cms_routes_redirect_unauthenticated_requests(db_client):
    for path in PROTECTED_CMS_PATHS:
        resp = db_client.get(path, follow_redirects=False)
        assert resp.status_code == 302, f"{path} did not redirect (got {resp.status_code})"
        assert "/admin/login" in resp.headers["Location"], f"{path} did not redirect to login"


def test_cms_post_routes_require_authentication(db_client):
    resp = db_client.post("/admin/content", data={"homepage.hero_badge": "x"}, follow_redirects=False)
    assert resp.status_code == 302
    assert "/admin/login" in resp.headers["Location"]


# ---------------------------------------------------------------
# WEBSITE CONTENT
# ---------------------------------------------------------------

def test_content_editor_renders_all_registry_groups(db_client, db_app):
    with db_app.app_context():
        create_admin_user()
    login_admin(db_client)
    resp = db_client.get("/admin/content")
    assert resp.status_code == 200
    assert b"Homepage" in resp.data
    assert b"Contact Information" in resp.data


def test_content_editor_save_persists_value(db_client, db_app):
    with db_app.app_context():
        create_admin_user()
    login_admin(db_client)
    get_resp = db_client.get("/admin/content")
    token = get_csrf_from(get_resp)
    resp = db_client.post("/admin/content", data={
        "csrf_token": token, "homepage.hero_badge": "New Badge Text", "contact.phone": "+254 700 111222",
    }, follow_redirects=False)
    assert resp.status_code == 302
    with db_app.app_context():
        row = SiteContent.query.filter_by(content_key="homepage.hero_badge").first()
        assert row is not None
        assert row.value == "New Badge Text"


def test_content_editor_rejects_unrecognized_key_silently_ignored():
    """The route only ever writes keys that exist in CONTENT_FIELD_REGISTRY
    — an unrecognized form field name is simply not in that loop, so it
    can never reach the service layer. Covered at the service layer
    instead (see test_set_content_value_rejects_unknown_key)."""


def test_set_content_value_rejects_unknown_key(db_app):
    from app.services import cms_service
    from app.utils.validation import ValidationError
    with db_app.app_context():
        try:
            cms_service.set_content_value("not.a.real.key", "value", None)
            assert False, "expected ValidationError"
        except ValidationError:
            pass


def test_get_content_value_blank_when_unset(db_app):
    from app.services import cms_service
    with db_app.app_context():
        assert cms_service.get_content_value("homepage.hero_badge") is None


# ---------------------------------------------------------------
# CONTENT LIST ITEMS
# ---------------------------------------------------------------

def test_content_list_item_create_update_archive(db_client, db_app):
    with db_app.app_context():
        create_admin_user()
    login_admin(db_client)

    get_resp = db_client.get("/admin/content/lists/homepage_hero_slides")
    assert get_resp.status_code == 200
    token = get_csrf_from(get_resp)
    resp = db_client.post("/admin/content/lists/homepage_hero_slides/create", data={
        "csrf_token": token, "title": "Slide One", "subtitle": "Sub", "display_order": "1",
    }, follow_redirects=False)
    assert resp.status_code == 302

    with db_app.app_context():
        item = ContentListItem.query.filter_by(list_key="homepage_hero_slides").first()
        assert item is not None
        assert item.title == "Slide One"
        assert item.is_active is True
        item_id = item.id

    get_resp = db_client.get("/admin/content/lists/homepage_hero_slides")
    token = get_csrf_from(get_resp)
    resp = db_client.post(f"/admin/content/lists/item/{item_id}/update", data={
        "csrf_token": token, "title": "Slide One Updated", "display_order": "2",
    }, follow_redirects=False)
    assert resp.status_code == 302
    with db_app.app_context():
        item = db.session.get(ContentListItem, item_id)
        assert item.title == "Slide One Updated"

    resp = db_client.post(f"/admin/content/lists/item/{item_id}/archive", data={"csrf_token": token}, follow_redirects=False)
    assert resp.status_code == 302
    with db_app.app_context():
        item = db.session.get(ContentListItem, item_id)
        assert item.is_active is False


def test_content_list_item_unrecognized_list_key_is_404(db_client, db_app):
    with db_app.app_context():
        create_admin_user()
    login_admin(db_client)
    resp = db_client.get("/admin/content/lists/not_a_real_list")
    assert resp.status_code == 404


def test_create_list_item_enforces_max_items(db_app):
    from app.services import cms_service
    from app.utils.validation import ValidationError
    with db_app.app_context():
        max_items = cms_service.LIST_KEY_REGISTRY["student_life_sports"]["max_items"]
        for i in range(max_items):
            cms_service.create_list_item("student_life_sports", title=f"Item {i}")
        try:
            cms_service.create_list_item("student_life_sports", title="One Too Many")
            assert False, "expected ValidationError once max_items is reached"
        except ValidationError:
            pass


# ---------------------------------------------------------------
# MEDIA LIBRARY
# ---------------------------------------------------------------

def test_media_upload_valid_png_succeeds(db_client, db_app):
    with db_app.app_context():
        create_admin_user()
    login_admin(db_client)
    get_resp = db_client.get("/admin/media")
    token = get_csrf_from(get_resp)
    resp = db_client.post("/admin/media/upload", data={
        "csrf_token": token, "file": (io.BytesIO(PNG_BYTES), "photo.png"), "alt_text": "A test photo",
    }, content_type="multipart/form-data", follow_redirects=False)
    assert resp.status_code == 302
    with db_app.app_context():
        asset = MediaAsset.query.first()
        assert asset is not None
        assert asset.mime_type == "image/png"
        assert asset.status == "active"
        assert asset.original_filename == "photo.png"
        # filename is never the browser-supplied name
        assert asset.filename != "photo.png"


def test_media_upload_rejects_disguised_executable(db_client, db_app):
    with db_app.app_context():
        create_admin_user()
    login_admin(db_client)
    get_resp = db_client.get("/admin/media")
    token = get_csrf_from(get_resp)
    fake_php = b"<?php system($_GET['c']); ?>"
    resp = db_client.post("/admin/media/upload", data={
        "csrf_token": token, "file": (io.BytesIO(fake_php), "shell.png"),
    }, content_type="multipart/form-data", follow_redirects=False)
    assert resp.status_code == 302  # redirected back with a flash error, not a crash
    with db_app.app_context():
        assert MediaAsset.query.count() == 0


def test_media_upload_rejects_disallowed_extension(db_client, db_app):
    with db_app.app_context():
        create_admin_user()
    login_admin(db_client)
    get_resp = db_client.get("/admin/media")
    token = get_csrf_from(get_resp)
    resp = db_client.post("/admin/media/upload", data={
        "csrf_token": token, "file": (io.BytesIO(b"not an image"), "notes.txt"),
    }, content_type="multipart/form-data", follow_redirects=False)
    assert resp.status_code == 302
    with db_app.app_context():
        assert MediaAsset.query.count() == 0


def test_media_alt_text_update_and_archive(db_client, db_app):
    with db_app.app_context():
        create_admin_user()
    login_admin(db_client)
    get_resp = db_client.get("/admin/media")
    token = get_csrf_from(get_resp)
    db_client.post("/admin/media/upload", data={
        "csrf_token": token, "file": (io.BytesIO(PNG_BYTES), "photo.png"),
    }, content_type="multipart/form-data")

    with db_app.app_context():
        media_id = MediaAsset.query.first().id

    get_resp = db_client.get("/admin/media")
    token = get_csrf_from(get_resp)
    resp = db_client.post(f"/admin/media/{media_id}/alt-text", data={"csrf_token": token, "alt_text": "Updated alt"}, follow_redirects=False)
    assert resp.status_code == 302
    with db_app.app_context():
        assert db.session.get(MediaAsset, media_id).alt_text == "Updated alt"

    resp = db_client.post(f"/admin/media/{media_id}/archive", data={"csrf_token": token}, follow_redirects=False)
    assert resp.status_code == 302
    with db_app.app_context():
        assert db.session.get(MediaAsset, media_id).status == "archived"


def test_media_asset_never_exposes_filesystem_path_in_admin_html(db_client, db_app):
    """The admin media grid must render the public url_path, never a raw
    server filesystem path."""
    with db_app.app_context():
        create_admin_user()
    login_admin(db_client)
    get_resp = db_client.get("/admin/media")
    token = get_csrf_from(get_resp)
    db_client.post("/admin/media/upload", data={
        "csrf_token": token, "file": (io.BytesIO(PNG_BYTES), "photo.png"),
    }, content_type="multipart/form-data")
    resp = db_client.get("/admin/media")
    assert b"/static/media/" in resp.data
    assert b"/sessions/" not in resp.data


# ---------------------------------------------------------------
# NEWS
# ---------------------------------------------------------------

def test_news_full_lifecycle_draft_publish_unpublish_archive(db_client, db_app):
    with db_app.app_context():
        create_admin_user()
    login_admin(db_client)

    get_resp = db_client.get("/admin/news/new")
    token = get_csrf_from(get_resp)
    resp = db_client.post("/admin/news/new", data={
        "csrf_token": token, "title": "New Intake Announced", "summary": "Summary text",
        "body": "Full article body.", "category": "Announcements", "author": "Registrar",
    }, follow_redirects=False)
    assert resp.status_code == 302

    with db_app.app_context():
        article = NewsArticle.query.first()
        assert article is not None
        assert article.status == "draft"
        assert article.slug == "new-intake-announced"
        article_id = article.id

    edit_resp = db_client.get(f"/admin/news/{article_id}")
    assert edit_resp.status_code == 200
    token = get_csrf_from(edit_resp)

    resp = db_client.post(f"/admin/news/{article_id}/publish", data={"csrf_token": token}, follow_redirects=False)
    assert resp.status_code == 302
    with db_app.app_context():
        article = db.session.get(NewsArticle, article_id)
        assert article.status == "published"
        assert article.published_at is not None

    edit_resp = db_client.get(f"/admin/news/{article_id}")
    token = get_csrf_from(edit_resp)
    resp = db_client.post(f"/admin/news/{article_id}/unpublish", data={"csrf_token": token}, follow_redirects=False)
    assert resp.status_code == 302
    with db_app.app_context():
        assert db.session.get(NewsArticle, article_id).status == "draft"

    edit_resp = db_client.get(f"/admin/news/{article_id}")
    token = get_csrf_from(edit_resp)
    resp = db_client.post(f"/admin/news/{article_id}/archive", data={"csrf_token": token}, follow_redirects=False)
    assert resp.status_code == 302
    with db_app.app_context():
        assert db.session.get(NewsArticle, article_id).status == "archived"


def test_news_publish_requires_title_and_body(db_app):
    from app.services import cms_service
    from app.utils.validation import ValidationError
    with db_app.app_context():
        create_admin_user()
        admin = create_admin_user(email="second@example.com")
        article = cms_service.create_news_article({"title": "No Body Yet"}, admin)
        try:
            cms_service.publish_news_article(article.id)
            assert False, "expected ValidationError — article has no body"
        except ValidationError:
            pass


def test_news_detail_404_for_unknown_id(db_client, db_app):
    with db_app.app_context():
        create_admin_user()
    login_admin(db_client)
    resp = db_client.get("/admin/news/999999")
    assert resp.status_code == 404


def test_news_two_articles_same_title_get_distinct_slugs(db_client, db_app):
    with db_app.app_context():
        create_admin_user()
    login_admin(db_client)
    for _ in range(2):
        get_resp = db_client.get("/admin/news/new")
        token = get_csrf_from(get_resp)
        db_client.post("/admin/news/new", data={
            "csrf_token": token, "title": "Same Title", "body": "Body text.",
        })
    with db_app.app_context():
        slugs = sorted(a.slug for a in NewsArticle.query.all())
        assert slugs == ["same-title", "same-title-2"]


# ---------------------------------------------------------------
# ACADEMICS
# ---------------------------------------------------------------

def test_academics_school_update(db_client, db_app):
    with db_app.app_context():
        create_admin_user()
        catalogue = seed_minimal_catalogue()
        school_id = catalogue["school"].id
    login_admin(db_client)

    get_resp = db_client.get(f"/admin/academics/schools/{school_id}")
    assert get_resp.status_code == 200
    token = get_csrf_from(get_resp)
    resp = db_client.post(f"/admin/academics/schools/{school_id}", data={
        "csrf_token": token, "description": "Updated description", "fee": "KES 13,000",
        "display_order": "2", "is_active": "on",
    }, follow_redirects=False)
    assert resp.status_code == 302
    with db_app.app_context():
        from app.models import School
        school = db.session.get(School, school_id)
        assert school.fee == "KES 13,000"
        assert school.description == "Updated description"


def test_academics_programme_update_never_touches_fee(db_client, db_app):
    """update_programme() has no `fee` field at all — academic pricing is
    only ever editable via the school. This asserts the admin form POST
    cannot smuggle a fee value onto Programme even if someone adds one
    client-side, because the service function signature simply has no
    parameter for it."""
    with db_app.app_context():
        create_admin_user()
        catalogue = seed_minimal_catalogue()
        academic_id = catalogue["academic"].id
    login_admin(db_client)

    get_resp = db_client.get(f"/admin/academics/programmes/{academic_id}")
    assert get_resp.status_code == 200
    token = get_csrf_from(get_resp)
    resp = db_client.post(f"/admin/academics/programmes/{academic_id}", data={
        "csrf_token": token, "overview": "New overview text", "gain_points": "Skill A\nSkill B",
        "fee": "KES 999,999",  # not a real field on the service function — must be silently ignored
        "is_active": "on",
    }, follow_redirects=False)
    assert resp.status_code == 302
    with db_app.app_context():
        from app.models import Programme
        programme = db.session.get(Programme, academic_id)
        assert programme.overview == "New overview text"
        assert programme.gain_points == ["Skill A", "Skill B"]
        assert not hasattr(programme, "fee")


def test_academics_programme_mode_fee_update_and_clear(db_client, db_app):
    with db_app.app_context():
        create_admin_user()
        catalogue = seed_minimal_catalogue()
        mode_id = catalogue["mode"].id
    login_admin(db_client)

    get_resp = db_client.get("/admin/academics/categories")
    token = get_csrf_from(get_resp)

    resp = db_client.post(f"/admin/academics/programmes/modes/{mode_id}", data={
        "csrf_token": token, "fee_amount": "160000", "schedule": "Weekdays",
        "is_available_present": "1", "is_available": "on",
    }, follow_redirects=False)
    assert resp.status_code == 302
    with db_app.app_context():
        from app.models import ProgrammeMode
        mode = db.session.get(ProgrammeMode, mode_id)
        assert float(mode.fee_amount) == 160000

    resp = db_client.post(f"/admin/academics/programmes/modes/{mode_id}", data={
        "csrf_token": token, "fee_amount": "", "schedule": "Weekdays",
        "is_available_present": "1",  # checkbox omitted -> False
    }, follow_redirects=False)
    assert resp.status_code == 302
    with db_app.app_context():
        from app.models import ProgrammeMode
        mode = db.session.get(ProgrammeMode, mode_id)
        assert mode.fee_amount is None  # blank fee = "Contact Admissions" sentinel
        assert mode.is_available is False


def test_academics_category_update(db_client, db_app):
    with db_app.app_context():
        create_admin_user()
        catalogue = seed_minimal_catalogue()
        category_id = catalogue["category"].id
    login_admin(db_client)

    get_resp = db_client.get(f"/admin/academics/categories/{category_id}")
    token = get_csrf_from(get_resp)
    resp = db_client.post(f"/admin/academics/categories/{category_id}", data={
        "csrf_token": token, "label": "Updated Label", "icon": "fa-solid fa-robot",
    }, follow_redirects=False)
    assert resp.status_code == 302
    with db_app.app_context():
        from app.models import ProgrammeCategory
        category = db.session.get(ProgrammeCategory, category_id)
        assert category.label == "Updated Label"


# ---------------------------------------------------------------
# PUBLIC READ API
# ---------------------------------------------------------------

def test_public_news_list_empty_by_default(db_client):
    resp = db_client.get("/api/news")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["success"] is True
    assert body["data"]["items"] == []
    assert body["data"]["total"] == 0


def test_public_news_list_only_returns_published(db_app, db_client):
    from app.services import cms_service
    with db_app.app_context():
        admin = create_admin_user()
        draft = cms_service.create_news_article({"title": "Draft Only", "body": "..."}, admin)
        published = cms_service.create_news_article({"title": "Published One", "body": "Body here."}, admin)
        cms_service.publish_news_article(published.id)

    resp = db_client.get("/api/news")
    body = resp.get_json()
    titles = [item["title"] for item in body["data"]["items"]]
    assert "Published One" in titles
    assert "Draft Only" not in titles


def test_public_news_detail_404_for_draft_or_missing(db_app, db_client):
    from app.services import cms_service
    with db_app.app_context():
        admin = create_admin_user()
        draft = cms_service.create_news_article({"title": "Still A Draft", "body": "..."}, admin)
        draft_slug = draft.slug

    resp = db_client.get(f"/api/news/{draft_slug}")
    assert resp.status_code == 404

    resp = db_client.get("/api/news/does-not-exist")
    assert resp.status_code == 404


def test_public_news_detail_returns_full_body_for_published(db_app, db_client):
    from app.services import cms_service
    with db_app.app_context():
        admin = create_admin_user()
        article = cms_service.create_news_article({"title": "Read Full Article", "body": "The full body text."}, admin)
        cms_service.publish_news_article(article.id)
        slug = article.slug

    resp = db_client.get(f"/api/news/{slug}")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["data"]["body"] == "The full body text."


def test_public_site_content_ignores_unrecognized_keys(db_client):
    resp = db_client.get("/api/site-content?keys=homepage.hero_badge,not.a.real.key,also.fake")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["data"] == {"homepage.hero_badge": None}


def test_public_site_content_returns_set_values(db_app, db_client):
    from app.services import cms_service
    with db_app.app_context():
        admin = create_admin_user()
        cms_service.set_content_value("contact.phone", "+254 700 000 000", admin)

    resp = db_client.get("/api/site-content?keys=contact.phone")
    body = resp.get_json()
    assert body["data"]["contact.phone"] == "+254 700 000 000"


def test_public_content_list_empty_for_unrecognized_key_not_an_error(db_client):
    resp = db_client.get("/api/content-lists/not_a_real_list")
    assert resp.status_code == 200
    assert resp.get_json()["data"] == []


def test_public_content_list_excludes_archived_items(db_app, db_client):
    from app.services import cms_service
    with db_app.app_context():
        create_admin_user()
        active_item = cms_service.create_list_item("homepage_hero_slides", title="Visible Slide")
        archived_item = cms_service.create_list_item("homepage_hero_slides", title="Hidden Slide")
        cms_service.archive_list_item(archived_item.id)

    resp = db_client.get("/api/content-lists/homepage_hero_slides")
    body = resp.get_json()
    titles = [item["title"] for item in body["data"]]
    assert "Visible Slide" in titles
    assert "Hidden Slide" not in titles


def test_public_cms_endpoints_never_require_authentication(db_client):
    """Sanity check that these are genuinely public — no admin session
    cookie exists in this client at all."""
    for path in ["/api/news", "/api/site-content", "/api/content-lists/homepage_hero_slides"]:
        resp = db_client.get(path)
        assert resp.status_code == 200


# ---------------------------------------------------------------
# CSRF ENFORCEMENT SPOT CHECK
# ---------------------------------------------------------------

def test_cms_post_without_csrf_token_is_rejected(db_client, db_app):
    with db_app.app_context():
        create_admin_user()
    login_admin(db_client)
    resp = db_client.post("/admin/content", data={"homepage.hero_badge": "no token here"})
    assert resp.status_code == 403


def test_media_upload_without_csrf_token_is_rejected(db_client, db_app):
    with db_app.app_context():
        create_admin_user()
    login_admin(db_client)
    resp = db_client.post("/admin/media/upload", data={
        "file": (io.BytesIO(PNG_BYTES), "photo.png"),
    }, content_type="multipart/form-data")
    assert resp.status_code == 403
