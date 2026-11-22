"""
Public News & Events API (read-only, published content only).

  GET  /api/newsroom/home                 one call for the News & Events page
  GET  /api/newsroom/stories              ?category=&q=&page=&per_page=
  GET  /api/newsroom/stories/<slug>       detail + related stories
  POST /api/newsroom/stories/<slug>/view  real read counter (throttled)
  GET  /api/newsroom/events               ?category=&county=&q=&month=YYYY-MM&date=&status=
  GET  /api/newsroom/events/<slug>
  GET  /api/newsroom/search?q=            stories + events

The client IP is used only as an in-memory throttling key; it is never
stored.
"""

from flask import request

from app.blueprints.public import public_bp
from app.services import newsroom_service
from app.utils.rate_limit import SlidingWindowLimiter
from app.utils.responses import error, success

_view_limiter = SlidingWindowLimiter(max_events=60, window_seconds=60)


def _client_key():
    fwd = request.headers.get("X-Forwarded-For", "")
    return (fwd.split(",")[0].strip() if fwd else request.remote_addr) or "anon"


def _cached(resp, seconds=60):
    resp[0].headers["Cache-Control"] = f"public, max-age={seconds}"
    return resp


@public_bp.route("/api/newsroom/home", methods=["GET"])
def newsroom_home():
    return _cached(success(newsroom_service.homepage()))


@public_bp.route("/api/newsroom/stories", methods=["GET"])
def newsroom_stories():
    return _cached(success(newsroom_service.list_stories(
        category=request.args.get("category") or None,
        q=request.args.get("q") or None,
        page=request.args.get("page", default=1, type=int),
        per_page=request.args.get("per_page", default=12, type=int),
    )))


@public_bp.route("/api/newsroom/stories/<slug>", methods=["GET"])
def newsroom_story(slug):
    return _cached(success(newsroom_service.get_story(slug)))


@public_bp.route("/api/newsroom/stories/<slug>/view", methods=["POST"])
def newsroom_story_view(slug):
    key = _client_key()
    if not _view_limiter.hit(key):
        return error("Too many requests.", status=429)
    counted = newsroom_service.record_view(slug, key)
    return success({"counted": counted})


@public_bp.route("/api/newsroom/events", methods=["GET"])
def newsroom_events():
    return _cached(success({"items": newsroom_service.list_events(
        category=request.args.get("category") or None,
        county=request.args.get("county") or None,
        q=request.args.get("q") or None,
        month=request.args.get("month") or None,
        status=request.args.get("status") or None,
        on_date=request.args.get("date") or None,
        include_completed=request.args.get("include_completed") == "1",
    )}))


@public_bp.route("/api/newsroom/events/<slug>", methods=["GET"])
def newsroom_event(slug):
    return _cached(success(newsroom_service.get_event(slug)))


@public_bp.route("/api/newsroom/search", methods=["GET"])
def newsroom_search():
    q = (request.args.get("q") or "").strip()
    if len(q) < 2:
        return success({"stories": [], "events": []})
    return success({
        "stories": newsroom_service.list_stories(q=q, per_page=10)["items"],
        "events": newsroom_service.list_events(q=q, include_completed=True)[:10],
    })
