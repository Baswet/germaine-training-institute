"""
Admin — Newsroom (News & Events publication).

Same auth (admin_required) and CSRF (validate_csrf) as the rest of the
admin portal. Stories are NewsArticle rows + NewsArticleMeta; events are
NewsEvent rows. Image uploads reuse the existing CMS media validation
(extension + MIME + magic bytes) and land in the existing media library.
"""

import os

from flask import abort, current_app, flash, redirect, render_template, request, url_for
from sqlalchemy.orm import joinedload

from app.blueprints.admin import admin_bp
from app.extensions import db
from app.models import NewsArticle
from app.models.newsroom import EVENT_CATEGORIES, NEWS_CATEGORIES, NewsArticleMeta, NewsEvent
from app.services import cms_service, newsroom_service
from app.utils.auth import admin_required, current_admin
from app.utils.csrf import get_csrf_token, validate_csrf
from app.utils.validation import NotFoundError, ValidationError

STORY_FIELDS = ("title", "summary", "body", "author", "news_category", "is_external", "source_name",
                "source_url", "source_published_at", "image_credit", "video_url", "video_duration",
                "feature_rank", "trending_note")
FLAGS = ("is_featured", "is_trending", "is_breaking", "is_editors_pick")
EVENT_FIELDS = ("title", "category", "description", "organizer", "start_date", "end_date", "start_time",
                "date_note", "venue", "county", "registration_url", "source_url", "status_override")


def _require_csrf():
    if not validate_csrf(request.form.get("csrf_token")):
        abort(403)


def _errors(e: ValidationError) -> str:
    return "; ".join(sum(e.errors.values(), []))


def _uploaded_image_id():
    """Optional inline upload -> MediaAsset id (or None). Raises ValidationError."""
    file = request.files.get("image_file")
    if file is None or not file.filename:
        return None
    raw = file.read()
    mime = cms_service.validate_upload(file.filename, file.mimetype or "", len(raw), raw[:16])
    safe_name = cms_service.generate_safe_filename(file.filename)
    media_dir = os.path.join(current_app.static_folder, "media")
    os.makedirs(media_dir, exist_ok=True)
    with open(os.path.join(media_dir, safe_name), "wb") as fh:
        fh.write(raw)
    asset = cms_service.record_media_asset(
        filename=safe_name, original_filename=file.filename, url_path=f"/static/media/{safe_name}",
        mime_type=mime, size_bytes=len(raw), alt_text=request.form.get("image_alt") or None, admin=current_admin(),
    )
    return asset.id


def _media():
    return cms_service.list_media(status="active", per_page=200)["records"]


# ---------------------------------------------------------------- overview
@admin_bp.route("/newsroom")
@admin_required
def newsroom_index():
    tab = request.args.get("tab") or "stories"
    q = (request.args.get("q") or "").strip()
    stories = (db.session.query(NewsArticle).options(joinedload(NewsArticle.meta))
               .join(NewsArticleMeta, NewsArticleMeta.article_id == NewsArticle.id)
               .filter(NewsArticle.status != "archived"))
    events = NewsEvent.query
    if q:
        like = f"%{q[:100]}%"
        stories = stories.filter(NewsArticle.title.ilike(like))
        events = events.filter(NewsEvent.title.ilike(like))
    return render_template(
        "admin/newsroom_index.html", tab=tab, q=q,
        stories=stories.order_by(NewsArticle.updated_at.desc()).limit(300).all(),
        events=events.order_by(NewsEvent.start_date.desc()).limit(300).all(),
        news_labels=dict(NEWS_CATEGORIES), event_labels=dict(EVENT_CATEGORIES),
        event_status=newsroom_service.event_status,
        admin=current_admin(), csrf_token=get_csrf_token(),
    )


# ---------------------------------------------------------------- stories
def _story_form_data():
    data = {k: request.form.get(k, "") for k in STORY_FIELDS}
    data["is_external"] = "1" if request.form.get("is_external") else "0"
    for f in FLAGS:
        data[f] = "1" if request.form.get(f) else "0"
    image_id = _uploaded_image_id() or request.form.get("featured_image_id", type=int)
    data["featured_image_id"] = image_id
    return data


@admin_bp.route("/newsroom/stories/new", methods=["GET", "POST"])
@admin_required
def newsroom_story_new():
    if request.method == "POST":
        _require_csrf()
        try:
            article = newsroom_service.save_story(_story_form_data(), current_admin())
            flash("Story saved as a draft.", "success")
            return redirect(url_for("admin.newsroom_story_edit", article_id=article.id))
        except ValidationError as e:
            db.session.rollback()
            flash("Could not save: " + _errors(e), "error")
    return render_template("admin/newsroom_story_form.html", article=None, meta=None, form=request.form,
                           categories=NEWS_CATEGORIES, media=_media(), admin=current_admin(),
                           csrf_token=get_csrf_token())


@admin_bp.route("/newsroom/stories/<int:article_id>", methods=["GET", "POST"])
@admin_required
def newsroom_story_edit(article_id):
    try:
        article = cms_service.get_news_article(article_id)
    except NotFoundError:
        abort(404)
    if request.method == "POST":
        _require_csrf()
        try:
            newsroom_service.save_story(_story_form_data(), current_admin(), article_id=article_id)
            flash("Story updated.", "success")
            return redirect(url_for("admin.newsroom_story_edit", article_id=article_id))
        except ValidationError as e:
            db.session.rollback()
            flash("Could not save: " + _errors(e), "error")
    return render_template("admin/newsroom_story_form.html", article=article, meta=article.meta, form=None,
                           categories=NEWS_CATEGORIES, media=_media(), admin=current_admin(),
                           csrf_token=get_csrf_token())


@admin_bp.route("/newsroom/stories/<int:article_id>/publish", methods=["POST"])
@admin_required
def newsroom_story_publish(article_id):
    _require_csrf()
    try:
        newsroom_service.publish_story(article_id)
        flash("Story published.", "success")
    except NotFoundError:
        abort(404)
    except ValidationError as e:
        flash("Could not publish: " + _errors(e), "error")
    return redirect(url_for("admin.newsroom_story_edit", article_id=article_id))


@admin_bp.route("/newsroom/stories/<int:article_id>/unpublish", methods=["POST"])
@admin_required
def newsroom_story_unpublish(article_id):
    _require_csrf()
    try:
        cms_service.unpublish_news_article(article_id)
        flash("Story moved back to draft.", "success")
    except NotFoundError:
        abort(404)
    return redirect(url_for("admin.newsroom_story_edit", article_id=article_id))


@admin_bp.route("/newsroom/stories/<int:article_id>/remove", methods=["POST"])
@admin_required
def newsroom_story_remove(article_id):
    """Remove from the publication (archived — recoverable via News admin)."""
    _require_csrf()
    try:
        cms_service.archive_news_article(article_id)
        flash("Story removed from the publication (archived).", "success")
    except NotFoundError:
        abort(404)
    return redirect(url_for("admin.newsroom_index"))


# ---------------------------------------------------------------- events
def _event_form_data():
    data = {k: request.form.get(k, "") for k in EVENT_FIELDS}
    data["is_featured"] = "1" if request.form.get("is_featured") else "0"
    data["image_id"] = _uploaded_image_id() or request.form.get("image_id", type=int)
    return data


@admin_bp.route("/newsroom/events/new", methods=["GET", "POST"])
@admin_required
def newsroom_event_new():
    if request.method == "POST":
        _require_csrf()
        try:
            event = newsroom_service.save_event(_event_form_data())
            flash("Event saved as a draft.", "success")
            return redirect(url_for("admin.newsroom_event_edit", event_id=event.id))
        except ValidationError as e:
            db.session.rollback()
            flash("Could not save: " + _errors(e), "error")
    return render_template("admin/newsroom_event_form.html", event=None, form=request.form,
                           categories=EVENT_CATEGORIES, media=_media(), status=None,
                           admin=current_admin(), csrf_token=get_csrf_token())


@admin_bp.route("/newsroom/events/<int:event_id>", methods=["GET", "POST"])
@admin_required
def newsroom_event_edit(event_id):
    event = db.session.get(NewsEvent, event_id)
    if event is None:
        abort(404)
    if request.method == "POST":
        _require_csrf()
        try:
            newsroom_service.save_event(_event_form_data(), event_id=event_id)
            flash("Event updated.", "success")
            return redirect(url_for("admin.newsroom_event_edit", event_id=event_id))
        except ValidationError as e:
            db.session.rollback()
            flash("Could not save: " + _errors(e), "error")
    return render_template("admin/newsroom_event_form.html", event=event, form=None,
                           categories=EVENT_CATEGORIES, media=_media(),
                           status=newsroom_service.event_status(event),
                           admin=current_admin(), csrf_token=get_csrf_token())


@admin_bp.route("/newsroom/events/<int:event_id>/publish", methods=["POST"])
@admin_required
def newsroom_event_publish(event_id):
    _require_csrf()
    try:
        newsroom_service.set_event_publication(event_id, True)
        flash("Event published.", "success")
    except NotFoundError:
        abort(404)
    except ValidationError as e:
        flash("Could not publish: " + _errors(e), "error")
    return redirect(url_for("admin.newsroom_event_edit", event_id=event_id))


@admin_bp.route("/newsroom/events/<int:event_id>/unpublish", methods=["POST"])
@admin_required
def newsroom_event_unpublish(event_id):
    _require_csrf()
    try:
        newsroom_service.set_event_publication(event_id, False)
        flash("Event moved back to draft.", "success")
    except NotFoundError:
        abort(404)
    return redirect(url_for("admin.newsroom_event_edit", event_id=event_id))


@admin_bp.route("/newsroom/events/<int:event_id>/delete", methods=["POST"])
@admin_required
def newsroom_event_delete(event_id):
    _require_csrf()
    if request.form.get("confirm") != "DELETE":
        flash("Type DELETE to confirm removing this event.", "error")
        return redirect(url_for("admin.newsroom_event_edit", event_id=event_id))
    if newsroom_service.delete_event(event_id):
        flash("Event deleted.", "success")
    return redirect(url_for("admin.newsroom_index", tab="events"))
