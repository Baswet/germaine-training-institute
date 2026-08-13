"""
Public blueprint routes.

Step 5: the catalogue is now seeded (Step 4), so this blueprint exposes
the real, unauthenticated public read API described in Step 2 §32 —
schools, departments, programme categories, and programmes (unified
academic + AI Bootcamp) — plus the original health check.

All routes here are read-only. No write route exists in this blueprint.
"""

from datetime import datetime, timezone

from flask import jsonify, request
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.blueprints.public import public_bp
from app.extensions import db
from app.services import school_service, programme_service, cms_service
from app.utils.responses import success


@public_bp.route("/api/health", methods=["GET"])
def health():
    """Minimal liveness check. Does not touch the database."""
    return jsonify({
        "status": "ok",
        "service": "germaine-backend",
        "time": datetime.now(timezone.utc).isoformat(),
    }), 200


@public_bp.route("/health", methods=["GET"])
def root_health():
    """
    Root-level health check used by start-admin.ps1 to decide when it is
    safe to open the browser. Confirms both that Flask itself is
    responding AND that the configured database is actually reachable
    (a single cheap "SELECT 1", not a real query against any table), so
    a broken/unreachable PostgreSQL instance is reported here instead of
    surfacing as a raw traceback the first time an admin page is opened.

    Deliberately returns only a status flag — no connection string,
    hostname, driver error text, or other DB detail is ever included in
    the response body, so this endpoint is safe to leave publicly
    reachable in every environment.
    """
    try:
        db.session.execute(text("SELECT 1"))
        db_ok = True
    except SQLAlchemyError:
        db_ok = False
    except Exception:
        # Any other unexpected failure (e.g. driver not installed) is
        # still just "database not available" from this endpoint's
        # point of view — never let an unhandled error leak a traceback.
        db_ok = False

    body = {
        "status": "ok" if db_ok else "degraded",
        "service": "germaine-backend",
        "database": "connected" if db_ok else "unavailable",
        "time": datetime.now(timezone.utc).isoformat(),
    }
    return jsonify(body), 200 if db_ok else 503


@public_bp.route("/api/schools", methods=["GET"])
def list_schools():
    active_only = request.args.get("active_only", "true").lower() != "false"
    schools = school_service.list_schools(active_only=active_only)
    return success([school_service.school_to_dict(s) for s in schools])


@public_bp.route("/api/schools/<slug>", methods=["GET"])
def get_school(slug):
    school = school_service.get_school_by_slug(slug)
    return success(school_service.school_to_dict(school, include_departments=True))


@public_bp.route("/api/schools/<slug>/departments", methods=["GET"])
def list_school_departments(slug):
    departments = school_service.list_departments_for_school(slug)
    return success([school_service.department_to_dict(d) for d in departments])


@public_bp.route("/api/programme-categories", methods=["GET"])
def list_programme_categories():
    categories = programme_service.list_categories()
    return success([{"slug": c.slug, "label": c.label, "icon": c.icon} for c in categories])


@public_bp.route("/api/programmes", methods=["GET"])
def list_programmes():
    result = programme_service.search_programmes(
        school_slug=request.args.get("school"),
        department_id=request.args.get("department_id", type=int),
        category_slug=request.args.get("category"),
        programme_type=request.args.get("type"),
        q=request.args.get("q"),
        active_only=request.args.get("active_only", "true").lower() != "false",
        page=request.args.get("page", default=1, type=int),
        per_page=request.args.get("per_page", default=20, type=int),
    )
    return success({
        "items": [programme_service.programme_to_dict(p) for p in result["items"]],
        "total": result["total"],
        "page": result["page"],
        "per_page": result["per_page"],
    })


@public_bp.route("/api/programmes/<slug>", methods=["GET"])
def get_programme(slug):
    programme = programme_service.get_programme_by_slug(slug)
    return success(programme_service.programme_to_dict(programme, detailed=True))


# ---------------------------------------------------------------
# CMS — read-only public endpoints (Step 7 CMS addition).
#
# These deliberately never error just because the CMS is empty — an
# empty/absent SiteContent key, an empty content_list_items result, or
# zero published NewsArticle rows are all valid, expected states (no
# admin has entered that content yet). The frontend bridge scripts that
# call these are responsible for falling back to the existing static
# HTML in that case; this API layer just reports what's there.
# ---------------------------------------------------------------

def _article_to_dict(article, detailed: bool = False) -> dict:
    data = {
        "slug": article.slug,
        "title": article.title,
        "summary": article.summary,
        "category": article.category,
        "author": article.author,
        "featured_image_url": article.featured_image.url_path if article.featured_image else None,
        "published_at": article.published_at.isoformat() if article.published_at else None,
    }
    if detailed:
        data["body"] = article.body
    return data


@public_bp.route("/api/news", methods=["GET"])
def list_news():
    result = cms_service.list_published_news(
        page=request.args.get("page", default=1, type=int),
        per_page=request.args.get("per_page", default=12, type=int),
        category=request.args.get("category"),
    )
    return success({
        "items": [_article_to_dict(a) for a in result["records"]],
        "total": result["total"], "page": result["page"], "per_page": result["per_page"],
    })


@public_bp.route("/api/news/<slug>", methods=["GET"])
def get_news_article(slug):
    article = cms_service.get_published_news_by_slug(slug)
    return success(_article_to_dict(article, detailed=True))


@public_bp.route("/api/site-content", methods=["GET"])
def get_site_content():
    """?keys=homepage.hero_badge,contact.phone,... — bulk-fetch several
    content fields in one request. Unrecognized keys are silently
    ignored (never a 400) so a frontend bridge can be conservative about
    what it asks for without needing to keep two lists in sync."""
    keys_param = request.args.get("keys", "")
    keys = [k.strip() for k in keys_param.split(",") if k.strip()]
    keys = [k for k in keys if k in cms_service.CONTENT_FIELD_REGISTRY]
    return success(cms_service.get_content_values(keys))


@public_bp.route("/api/content-lists/<list_key>", methods=["GET"])
def get_content_list(list_key):
    if list_key not in cms_service.LIST_KEY_REGISTRY:
        return success([])  # unrecognized list_key -> empty, not an error; caller falls back to static content
    items = cms_service.list_list_items(list_key, include_inactive=False)
    return success([
        {
            "id": item.id, "title": item.title, "subtitle": item.subtitle,
            "link_url": item.link_url, "image_url": item.image.url_path if item.image else None,
            "display_order": item.display_order,
        }
        for item in items
    ])
