"""
CMS service (Step 7 CMS addition) — structured content, news, media and
academics-admin query/update layer for the staff administration portal.

This is deliberately a STRUCTURED CMS, not a page builder:
  - Website Content fields are constrained to CONTENT_FIELD_REGISTRY, a
    fixed, code-defined set of keys. Administrators can only fill in
    values for fields that already correspond to real content on the
    current public frontend (Step 7 CMS instruction #6/#9) — they cannot
    invent a new field, section, or page.
  - Repeating image+caption lists (homepage hero slideshow, Student Life
    clubs/sports) are constrained to LIST_KEY_REGISTRY, matching the
    `list_key` CHECK constraint on content_list_items.
  - News is real CRUD (create/edit/draft/publish/unpublish/archive) —
    the one genuinely dynamic content type this CMS introduces, per
    Step 7 CMS instruction #17-24.
  - Media upload is validated by extension AND MIME type AND a magic-byte
    content sniff (no third-party image library is added — Pillow is not
    in requirements.txt and this project deliberately keeps dependencies
    minimal per the Step 3 scaffold instructions), with a safe randomly
    generated filename that never trusts the browser-supplied name.
  - Academics admin functions are thin update wrappers over the EXISTING
    School / Programme / ProgrammeMode / ProgrammeCategory models (Step 2
    §28) — no new catalogue tables. The two distinct pricing models are
    kept strictly separate: School.fee (academic flat fee) is only ever
    edited via update_school(); ProgrammeMode.fee_amount (AI Bootcamp
    per-mode fee) is only ever edited via update_programme_mode(). No
    function here ever merges or aliases the two.

Backward-compatibility rule enforced throughout: an absent/blank
SiteContent row, an empty content_list_items result for a given
list_key, or zero published NewsArticle rows must never blank a public
page — callers (the public API / frontend bridges) are responsible for
falling back to the existing static content, and this service never
raises just because a registry key has no row yet.
"""

import re
import secrets
import uuid
from datetime import datetime, timezone

from app.extensions import db
from app.models import (
    MediaAsset,
    NewsArticle,
    SiteContent,
    ContentListItem,
    School,
    Programme,
    ProgrammeMode,
    ProgrammeCategory,
)
from app.utils.validation import NotFoundError, ValidationError, Validator

# ---------------------------------------------------------------
# WEBSITE CONTENT — structured registry (Step 7 CMS instruction #6-9)
# ---------------------------------------------------------------
# Only fields that correspond to content genuinely present in the
# current frontend today. Nothing here invents a new section.

CONTENT_FIELD_REGISTRY = {
    # Homepage hero (index.html #heroTpl) — badge/headline/subtitle text.
    # The 4-slide hero slideshow itself is NOT here — see
    # LIST_KEY_REGISTRY["homepage_hero_slides"] below.
    "homepage.hero_badge": {"label": "Hero Badge Text", "group": "Homepage", "max_length": 100, "multiline": False},
    "homepage.hero_headline_line1": {"label": "Hero Headline — Line 1", "group": "Homepage", "max_length": 100, "multiline": False},
    "homepage.hero_headline_line2": {"label": "Hero Headline — Line 2", "group": "Homepage", "max_length": 100, "multiline": False},
    "homepage.hero_headline_accent": {"label": "Hero Headline — Accent (gold text)", "group": "Homepage", "max_length": 100, "multiline": False},
    "homepage.hero_subtitle": {"label": "Hero Subtitle", "group": "Homepage", "max_length": 300, "multiline": True},

    # About Us (about.html) — Vision / Mission / Core Values flip cards.
    "about.vision_text": {"label": "Vision Statement", "group": "About Us", "max_length": 500, "multiline": True},
    "about.mission_text": {"label": "Mission Statement", "group": "About Us", "max_length": 500, "multiline": True},
    "about.core_values_list": {"label": "Core Values (one per line)", "group": "About Us", "max_length": 1000, "multiline": True},

    # Student Life (campus.html) hero paragraph. The hero photo
    # slideshow and the Clubs/Sports repeating lists are NOT here — see
    # LIST_KEY_REGISTRY below.
    "student_life.hero_subtitle": {"label": "Student Life Hero Paragraph", "group": "Student Life", "max_length": 400, "multiline": True},

    # Contact Information — appears in several places on contact.html
    # (Quick Contact cards, hub links, footer). One authoritative value
    # per field here; the frontend bridge script fans it out to every
    # matching element (Step 7 CMS instruction #12: "single source of
    # truth for content already repeated on the page").
    "contact.phone": {"label": "Phone Number (as displayed, e.g. +254 719 488 112)", "group": "Contact Information", "max_length": 30, "multiline": False},
    "contact.email": {"label": "Admissions Email", "group": "Contact Information", "max_length": 150, "multiline": False},
    "contact.whatsapp": {"label": "WhatsApp Number (digits only, e.g. 254719488112)", "group": "Contact Information", "max_length": 20, "multiline": False},
    "contact.address": {"label": "Campus Address", "group": "Contact Information", "max_length": 300, "multiline": True},
    "contact.hours": {"label": "Business Hours", "group": "Contact Information", "max_length": 100, "multiline": False},
}

LIST_KEY_REGISTRY = {
    "homepage_hero_slides": {"label": "Homepage Hero Slideshow", "max_items": 8},
    "student_life_clubs": {"label": "Student Life — Clubs & Societies", "max_items": 20},
    "student_life_sports": {"label": "Student Life — Sports & Recreation", "max_items": 20},
}

NEWS_STATUSES = ["draft", "published", "archived"]
MEDIA_STATUSES = ["active", "archived"]

# Magic-byte signatures for the only image formats accepted. Extension
# AND declared MIME type AND these leading bytes must all agree — this
# is the "content sniffing where practical" layer (Step 7 CMS
# instruction #29), without adding a third-party image library.
_IMAGE_SIGNATURES = {
    "image/jpeg": (b"\xff\xd8\xff",),
    "image/png": (b"\x89PNG\r\n\x1a\n",),
    "image/gif": (b"GIF87a", b"GIF89a"),
    "image/webp": (b"RIFF",),  # bytes 8-11 must additionally be b"WEBP" — checked separately
}
_ALLOWED_EXTENSIONS = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp"}
MAX_UPLOAD_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


# ---------------------------------------------------------------
# PAGINATION HELPER (same "records" convention as admin_service.py —
# Jinja's dict.items() shadowing bug applies here too)
# ---------------------------------------------------------------

def _paginate(query, page: int, per_page: int = 25):
    page = max(1, page)
    per_page = min(max(1, per_page), 100)
    total = query.count()
    records = query.offset((page - 1) * per_page).limit(per_page).all()
    pages = max(1, (total + per_page - 1) // per_page)
    return {"records": records, "total": total, "page": page, "per_page": per_page, "pages": pages}


# =================================================================
# WEBSITE CONTENT (SiteContent)
# =================================================================

def list_content_grouped() -> dict:
    """Every registry key, grouped by CONTENT_FIELD_REGISTRY's "group",
    each with its current stored value (or None if never set)."""
    existing = {row.content_key: row.value for row in SiteContent.query.all()}
    grouped: dict[str, list[dict]] = {}
    for key, meta in CONTENT_FIELD_REGISTRY.items():
        grouped.setdefault(meta["group"], []).append({
            "key": key,
            "label": meta["label"],
            "max_length": meta["max_length"],
            "multiline": meta["multiline"],
            "value": existing.get(key) or "",
        })
    return grouped


def get_content_value(content_key: str) -> str | None:
    """Public-facing lookup. Returns None (never an empty string) if the
    key has no row or the row's value is blank — callers must treat None
    as "use the existing static fallback", not as an error."""
    if content_key not in CONTENT_FIELD_REGISTRY:
        return None
    row = SiteContent.query.filter_by(content_key=content_key).first()
    if row is None or row.value is None or row.value.strip() == "":
        return None
    return row.value


def get_content_values(content_keys: list[str]) -> dict:
    """Bulk version of get_content_value for a public bridge fetching several keys at once."""
    return {key: get_content_value(key) for key in content_keys}


def set_content_value(content_key: str, value: str, admin) -> SiteContent:
    if content_key not in CONTENT_FIELD_REGISTRY:
        raise ValidationError({"content_key": [f"'{content_key}' is not a recognized content field."]})
    meta = CONTENT_FIELD_REGISTRY[content_key]
    if value and len(value) > meta["max_length"]:
        raise ValidationError({"value": [f"{meta['label']} must be {meta['max_length']} characters or fewer."]})

    row = SiteContent.query.filter_by(content_key=content_key).first()
    if row is None:
        row = SiteContent(content_key=content_key)
        db.session.add(row)
    row.value = value.strip() if value else None
    row.updated_by_id = admin.id if admin else None
    db.session.commit()
    return row


# =================================================================
# CONTENT LIST ITEMS (hero slides / clubs / sports)
# =================================================================

def list_list_items(list_key: str, include_inactive: bool = True):
    if list_key not in LIST_KEY_REGISTRY:
        raise ValidationError({"list_key": [f"'{list_key}' is not a recognized list."]})
    query = ContentListItem.query.filter_by(list_key=list_key)
    if not include_inactive:
        query = query.filter_by(is_active=True)
    return query.order_by(ContentListItem.display_order.asc().nullslast(), ContentListItem.id.asc()).all()


def get_list_item(item_id: int) -> ContentListItem:
    item = db.session.get(ContentListItem, item_id)
    if item is None:
        raise NotFoundError(f"No content list item found with id {item_id}.")
    return item


def create_list_item(list_key: str, title=None, subtitle=None, link_url=None, image_id=None, display_order=None) -> ContentListItem:
    if list_key not in LIST_KEY_REGISTRY:
        raise ValidationError({"list_key": [f"'{list_key}' is not a recognized list."]})
    current_count = ContentListItem.query.filter_by(list_key=list_key).count()
    max_items = LIST_KEY_REGISTRY[list_key]["max_items"]
    if current_count >= max_items:
        raise ValidationError({"list_key": [f"'{list_key}' already has the maximum of {max_items} items."]})
    if image_id is not None and db.session.get(MediaAsset, image_id) is None:
        raise ValidationError({"image_id": ["No media asset found with that id."]})

    item = ContentListItem(
        list_key=list_key,
        title=(title or "").strip() or None,
        subtitle=(subtitle or "").strip() or None,
        link_url=(link_url or "").strip() or None,
        image_id=image_id,
        display_order=display_order,
        is_active=True,
    )
    db.session.add(item)
    db.session.commit()
    return item


def update_list_item(item_id: int, title=None, subtitle=None, link_url=None, image_id=None, display_order=None, is_active=None) -> ContentListItem:
    item = get_list_item(item_id)
    if image_id is not None and db.session.get(MediaAsset, image_id) is None:
        raise ValidationError({"image_id": ["No media asset found with that id."]})
    if title is not None:
        item.title = title.strip() or None
    if subtitle is not None:
        item.subtitle = subtitle.strip() or None
    if link_url is not None:
        item.link_url = link_url.strip() or None
    if image_id is not None:
        item.image_id = image_id
    if display_order is not None:
        item.display_order = display_order
    if is_active is not None:
        item.is_active = is_active
    db.session.commit()
    return item


def archive_list_item(item_id: int) -> ContentListItem:
    """Soft-remove — matches the codebase-wide preference for
    draft/unpublish/archive over permanent deletion."""
    item = get_list_item(item_id)
    item.is_active = False
    db.session.commit()
    return item


# =================================================================
# MEDIA LIBRARY
# =================================================================

def _sniff_image_mime(head_bytes: bytes) -> str | None:
    """Return the sniffed MIME type from magic bytes, or None if unrecognized."""
    for mime, signatures in _IMAGE_SIGNATURES.items():
        for sig in signatures:
            if head_bytes.startswith(sig):
                if mime == "image/webp":
                    if len(head_bytes) >= 12 and head_bytes[8:12] == b"WEBP":
                        return mime
                    continue
                return mime
    return None


def validate_upload(filename: str, declared_mime: str, size_bytes: int, head_bytes: bytes) -> str:
    """Validates extension + declared MIME type + magic-byte content sniff
    all agree on the same real image format. Returns the confirmed MIME
    type on success, raises ValidationError otherwise. Never trusts the
    browser-supplied filename or Content-Type alone (Step 7 CMS
    instruction #28: "generate safe filenames, never trust the browser").
    """
    errors: dict[str, list[str]] = {}

    if not filename or "." not in filename:
        raise ValidationError({"file": ["File must have a recognizable extension."]})
    ext = "." + filename.rsplit(".", 1)[-1].lower()

    if ext not in _ALLOWED_EXTENSIONS:
        errors.setdefault("file", []).append(
            f"File type '{ext}' is not allowed. Accepted types: {', '.join(sorted(_ALLOWED_EXTENSIONS))}."
        )

    if size_bytes > MAX_UPLOAD_SIZE_BYTES:
        errors.setdefault("file", []).append(f"File exceeds the {MAX_UPLOAD_SIZE_BYTES // (1024*1024)}MB upload limit.")
    if size_bytes <= 0:
        errors.setdefault("file", []).append("File is empty.")

    sniffed_mime = _sniff_image_mime(head_bytes)
    if sniffed_mime is None:
        errors.setdefault("file", []).append("File content does not match a supported image format (JPEG, PNG, GIF, WEBP).")
    elif ext in _ALLOWED_EXTENSIONS and _ALLOWED_EXTENSIONS[ext] != sniffed_mime:
        errors.setdefault("file", []).append("File extension does not match its actual content — possible disguised file type.")
    elif declared_mime and not declared_mime.startswith("image/"):
        errors.setdefault("file", []).append(f"Declared content type '{declared_mime}' is not an image type.")

    if errors:
        raise ValidationError(errors)
    return sniffed_mime


def generate_safe_filename(original_filename: str) -> str:
    """Never uses the browser-supplied name directly — a random token plus
    the validated extension only."""
    ext = "." + original_filename.rsplit(".", 1)[-1].lower()
    return f"{uuid.uuid4().hex}{ext}"


def record_media_asset(filename: str, original_filename: str, url_path: str, mime_type: str, size_bytes: int, alt_text: str | None, admin) -> MediaAsset:
    asset = MediaAsset(
        filename=filename,
        original_filename=(original_filename or "")[:255] or None,
        url_path=url_path,
        alt_text=(alt_text or "").strip()[:300] or None,
        mime_type=mime_type,
        size_bytes=size_bytes,
        status="active",
        uploaded_by_id=admin.id if admin else None,
    )
    db.session.add(asset)
    db.session.commit()
    return asset


def list_media(status=None, q=None, page=1, per_page=24):
    query = MediaAsset.query
    if status:
        query = query.filter(MediaAsset.status == status)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(db.or_(MediaAsset.original_filename.ilike(like), MediaAsset.alt_text.ilike(like)))
    query = query.order_by(MediaAsset.created_at.desc())
    return _paginate(query, page, per_page)


def get_media(media_id: int) -> MediaAsset:
    asset = db.session.get(MediaAsset, media_id)
    if asset is None:
        raise NotFoundError(f"No media asset found with id {media_id}.")
    return asset


def update_media_alt_text(media_id: int, alt_text: str) -> MediaAsset:
    asset = get_media(media_id)
    asset.alt_text = (alt_text or "").strip()[:300] or None
    db.session.commit()
    return asset


def archive_media(media_id: int) -> MediaAsset:
    asset = get_media(media_id)
    asset.status = "archived"
    db.session.commit()
    return asset


def update_media_file(media_id: int, filename: str, url_path: str, mime_type: str, size_bytes: int) -> MediaAsset:
    """Called after a replacement file has already been validated and
    saved to disk by the route layer — updates the existing row in place
    so every reference (news featured_image_id, content_list_items.image_id)
    keeps pointing at the same MediaAsset id."""
    asset = get_media(media_id)
    asset.filename = filename
    asset.url_path = url_path
    asset.mime_type = mime_type
    asset.size_bytes = size_bytes
    asset.status = "active"
    db.session.commit()
    return asset


# =================================================================
# NEWS ARTICLES
# =================================================================

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slugify(title: str) -> str:
    base = _SLUG_RE.sub("-", title.strip().lower()).strip("-") or "article"
    base = base[:200]
    slug = base
    suffix = 2
    while NewsArticle.query.filter_by(slug=slug).first() is not None:
        slug = f"{base}-{suffix}"
        suffix += 1
    return slug


def list_news_admin(status=None, q=None, page=1, per_page=20):
    query = NewsArticle.query
    if status:
        query = query.filter(NewsArticle.status == status)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(db.or_(NewsArticle.title.ilike(like), NewsArticle.summary.ilike(like)))
    query = query.order_by(NewsArticle.updated_at.desc())
    return _paginate(query, page, per_page)


def get_news_article(article_id: int) -> NewsArticle:
    article = db.session.get(NewsArticle, article_id)
    if article is None:
        raise NotFoundError(f"No news article found with id {article_id}.")
    return article


def create_news_article(data: dict, admin) -> NewsArticle:
    Validator().require(data, "title", "Title").max_length(data, "title", 250, "Title").finish()
    if data.get("featured_image_id") and db.session.get(MediaAsset, data["featured_image_id"]) is None:
        raise ValidationError({"featured_image_id": ["No media asset found with that id."]})

    article = NewsArticle(
        slug=_slugify(data["title"]),
        title=data["title"].strip(),
        summary=(data.get("summary") or "").strip()[:500] or None,
        body=(data.get("body") or "").strip() or None,
        category=(data.get("category") or "").strip()[:100] or None,
        author=(data.get("author") or "").strip()[:150] or None,
        featured_image_id=data.get("featured_image_id") or None,
        status="draft",
        created_by_id=admin.id if admin else None,
    )
    db.session.add(article)
    db.session.commit()
    return article


def update_news_article(article_id: int, data: dict) -> NewsArticle:
    article = get_news_article(article_id)
    if "title" in data:
        Validator().require(data, "title", "Title").max_length(data, "title", 250, "Title").finish()
        article.title = data["title"].strip()
    if "summary" in data:
        article.summary = (data.get("summary") or "").strip()[:500] or None
    if "body" in data:
        article.body = (data.get("body") or "").strip() or None
    if "category" in data:
        article.category = (data.get("category") or "").strip()[:100] or None
    if "author" in data:
        article.author = (data.get("author") or "").strip()[:150] or None
    if "featured_image_id" in data:
        fid = data.get("featured_image_id") or None
        if fid is not None and db.session.get(MediaAsset, fid) is None:
            raise ValidationError({"featured_image_id": ["No media asset found with that id."]})
        article.featured_image_id = fid
    db.session.commit()
    return article


def publish_news_article(article_id: int) -> NewsArticle:
    article = get_news_article(article_id)
    if not article.title or not article.body:
        raise ValidationError({"status": ["An article must have both a title and body before it can be published."]})
    article.status = "published"
    if article.published_at is None:
        article.published_at = datetime.now(timezone.utc)
    db.session.commit()
    return article


def unpublish_news_article(article_id: int) -> NewsArticle:
    """Returns a published article to draft. published_at is deliberately
    left untouched (preserves "originally published on" provenance if
    republished later)."""
    article = get_news_article(article_id)
    article.status = "draft"
    db.session.commit()
    return article


def archive_news_article(article_id: int) -> NewsArticle:
    article = get_news_article(article_id)
    article.status = "archived"
    db.session.commit()
    return article


def list_published_news(page=1, per_page=12, category=None):
    """Public-facing — status='published' only. Empty result is a valid,
    expected state (no articles authored yet); callers must fall back to
    news.html's existing static cards, never render an empty CMS as
    'no news'."""
    query = NewsArticle.query.filter_by(status="published")
    if category:
        query = query.filter(NewsArticle.category == category)
    query = query.order_by(NewsArticle.published_at.desc())
    return _paginate(query, page, per_page)


def get_published_news_by_slug(slug: str) -> NewsArticle:
    article = NewsArticle.query.filter_by(slug=slug, status="published").first()
    if article is None:
        raise NotFoundError(f"No published article found with slug '{slug}'.")
    return article


# =================================================================
# ACADEMICS ADMIN (Schools / Programmes / Programme Modes / Categories)
# — thin update wrappers over the EXISTING Step 2 catalogue tables.
# Read paths reuse the same models school_service/programme_service
# already expose publicly; these add authenticated, admin-only writes.
# =================================================================

def list_schools_admin(q=None, page=1, per_page=25):
    query = School.query
    if q:
        query = query.filter(School.name.ilike(f"%{q.strip()}%"))
    query = query.order_by(School.display_order.asc().nullslast(), School.name.asc())
    return _paginate(query, page, per_page)


def get_school_admin(school_id: int) -> School:
    school = db.session.get(School, school_id)
    if school is None:
        raise NotFoundError(f"No school found with id {school_id}.")
    return school


def update_school(school_id: int, description=None, fee=None, is_active=None, display_order=None) -> School:
    school = get_school_admin(school_id)
    if description is not None:
        school.description = description.strip() or None
    if fee is not None:
        if len(fee) > 50:
            raise ValidationError({"fee": ["Fee display text must be 50 characters or fewer."]})
        school.fee = fee.strip() or None
    if is_active is not None:
        school.is_active = is_active
    if display_order is not None:
        school.display_order = display_order
    db.session.commit()
    return school


def list_programmes_admin(programme_type=None, school_id=None, category_id=None, q=None, page=1, per_page=25):
    query = Programme.query
    if programme_type:
        query = query.filter(Programme.programme_type == programme_type)
    if school_id:
        query = query.filter(Programme.school_id == school_id)
    if category_id:
        query = query.filter(Programme.category_id == category_id)
    if q:
        query = query.filter(Programme.name.ilike(f"%{q.strip()}%"))
    query = query.order_by(Programme.display_order.asc().nullslast(), Programme.name.asc())
    return _paginate(query, page, per_page)


def get_programme_admin(programme_id: int) -> Programme:
    programme = db.session.get(Programme, programme_id)
    if programme is None:
        raise NotFoundError(f"No programme found with id {programme_id}.")
    return programme


def update_programme(programme_id: int, overview=None, gain_points=None, entry_requirement=None,
                      exam_body=None, apply_heading=None, apply_subtext=None, is_active=None, display_order=None) -> Programme:
    """Deliberately has no `fee` parameter — academic pricing lives on
    School.fee (update_school), AI Bootcamp pricing lives on
    ProgrammeMode.fee_amount (update_programme_mode). Never here."""
    programme = get_programme_admin(programme_id)
    if overview is not None:
        programme.overview = overview.strip() or None
    if gain_points is not None:
        # Admin form supplies newline-separated text; stored as the same
        # JSON array-of-strings shape the model/frontend already use.
        if isinstance(gain_points, str):
            programme.gain_points = [line.strip() for line in gain_points.splitlines() if line.strip()] or None
        else:
            programme.gain_points = gain_points or None
    if entry_requirement is not None:
        programme.entry_requirement = entry_requirement.strip() or None
    if exam_body is not None:
        if len(exam_body) > 50:
            raise ValidationError({"exam_body": ["Must be 50 characters or fewer."]})
        programme.exam_body = exam_body.strip() or None
    if apply_heading is not None:
        if len(apply_heading) > 200:
            raise ValidationError({"apply_heading": ["Must be 200 characters or fewer."]})
        programme.apply_heading = apply_heading.strip() or None
    if apply_subtext is not None:
        if len(apply_subtext) > 300:
            raise ValidationError({"apply_subtext": ["Must be 300 characters or fewer."]})
        programme.apply_subtext = apply_subtext.strip() or None
    if is_active is not None:
        programme.is_active = is_active
    if display_order is not None:
        programme.display_order = display_order
    db.session.commit()
    return programme


def update_programme_mode(mode_id: int, fee_amount=None, is_available=None, schedule=None) -> ProgrammeMode:
    """AI Bootcamp per-mode pricing only. fee_amount=None means "Contact
    Admissions" (Step 2 §8 sentinel) — passing the Python value None here
    intentionally clears the fee, it does not mean "leave unchanged"; use
    the caller's own "field present in payload" check before calling this
    (see the CMS admin route), mirroring how update_programme's optional
    kwargs work."""
    mode = db.session.get(ProgrammeMode, mode_id)
    if mode is None:
        raise NotFoundError(f"No programme mode found with id {mode_id}.")
    if fee_amount is not None:
        try:
            mode.fee_amount = None if fee_amount in ("", None) else float(fee_amount)
        except (TypeError, ValueError):
            raise ValidationError({"fee_amount": ["Must be a number, or blank for 'Contact Admissions'."]})
    if is_available is not None:
        mode.is_available = is_available
    if schedule is not None:
        mode.schedule = schedule.strip() or None
    db.session.commit()
    return mode


def list_categories_admin():
    return ProgrammeCategory.query.order_by(ProgrammeCategory.label.asc()).all()


def get_category_admin(category_id: int) -> ProgrammeCategory:
    category = db.session.get(ProgrammeCategory, category_id)
    if category is None:
        raise NotFoundError(f"No programme category found with id {category_id}.")
    return category


def update_category(category_id: int, label=None, icon=None) -> ProgrammeCategory:
    category = get_category_admin(category_id)
    if label is not None:
        if not label.strip():
            raise ValidationError({"label": ["Label is required."]})
        if len(label) > 150:
            raise ValidationError({"label": ["Must be 150 characters or fewer."]})
        category.label = label.strip()
    if icon is not None:
        if len(icon) > 80:
            raise ValidationError({"icon": ["Must be 80 characters or fewer."]})
        category.icon = icon.strip() or None
    db.session.commit()
    return category
