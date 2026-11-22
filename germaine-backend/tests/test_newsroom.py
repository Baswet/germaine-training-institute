"""News & Events publication: service rules, public API, admin section, seed."""

import io
from datetime import date, timedelta

import pytest

from app.blueprints.public import newsroom_routes
from app.extensions import db
from app.models import NewsArticle
from app.models.newsroom import NewsArticleMeta, NewsEvent
from app.services import newsroom_seed, newsroom_service
from app.utils.validation import ValidationError
from tests._helpers import create_admin_user, get_csrf_from, login_admin


@pytest.fixture(autouse=True)
def _reset():
    newsroom_service.reset_view_throttle()
    newsroom_routes._view_limiter.reset()
    yield


@pytest.fixture()
def admin_client(db_client, db_app):
    with db_app.app_context():
        create_admin_user()
    login_admin(db_client)
    return db_client


def _story(**kw):
    data = dict(title="Test story", summary="An original summary.", news_category="kenya",
                source_name="Example News", source_url="https://example.com/a", is_external="1")
    data.update(kw)
    return newsroom_service.save_story(data)


# ------------------------------------------------------------ service rules
def test_external_story_needs_attribution_to_publish(db_app):
    a = _story(source_name="", source_url="")
    with pytest.raises(ValidationError) as ei:
        newsroom_service.publish_story(a.id)
    assert "source_name" in ei.value.errors and "source_url" in ei.value.errors
    assert db.session.get(NewsArticle, a.id).status == "draft"


def test_invalid_urls_rejected(db_app):
    with pytest.raises(ValidationError):
        _story(source_url="javascript:alert(1)")
    db.session.rollback()
    with pytest.raises(ValidationError):
        _story(video_url="https://evil.example/video")


def test_only_published_stories_public(db_app, db_client):
    draft = _story(title="Draft one", source_url="https://example.com/d")
    pub = _story(title="Live one", source_url="https://example.com/l")
    newsroom_service.publish_story(pub.id)
    items = db_client.get("/api/newsroom/stories").get_json()["data"]["items"]
    assert [i["title"] for i in items] == ["Live one"]
    assert db_client.get(f"/api/newsroom/stories/{draft.slug}").status_code == 404
    detail = db_client.get(f"/api/newsroom/stories/{pub.slug}").get_json()["data"]
    assert detail["source_name"] == "Example News" and detail["source_url"] == "https://example.com/l"


def test_category_filter_and_search(db_app, db_client):
    for i, cat in enumerate(["sports", "business", "sports"]):
        a = _story(title=f"Story {cat} {i}", news_category=cat, source_url=f"https://example.com/{i}")
        newsroom_service.publish_story(a.id)
    d = db_client.get("/api/newsroom/stories?category=sports").get_json()["data"]
    assert d["total"] == 2
    assert db_client.get("/api/newsroom/stories?category=politics").status_code == 422
    s = db_client.get("/api/newsroom/search?q=business").get_json()["data"]
    assert len(s["stories"]) == 1


def test_view_counter_is_real_and_throttled(db_app, db_client):
    a = _story()
    newsroom_service.publish_story(a.id)
    home = db_client.get("/api/newsroom/home").get_json()["data"]
    assert home["most_read"] == []  # no invented popularity
    assert db_client.post(f"/api/newsroom/stories/{a.slug}/view").get_json()["data"]["counted"] is True
    assert db_client.post(f"/api/newsroom/stories/{a.slug}/view").get_json()["data"]["counted"] is False
    assert NewsArticleMeta.query.filter_by(article_id=a.id).one().view_count == 1
    home = db_client.get("/api/newsroom/home").get_json()["data"]
    assert home["most_read"][0]["views"] == 1


def test_breaking_only_when_flagged(db_app, db_client):
    a = _story()
    newsroom_service.publish_story(a.id)
    assert db_client.get("/api/newsroom/home").get_json()["data"]["breaking"] == []


def test_existing_gti_news_kept_separate(db_app, db_client):
    from app.services import cms_service
    gti = cms_service.create_news_article({"title": "GTI graduation", "body": "Body"}, None)
    cms_service.publish_news_article(gti.id)
    ext = _story()
    newsroom_service.publish_story(ext.id)
    home = db_client.get("/api/newsroom/home").get_json()["data"]
    assert [g["title"] for g in home["gti_updates"]] == ["GTI graduation"]
    assert all(s["title"] != "GTI graduation" for s in home["latest"])


# ------------------------------------------------------------ events
def _event(**kw):
    data = dict(title="Expo", category="exhibition", organizer="Org", start_date=date.today().isoformat(),
                source_url="https://example.com/e", county="Nairobi")
    data.update(kw)
    e = newsroom_service.save_event(data)
    newsroom_service.set_event_publication(e.id, True)
    return e


def test_event_status_computed_from_dates(db_app):
    t = date(2026, 11, 22)
    e = NewsEvent(start_date=date(2026, 11, 19), end_date=date(2026, 11, 22))
    assert newsroom_service.event_status(e, t) == "ongoing"
    e = NewsEvent(start_date=date(2026, 11, 23), end_date=date(2026, 11, 26))
    assert newsroom_service.event_status(e, t) == "upcoming"
    e = NewsEvent(start_date=date(2026, 11, 1), end_date=None)
    assert newsroom_service.event_status(e, t) == "completed"
    e.status_override = "cancelled"
    assert newsroom_service.event_status(e, t) == "cancelled"


def test_event_validation(db_app):
    with pytest.raises(ValidationError) as ei:
        newsroom_service.save_event({"title": "X", "category": "nope", "start_date": "2026-11-30",
                                     "end_date": "2026-11-01", "status_override": "upcoming"})
    errs = ei.value.errors
    assert {"category", "organizer", "end_date", "status_override"} <= set(errs)


def test_event_publish_requires_source(db_app):
    e = newsroom_service.save_event(dict(title="No link", category="concert", organizer="O",
                                         start_date="2030-01-01"))
    with pytest.raises(ValidationError):
        newsroom_service.set_event_publication(e.id, True)


def test_events_api_hides_past_and_drafts(db_app, db_client):
    today = newsroom_service._today_eat()
    _event(title="Past", start_date=(today - timedelta(days=10)).isoformat())
    _event(title="Soon", start_date=(today + timedelta(days=3)).isoformat(), county="Mombasa")
    newsroom_service.save_event(dict(title="Draft", category="concert", organizer="O",
                                     start_date=(today + timedelta(days=3)).isoformat()))
    items = db_client.get("/api/newsroom/events").get_json()["data"]["items"]
    assert [i["title"] for i in items] == ["Soon"] and items[0]["status"] == "upcoming"
    assert db_client.get("/api/newsroom/events?county=mombasa").get_json()["data"]["items"][0]["title"] == "Soon"
    month = (today - timedelta(days=10)).strftime("%Y-%m")
    titles = [i["title"] for i in db_client.get(f"/api/newsroom/events?month={month}").get_json()["data"]["items"]]
    assert "Past" in titles
    assert db_client.get("/api/newsroom/events?month=bad").status_code == 422


def test_weekend_range():
    assert newsroom_service.weekend_range(date(2026, 11, 22)) == (date(2026, 11, 20), date(2026, 11, 22))
    assert newsroom_service.weekend_range(date(2026, 11, 23)) == (date(2026, 11, 27), date(2026, 11, 29))


# ------------------------------------------------------------ seed
def test_seed_is_idempotent_and_attributed(db_app, db_client):
    first = newsroom_seed.seed()
    assert first["stories"] == len(newsroom_seed.STORIES) and first["events"] == len(newsroom_seed.EVENTS)
    assert newsroom_seed.seed() == {"stories": 0, "events": 0}
    for m in NewsArticleMeta.query.all():
        assert m.source_name and m.source_url.startswith("https://") and m.is_breaking is False
        assert m.view_count == 0 and m.news_category != "politics"
    home = db_client.get("/api/newsroom/home").get_json()["data"]
    assert home["lead"]["title"].startswith("Turkana oil")
    assert len(home["top_stories"]) == 4 and home["watch"] == [] and home["breaking"] == []


# ------------------------------------------------------------ admin
def test_admin_requires_login(db_client):
    r = db_client.get("/admin/newsroom")
    assert r.status_code in (302, 401)


def test_admin_story_lifecycle(admin_client, db_app):
    page = admin_client.get("/admin/newsroom/stories/new")
    assert page.status_code == 200
    token = get_csrf_from(page)
    r = admin_client.post("/admin/newsroom/stories/new", data={
        "csrf_token": token, "title": "Admin story", "summary": "Mine.", "news_category": "technology",
        "is_external": "1", "source_name": "KBC", "source_url": "https://kbc.co.ke/x",
        "source_published_at": "2026-11-20T10:30", "is_trending": "1",
    })
    assert r.status_code == 302
    a = NewsArticle.query.filter_by(title="Admin story").one()
    assert a.meta.is_trending and a.meta.source_published_at is not None
    assert admin_client.get(f"/admin/newsroom/stories/{a.id}").status_code == 200
    admin_client.post(f"/admin/newsroom/stories/{a.id}/publish", data={"csrf_token": token})
    assert db.session.get(NewsArticle, a.id).status == "published"
    assert admin_client.get("/admin/newsroom").status_code == 200
    admin_client.post(f"/admin/newsroom/stories/{a.id}/remove", data={"csrf_token": token})
    assert db.session.get(NewsArticle, a.id).status == "archived"


def test_admin_csrf_enforced(admin_client):
    r = admin_client.post("/admin/newsroom/stories/new", data={"title": "x"})
    assert r.status_code == 403


def test_admin_event_lifecycle_with_upload(admin_client, db_app):
    token = get_csrf_from(admin_client.get("/admin/newsroom/events/new"))
    png = (b"\x89PNG\r\n\x1a\n" + b"\x00" * 64)
    r = admin_client.post("/admin/newsroom/events/new", content_type="multipart/form-data", data={
        "csrf_token": token, "title": "Career Fair", "category": "career", "organizer": "GTI",
        "start_date": "2030-03-01", "source_url": "https://example.com/fair", "county": "Nakuru",
        "image_file": (io.BytesIO(png), "fair.png", "image/png"),
    })
    assert r.status_code == 302
    e = NewsEvent.query.filter_by(title="Career Fair").one()
    try:
        assert e.image_id is not None
        admin_client.post(f"/admin/newsroom/events/{e.id}/publish", data={"csrf_token": token})
        assert db.session.get(NewsEvent, e.id).publication_status == "published"
        assert admin_client.get(f"/admin/newsroom/events/{e.id}").status_code == 200
        admin_client.post(f"/admin/newsroom/events/{e.id}/delete", data={"csrf_token": token})
        assert db.session.get(NewsEvent, e.id) is not None  # needs DELETE confirmation
        admin_client.post(f"/admin/newsroom/events/{e.id}/delete", data={"csrf_token": token, "confirm": "DELETE"})
        assert db.session.get(NewsEvent, e.id) is None
    finally:
        import os
        from app.models import MediaAsset
        for m in MediaAsset.query.all():
            path = os.path.join(db_app.static_folder, "media", m.filename)
            if os.path.exists(path):
                os.remove(path)
