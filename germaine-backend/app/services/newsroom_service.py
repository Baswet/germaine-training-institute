"""
Newsroom service — the News & Events publication.

Builds on the EXISTING Step 7 CMS: stories are ordinary NewsArticle rows
(created/published through cms_service so all existing rules apply), plus
a 1:1 NewsArticleMeta row for newsroom fields. Events are NewsEvent rows.

Editorial integrity rules enforced here:
  * External stories must name the original publisher and link the
    original article before they can be published.
  * Events must name an organizer and an official source URL.
  * Only published rows are ever public.
  * Event status (upcoming / ongoing / completed) is computed from dates
    in Nairobi time; it cannot be set by hand, so a past event can never be
    shown as upcoming. Editors can only add 'cancelled' / 'postponed'.
  * Featured / trending / breaking / editor's-pick are editorial flags.
    Nothing is labelled breaking unless an editor set it.
  * Most Read uses real counts from /view hits; it is empty until readers
    actually read stories (no invented popularity).
"""

import re
import threading
import time
from datetime import date, datetime, timedelta, timezone
from urllib.parse import urlparse

from app.extensions import db
from app.models import MediaAsset, NewsArticle
from app.models.newsroom import (
    EVENT_CATEGORY_KEYS,
    EVENT_CATEGORY_LABELS,
    NEWS_CATEGORY_KEYS,
    NEWS_CATEGORY_LABELS,
    NewsArticleMeta,
    NewsEvent,
)
from app.services import cms_service
from app.utils.validation import NotFoundError, ValidationError

EAT = timezone(timedelta(hours=3))
_SLUG_RE = re.compile(r"[^a-z0-9]+")
YOUTUBE_RE = re.compile(r"^https://(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{6,20})")


def _today_eat() -> date:
    return datetime.now(EAT).date()


def _clean(value, max_len=None):
    if value is None:
        return None
    value = str(value).strip()
    if not value:
        return None
    return value[:max_len] if max_len else value


def _valid_url(url) -> bool:
    if not url:
        return False
    try:
        p = urlparse(url)
    except ValueError:
        return False
    return p.scheme in ("http", "https") and bool(p.netloc)


def _parse_dt(value):
    """'YYYY-MM-DDTHH:MM' (datetime-local, Nairobi) or 'YYYY-MM-DD' -> aware UTC."""
    if not value:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(value).strip(), fmt).replace(tzinfo=EAT).astimezone(timezone.utc)
        except ValueError:
            continue
    raise ValidationError({"date": [f"Invalid date/time: {value}"]})


def _parse_date(value):
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError({"date": [f"Invalid date: {value}"]})


def _aware(dt):
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def youtube_id(url):
    m = YOUTUBE_RE.match(url or "")
    return m.group(3) if m else None


# =================================================================
# STORIES
# =================================================================

def get_or_create_meta(article: NewsArticle) -> NewsArticleMeta:
    if article.meta is None:
        meta = NewsArticleMeta(article_id=article.id, is_external=False)
        db.session.add(meta)
        db.session.flush()
        db.session.refresh(article)
    return article.meta


def save_story(data: dict, admin=None, article_id=None) -> NewsArticle:
    """Create or update a newsroom story (NewsArticle + meta)."""
    category = data.get("news_category") or None
    if category and category not in NEWS_CATEGORY_KEYS:
        raise ValidationError({"news_category": ["Choose one of the newsroom categories."]})
    source_url = _clean(data.get("source_url"), 600)
    if source_url and not _valid_url(source_url):
        raise ValidationError({"source_url": ["Original article link must be a full http(s) URL."]})
    video_url = _clean(data.get("video_url"), 600)
    if video_url and not youtube_id(video_url):
        raise ValidationError({"video_url": ["Video must be a YouTube link from the publisher's official channel."]})

    core = {k: data.get(k) for k in ("title", "summary", "body", "author", "featured_image_id") if k in data}
    if category:
        core["category"] = NEWS_CATEGORY_LABELS[category]
    # The CMS requires a body to publish; for a short external item the
    # original summary is the body.
    if "body" in core or "summary" in core:
        if not (core.get("body") or "").strip():
            core["body"] = core.get("summary") or ""
    if article_id is None:
        article = cms_service.create_news_article(core, admin)
    else:
        article = cms_service.update_news_article(article_id, core)

    meta = get_or_create_meta(article)
    is_external = str(data.get("is_external", "1")).lower() in ("1", "true", "yes", "on")
    meta.is_external = is_external
    meta.news_category = category
    meta.source_name = _clean(data.get("source_name"), 150)
    meta.source_url = source_url
    if "source_published_at" in data:
        meta.source_published_at = _parse_dt(data.get("source_published_at"))
    meta.image_credit = _clean(data.get("image_credit"), 200)
    meta.video_url = video_url
    meta.video_duration = _clean(data.get("video_duration"), 20)
    for flag in ("is_featured", "is_trending", "is_breaking", "is_editors_pick"):
        if flag in data:
            setattr(meta, flag, str(data.get(flag)).lower() in ("1", "true", "yes", "on"))
    if "feature_rank" in data:
        try:
            meta.feature_rank = int(data.get("feature_rank") or 0)
        except ValueError:
            meta.feature_rank = 0
    meta.trending_note = _clean(data.get("trending_note"), 200)
    db.session.commit()
    return article


def publish_story(article_id: int) -> NewsArticle:
    article = cms_service.get_news_article(article_id)
    meta = article.meta
    if meta is not None and meta.is_external:
        missing = {}
        if not meta.source_name:
            missing["source_name"] = ["External stories must name the original publisher."]
        if not _valid_url(meta.source_url):
            missing["source_url"] = ["External stories must link the original article."]
        if not meta.news_category:
            missing["news_category"] = ["Choose a newsroom category."]
        if missing:
            raise ValidationError(missing)
    return cms_service.publish_news_article(article_id)


def _published_external():
    return (
        db.session.query(NewsArticle, NewsArticleMeta)
        .join(NewsArticleMeta, NewsArticleMeta.article_id == NewsArticle.id)
        .filter(NewsArticle.status == "published", NewsArticleMeta.is_external.is_(True))
    )


def _story_time(article, meta):
    return _aware((meta.source_published_at if meta else None) or article.published_at)


def story_to_dict(article, meta, detailed=False):
    ts = _story_time(article, meta)
    data = {
        "slug": article.slug,
        "title": article.title,
        "summary": article.summary,
        "category": meta.news_category if meta else None,
        "category_label": NEWS_CATEGORY_LABELS.get(meta.news_category) if meta else (article.category or "GTI News"),
        "is_external": bool(meta and meta.is_external),
        "source_name": meta.source_name if meta else "Germaine Training Institute",
        "source_url": meta.source_url if meta else None,
        "published_at": ts.isoformat() if ts else None,
        "updated_at": _aware(article.updated_at).isoformat() if article.updated_at else None,
        "image_url": article.featured_image.url_path if article.featured_image else None,
        "image_credit": meta.image_credit if meta else None,
        "is_trending": bool(meta and meta.is_trending),
        "is_breaking": bool(meta and meta.is_breaking),
        "trending_note": meta.trending_note if meta else None,
        "video_id": youtube_id(meta.video_url) if meta else None,
        "video_duration": meta.video_duration if meta else None,
    }
    if detailed:
        data["body"] = article.body
        data["author"] = article.author
    return data


def list_stories(category=None, q=None, page=1, per_page=12):
    query = _published_external()
    if category:
        if category not in NEWS_CATEGORY_KEYS:
            raise ValidationError({"category": ["Unknown category."]})
        query = query.filter(NewsArticleMeta.news_category == category)
    if q:
        like = f"%{q.strip()[:100]}%"
        query = query.filter(db.or_(NewsArticle.title.ilike(like), NewsArticle.summary.ilike(like),
                                    NewsArticleMeta.source_name.ilike(like)))
    order_col = db.func.coalesce(NewsArticleMeta.source_published_at, NewsArticle.published_at)
    query = query.order_by(order_col.desc(), NewsArticle.id.desc())
    page = max(1, int(page or 1))
    per_page = min(max(1, int(per_page or 12)), 48)
    total = query.count()
    rows = query.offset((page - 1) * per_page).limit(per_page).all()
    return {"items": [story_to_dict(a, m) for a, m in rows], "total": total, "page": page,
            "per_page": per_page, "has_more": page * per_page < total}


def get_story(slug):
    row = (
        db.session.query(NewsArticle, NewsArticleMeta)
        .outerjoin(NewsArticleMeta, NewsArticleMeta.article_id == NewsArticle.id)
        .filter(NewsArticle.slug == slug, NewsArticle.status == "published")
        .first()
    )
    if row is None:
        raise NotFoundError("Story not found.")
    article, meta = row
    data = story_to_dict(article, meta, detailed=True)
    related_q = _published_external().filter(NewsArticle.id != article.id)
    if meta and meta.news_category:
        related_q = related_q.filter(NewsArticleMeta.news_category == meta.news_category)
    related = related_q.order_by(NewsArticle.published_at.desc()).limit(4).all()
    if len(related) < 3:
        more = (_published_external().filter(NewsArticle.id != article.id,
                                             ~NewsArticle.id.in_([a.id for a, _ in related] or [0]))
                .order_by(NewsArticle.published_at.desc()).limit(4 - len(related)).all())
        related += more
    data["related"] = [story_to_dict(a, m) for a, m in related]
    return data


# --- real read counter (throttled so reloads/bots don't inflate it) ---
_view_lock = threading.Lock()
_recent_views: dict = {}
VIEW_WINDOW_SECONDS = 6 * 3600


def record_view(slug, client_key) -> bool:
    article = NewsArticle.query.filter_by(slug=slug, status="published").first()
    if article is None:
        raise NotFoundError("Story not found.")
    key = (client_key or "anon", article.id)
    now = time.monotonic()
    with _view_lock:
        if len(_recent_views) > 50000:
            for k in [k for k, t in _recent_views.items() if now - t > VIEW_WINDOW_SECONDS]:
                del _recent_views[k]
        last = _recent_views.get(key)
        if last is not None and now - last < VIEW_WINDOW_SECONDS:
            return False
        _recent_views[key] = now
    meta = get_or_create_meta(article)
    NewsArticleMeta.query.filter_by(id=meta.id).update(
        {NewsArticleMeta.view_count: NewsArticleMeta.view_count + 1}, synchronize_session=False)
    db.session.commit()
    return True


def reset_view_throttle():
    with _view_lock:
        _recent_views.clear()


# =================================================================
# EVENTS
# =================================================================

def event_status(event, today=None) -> str:
    if event.status_override:
        return event.status_override
    today = today or _today_eat()
    end = event.end_date or event.start_date
    if today < event.start_date:
        return "upcoming"
    if today > end:
        return "completed"
    return "ongoing"


def event_to_dict(event, today=None):
    today = today or _today_eat()
    return {
        "slug": event.slug,
        "title": event.title,
        "category": event.category,
        "category_label": EVENT_CATEGORY_LABELS.get(event.category, event.category),
        "description": event.description,
        "image_url": event.image.url_path if event.image else None,
        "organizer": event.organizer,
        "start_date": event.start_date.isoformat(),
        "end_date": (event.end_date or event.start_date).isoformat(),
        "start_time": event.start_time,
        "date_note": event.date_note,
        "venue": event.venue,
        "county": event.county,
        "registration_url": event.registration_url,
        "source_url": event.source_url,
        "status": event_status(event, today),
        "is_featured": bool(event.is_featured),
    }


def _slugify_event(title, exclude_id=None):
    base = _SLUG_RE.sub("-", title.strip().lower()).strip("-")[:200] or "event"
    slug, n = base, 2
    while True:
        q = NewsEvent.query.filter_by(slug=slug)
        if exclude_id:
            q = q.filter(NewsEvent.id != exclude_id)
        if q.first() is None:
            return slug
        slug, n = f"{base}-{n}", n + 1


def save_event(data: dict, event_id=None) -> NewsEvent:
    errors = {}
    title = _clean(data.get("title"), 250)
    if not title:
        errors["title"] = ["Title is required."]
    category = data.get("category")
    if category not in EVENT_CATEGORY_KEYS:
        errors["category"] = ["Choose an event category."]
    organizer = _clean(data.get("organizer"), 200)
    if not organizer:
        errors["organizer"] = ["Every event must name its organizer."]
    try:
        start = _parse_date(data.get("start_date"))
        end = _parse_date(data.get("end_date"))
    except ValidationError as err:
        errors.update(err.errors)
        start = end = None
    if not start:
        errors.setdefault("start_date", ["Start date is required."])
    if start and end and end < start:
        errors["end_date"] = ["End date cannot be before the start date."]
    for f in ("registration_url", "source_url"):
        v = _clean(data.get(f), 600)
        if v and not _valid_url(v):
            errors[f] = ["Must be a full http(s) URL."]
    override = data.get("status_override") or None
    if override not in (None, "cancelled", "postponed"):
        errors["status_override"] = ["Only 'cancelled' or 'postponed' can be set by hand."]
    image_id = data.get("image_id") or None
    if image_id and db.session.get(MediaAsset, int(image_id)) is None:
        errors["image_id"] = ["No media asset with that id."]
    if errors:
        raise ValidationError(errors)

    event = db.session.get(NewsEvent, event_id) if event_id else None
    if event_id and event is None:
        raise NotFoundError("Event not found.")
    if event is None:
        event = NewsEvent(slug=_slugify_event(title), publication_status="draft")
        db.session.add(event)
    event.title = title
    event.category = category
    event.description = _clean(data.get("description"))
    event.organizer = organizer
    event.start_date = start
    event.end_date = end
    event.start_time = _clean(data.get("start_time"), 40)
    event.date_note = _clean(data.get("date_note"), 250)
    event.venue = _clean(data.get("venue"), 250)
    event.county = _clean(data.get("county"), 60)
    event.registration_url = _clean(data.get("registration_url"), 600)
    event.source_url = _clean(data.get("source_url"), 600)
    event.status_override = override
    event.image_id = int(image_id) if image_id else None
    if "is_featured" in data:
        event.is_featured = str(data.get("is_featured")).lower() in ("1", "true", "yes", "on")
    db.session.commit()
    return event


def set_event_publication(event_id, published: bool) -> NewsEvent:
    event = db.session.get(NewsEvent, event_id)
    if event is None:
        raise NotFoundError("Event not found.")
    if published and not _valid_url(event.source_url):
        raise ValidationError({"source_url": ["Add the official event page before publishing."]})
    event.publication_status = "published" if published else "draft"
    db.session.commit()
    return event


def delete_event(event_id) -> bool:
    event = db.session.get(NewsEvent, event_id)
    if event is None:
        return False
    db.session.delete(event)
    db.session.commit()
    return True


def list_events(category=None, county=None, q=None, month=None, status=None, on_date=None,
                include_completed=False):
    today = _today_eat()
    query = NewsEvent.query.filter(NewsEvent.publication_status == "published")
    if category:
        query = query.filter(NewsEvent.category == category)
    if county:
        query = query.filter(db.func.lower(NewsEvent.county) == county.strip().lower())
    if q:
        like = f"%{q.strip()[:100]}%"
        query = query.filter(db.or_(NewsEvent.title.ilike(like), NewsEvent.description.ilike(like),
                                    NewsEvent.venue.ilike(like), NewsEvent.organizer.ilike(like)))
    end_expr = db.func.coalesce(NewsEvent.end_date, NewsEvent.start_date)
    if month:
        try:
            y, m = (int(x) for x in month.split("-"))
            first = date(y, m, 1)
            nxt = date(y + (m == 12), (m % 12) + 1, 1)
        except (ValueError, TypeError):
            raise ValidationError({"month": ["Use YYYY-MM."]})
        query = query.filter(NewsEvent.start_date < nxt, end_expr >= first)
    if on_date:
        d = _parse_date(on_date)
        query = query.filter(NewsEvent.start_date <= d, end_expr >= d)
    if not include_completed and not month and not on_date:
        query = query.filter(end_expr >= today)
    events = query.order_by(NewsEvent.start_date.asc(), NewsEvent.id.asc()).all()
    out = [event_to_dict(e, today) for e in events]
    if status:
        out = [e for e in out if e["status"] == status]
    return out


def get_event(slug):
    event = NewsEvent.query.filter_by(slug=slug, publication_status="published").first()
    if event is None:
        raise NotFoundError("Event not found.")
    return event_to_dict(event)


def weekend_range(today=None):
    """The coming (or current) Friday–Sunday in Nairobi time."""
    today = today or _today_eat()
    wd = today.weekday()  # Mon=0 … Sun=6
    if wd >= 4:
        friday = today - timedelta(days=wd - 4)
    else:
        friday = today + timedelta(days=4 - wd)
    return friday, friday + timedelta(days=2)


# =================================================================
# HOMEPAGE AGGREGATE
# =================================================================

def homepage():
    today = _today_eat()
    rows = (_published_external()
            .order_by(db.func.coalesce(NewsArticleMeta.source_published_at, NewsArticle.published_at).desc())
            .limit(80).all())
    stories = [(a, m) for a, m in rows]
    d = lambda pair: story_to_dict(*pair)  # noqa: E731

    featured_pairs = sorted([p for p in stories if p[1].is_featured],
                            key=lambda p: (-p[1].feature_rank, -(_story_time(*p).timestamp() if _story_time(*p) else 0)))
    lead = featured_pairs[0] if featured_pairs else (stories[0] if stories else None)
    used = {lead[0].id} if lead else set()
    support = [p for p in featured_pairs[1:]]
    support += [p for p in stories if p[0].id not in used and p not in support]
    support = [p for p in support if p[0].id not in used][:4]
    used |= {p[0].id for p in support}

    most_read = sorted([p for p in stories if (p[1].view_count or 0) > 0],
                       key=lambda p: -p[1].view_count)[:5]

    gti_rows = (db.session.query(NewsArticle)
                .outerjoin(NewsArticleMeta, NewsArticleMeta.article_id == NewsArticle.id)
                .filter(NewsArticle.status == "published",
                        db.or_(NewsArticleMeta.id.is_(None), NewsArticleMeta.is_external.is_(False)))
                .order_by(NewsArticle.published_at.desc()).limit(4).all())

    events = list_events()
    fri, sun = weekend_range(today)
    weekend = [e for e in events if e["start_date"] <= sun.isoformat() and e["end_date"] >= fri.isoformat()]
    featured_event = next((e for e in events if e["is_featured"] and e["status"] != "completed"), None) \
        or (events[0] if events else None)
    counties = sorted({e["county"] for e in events if e["county"]})

    counts = dict(db.session.query(NewsArticleMeta.news_category, db.func.count(NewsArticleMeta.id))
                  .join(NewsArticle, NewsArticle.id == NewsArticleMeta.article_id)
                  .filter(NewsArticle.status == "published", NewsArticleMeta.is_external.is_(True))
                  .group_by(NewsArticleMeta.news_category).all())

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "categories": [{"key": k, "label": NEWS_CATEGORY_LABELS[k], "count": counts.get(k, 0)}
                       for k in NEWS_CATEGORY_KEYS],
        "event_categories": [{"key": k, "label": v} for k, v in EVENT_CATEGORY_LABELS.items()],
        "breaking": [d(p) for p in stories if p[1].is_breaking][:3],
        "trending": [d(p) for p in stories if p[1].is_trending][:8],
        "lead": d(lead) if lead else None,
        "top_stories": [d(p) for p in support],
        "latest": [d(p) for p in stories[:12]],
        "latest_total": len(stories),
        "daily_brief": [d(p) for p in stories[:5]],
        "most_read": [dict(d(p), views=p[1].view_count) for p in most_read],
        "editors_picks": [d(p) for p in stories if p[1].is_editors_pick][:5],
        "watch": [d(p) for p in stories if youtube_id(p[1].video_url)][:4],
        "gti_updates": [story_to_dict(a, None) for a in gti_rows],
        "events": {
            "featured": featured_event,
            "upcoming": events[:12],
            "weekend": weekend,
            "weekend_range": [fri.isoformat(), sun.isoformat()],
            "counties": counties,
        },
    }
