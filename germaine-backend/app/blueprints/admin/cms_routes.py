"""
Admin CMS routes (Step 7 CMS addition) — Website Content, News, Media
Library and Academics management pages.

Same conventions as routes.py: server-rendered Jinja2, admin_required on
every route, CSRF validated on every POST, all data access goes through
app/services/cms_service.py (no duplicate query logic here). Registered
on the same admin_bp, so everything stays under /admin — no new
blueprint, no new URL prefix, no public-facing exposure.
"""

import os

from flask import render_template, request, redirect, url_for, flash, abort, current_app

from app.blueprints.admin import admin_bp
from app.services import cms_service
from app.utils.auth import admin_required, current_admin
from app.utils.csrf import get_csrf_token, validate_csrf
from app.utils.validation import NotFoundError, ValidationError


def _require_csrf():
    if not validate_csrf(request.form.get("csrf_token")):
        abort(403)


# =================================================================
# WEBSITE CONTENT
# =================================================================

@admin_bp.route("/content")
@admin_required
def content_editor():
    grouped = cms_service.list_content_grouped()
    return render_template("admin/content_editor.html", grouped=grouped, admin=current_admin())


@admin_bp.route("/content", methods=["POST"])
@admin_required
def content_editor_save():
    _require_csrf()
    errors = []
    for key in cms_service.CONTENT_FIELD_REGISTRY:
        if key in request.form:
            try:
                cms_service.set_content_value(key, request.form.get(key, ""), current_admin())
            except ValidationError as e:
                errors.append(f"{key}: {'; '.join(sum(e.errors.values(), []))}")
    if errors:
        flash("Some fields could not be saved: " + " | ".join(errors), "error")
    else:
        flash("Website content updated.", "success")
    return redirect(url_for("admin.content_editor"))


# =================================================================
# CONTENT LISTS (hero slides / clubs / sports)
# =================================================================

@admin_bp.route("/content/lists/<list_key>")
@admin_required
def content_list_items(list_key):
    if list_key not in cms_service.LIST_KEY_REGISTRY:
        abort(404)
    items = cms_service.list_list_items(list_key)
    media = cms_service.list_media(status="active", per_page=200)["records"]
    return render_template(
        "admin/content_list_items.html", list_key=list_key,
        list_meta=cms_service.LIST_KEY_REGISTRY[list_key], items=items, media=media, admin=current_admin(),
    )


@admin_bp.route("/content/lists/<list_key>/create", methods=["POST"])
@admin_required
def content_list_item_create(list_key):
    _require_csrf()
    try:
        image_id = request.form.get("image_id", type=int)
        display_order = request.form.get("display_order", type=int)
        cms_service.create_list_item(
            list_key, title=request.form.get("title"), subtitle=request.form.get("subtitle"),
            link_url=request.form.get("link_url"), image_id=image_id, display_order=display_order,
        )
        flash("Item added.", "success")
    except ValidationError as e:
        flash("Could not add item: " + "; ".join(sum(e.errors.values(), [])), "error")
    return redirect(url_for("admin.content_list_items", list_key=list_key))


@admin_bp.route("/content/lists/item/<int:item_id>/update", methods=["POST"])
@admin_required
def content_list_item_update(item_id):
    _require_csrf()
    try:
        item = cms_service.get_list_item(item_id)
        image_id = request.form.get("image_id", type=int)
        display_order = request.form.get("display_order", type=int)
        cms_service.update_list_item(
            item_id, title=request.form.get("title"), subtitle=request.form.get("subtitle"),
            link_url=request.form.get("link_url"), image_id=image_id, display_order=display_order,
        )
        list_key = item.list_key
        flash("Item updated.", "success")
    except NotFoundError:
        abort(404)
    except ValidationError as e:
        flash("Could not update item: " + "; ".join(sum(e.errors.values(), [])), "error")
        list_key = cms_service.get_list_item(item_id).list_key
    return redirect(url_for("admin.content_list_items", list_key=list_key))


@admin_bp.route("/content/lists/item/<int:item_id>/archive", methods=["POST"])
@admin_required
def content_list_item_archive(item_id):
    _require_csrf()
    try:
        item = cms_service.archive_list_item(item_id)
    except NotFoundError:
        abort(404)
    flash("Item archived.", "success")
    return redirect(url_for("admin.content_list_items", list_key=item.list_key))


# =================================================================
# MEDIA LIBRARY
# =================================================================

@admin_bp.route("/media")
@admin_required
def media_library():
    page = request.args.get("page", default=1, type=int)
    q = request.args.get("q") or None
    status = request.args.get("status") or "active"
    result = cms_service.list_media(status=status if status != "all" else None, q=q, page=page, per_page=24)
    return render_template("admin/media_library.html", result=result, q=q or "", status=status, admin=current_admin())


def _media_dir():
    media_dir = os.path.join(current_app.static_folder, "media")
    os.makedirs(media_dir, exist_ok=True)
    return media_dir


@admin_bp.route("/media/upload", methods=["POST"])
@admin_required
def media_upload():
    _require_csrf()
    file = request.files.get("file")
    if file is None or file.filename == "":
        flash("No file selected.", "error")
        return redirect(url_for("admin.media_library"))

    raw = file.read()
    try:
        mime = cms_service.validate_upload(file.filename, file.mimetype or "", len(raw), raw[:16])
    except ValidationError as e:
        flash("Upload rejected: " + "; ".join(sum(e.errors.values(), [])), "error")
        return redirect(url_for("admin.media_library"))

    safe_name = cms_service.generate_safe_filename(file.filename)
    dest_path = os.path.join(_media_dir(), safe_name)
    with open(dest_path, "wb") as f:
        f.write(raw)

    cms_service.record_media_asset(
        filename=safe_name, original_filename=file.filename, url_path=f"/static/media/{safe_name}",
        mime_type=mime, size_bytes=len(raw), alt_text=request.form.get("alt_text"), admin=current_admin(),
    )
    flash("Image uploaded.", "success")
    return redirect(url_for("admin.media_library"))


@admin_bp.route("/media/<int:media_id>/replace", methods=["POST"])
@admin_required
def media_replace(media_id):
    _require_csrf()
    try:
        asset = cms_service.get_media(media_id)
    except NotFoundError:
        abort(404)

    file = request.files.get("file")
    if file is None or file.filename == "":
        flash("No replacement file selected.", "error")
        return redirect(url_for("admin.media_library"))

    raw = file.read()
    try:
        mime = cms_service.validate_upload(file.filename, file.mimetype or "", len(raw), raw[:16])
    except ValidationError as e:
        flash("Upload rejected: " + "; ".join(sum(e.errors.values(), [])), "error")
        return redirect(url_for("admin.media_library"))

    safe_name = cms_service.generate_safe_filename(file.filename)
    dest_path = os.path.join(_media_dir(), safe_name)
    with open(dest_path, "wb") as f:
        f.write(raw)

    # Best-effort cleanup of the old physical file — never fatal if it's
    # already missing or unwritable.
    old_path = os.path.join(_media_dir(), asset.filename)
    try:
        if os.path.exists(old_path):
            os.remove(old_path)
    except OSError:
        pass

    cms_service.update_media_file(media_id, filename=safe_name, url_path=f"/static/media/{safe_name}", mime_type=mime, size_bytes=len(raw))
    flash("Image replaced. Every page/article referencing this image now shows the new file.", "success")
    return redirect(url_for("admin.media_library"))


@admin_bp.route("/media/<int:media_id>/alt-text", methods=["POST"])
@admin_required
def media_alt_text_update(media_id):
    _require_csrf()
    try:
        cms_service.update_media_alt_text(media_id, request.form.get("alt_text", ""))
    except NotFoundError:
        abort(404)
    flash("Alt text updated.", "success")
    return redirect(url_for("admin.media_library"))


@admin_bp.route("/media/<int:media_id>/archive", methods=["POST"])
@admin_required
def media_archive(media_id):
    _require_csrf()
    try:
        cms_service.archive_media(media_id)
    except NotFoundError:
        abort(404)
    flash("Image archived.", "success")
    return redirect(url_for("admin.media_library"))


# =================================================================
# NEWS
# =================================================================

@admin_bp.route("/news")
@admin_required
def news_list():
    page = request.args.get("page", default=1, type=int)
    status = request.args.get("status") or None
    q = request.args.get("q") or None
    result = cms_service.list_news_admin(status=status, q=q, page=page)
    return render_template(
        "admin/news_list.html", result=result, status=status or "", q=q or "",
        statuses=cms_service.NEWS_STATUSES, admin=current_admin(),
    )


@admin_bp.route("/news/new", methods=["GET", "POST"])
@admin_required
def news_create():
    if request.method == "POST":
        _require_csrf()
        try:
            article = cms_service.create_news_article(
                {
                    "title": request.form.get("title", ""),
                    "summary": request.form.get("summary", ""),
                    "body": request.form.get("body", ""),
                    "category": request.form.get("category", ""),
                    "author": request.form.get("author", ""),
                    "featured_image_id": request.form.get("featured_image_id", type=int),
                },
                current_admin(),
            )
            flash("Article created as a draft.", "success")
            return redirect(url_for("admin.news_edit", article_id=article.id))
        except ValidationError as e:
            flash("Could not create article: " + "; ".join(sum(e.errors.values(), [])), "error")
    media = cms_service.list_media(status="active", per_page=200)["records"]
    return render_template("admin/news_form.html", article=None, media=media, admin=current_admin())


@admin_bp.route("/news/<int:article_id>", methods=["GET", "POST"])
@admin_required
def news_edit(article_id):
    try:
        article = cms_service.get_news_article(article_id)
    except NotFoundError:
        abort(404)

    if request.method == "POST":
        _require_csrf()
        try:
            cms_service.update_news_article(
                article_id,
                {
                    "title": request.form.get("title", ""),
                    "summary": request.form.get("summary", ""),
                    "body": request.form.get("body", ""),
                    "category": request.form.get("category", ""),
                    "author": request.form.get("author", ""),
                    "featured_image_id": request.form.get("featured_image_id", type=int),
                },
            )
            flash("Article updated.", "success")
            return redirect(url_for("admin.news_edit", article_id=article_id))
        except ValidationError as e:
            flash("Could not save: " + "; ".join(sum(e.errors.values(), [])), "error")

    media = cms_service.list_media(status="active", per_page=200)["records"]
    return render_template("admin/news_form.html", article=article, media=media, admin=current_admin(), csrf_token=get_csrf_token())


@admin_bp.route("/news/<int:article_id>/publish", methods=["POST"])
@admin_required
def news_publish(article_id):
    _require_csrf()
    try:
        cms_service.publish_news_article(article_id)
        flash("Article published.", "success")
    except NotFoundError:
        abort(404)
    except ValidationError as e:
        flash("Could not publish: " + "; ".join(sum(e.errors.values(), [])), "error")
    return redirect(url_for("admin.news_edit", article_id=article_id))


@admin_bp.route("/news/<int:article_id>/unpublish", methods=["POST"])
@admin_required
def news_unpublish(article_id):
    _require_csrf()
    try:
        cms_service.unpublish_news_article(article_id)
        flash("Article moved back to draft.", "success")
    except NotFoundError:
        abort(404)
    return redirect(url_for("admin.news_edit", article_id=article_id))


@admin_bp.route("/news/<int:article_id>/archive", methods=["POST"])
@admin_required
def news_archive(article_id):
    _require_csrf()
    try:
        cms_service.archive_news_article(article_id)
        flash("Article archived.", "success")
    except NotFoundError:
        abort(404)
    return redirect(url_for("admin.news_list"))


# =================================================================
# ACADEMICS — Schools
# =================================================================

@admin_bp.route("/academics/schools")
@admin_required
def academics_schools_list():
    page = request.args.get("page", default=1, type=int)
    q = request.args.get("q") or None
    result = cms_service.list_schools_admin(q=q, page=page)
    return render_template("admin/academics_schools_list.html", result=result, q=q or "", admin=current_admin())


@admin_bp.route("/academics/schools/<int:school_id>", methods=["GET", "POST"])
@admin_required
def academics_school_edit(school_id):
    try:
        school = cms_service.get_school_admin(school_id)
    except NotFoundError:
        abort(404)

    if request.method == "POST":
        _require_csrf()
        try:
            cms_service.update_school(
                school_id, description=request.form.get("description"), fee=request.form.get("fee"),
                is_active=request.form.get("is_active") == "on", display_order=request.form.get("display_order", type=int),
            )
            flash("School updated.", "success")
            return redirect(url_for("admin.academics_school_edit", school_id=school_id))
        except ValidationError as e:
            flash("Could not save: " + "; ".join(sum(e.errors.values(), [])), "error")

    return render_template("admin/academics_school_form.html", school=school, admin=current_admin(), csrf_token=get_csrf_token())


# =================================================================
# ACADEMICS — Programmes
# =================================================================

@admin_bp.route("/academics/programmes")
@admin_required
def academics_programmes_list():
    page = request.args.get("page", default=1, type=int)
    q = request.args.get("q") or None
    programme_type = request.args.get("programme_type") or None
    result = cms_service.list_programmes_admin(programme_type=programme_type, q=q, page=page)
    return render_template(
        "admin/academics_programmes_list.html", result=result, q=q or "",
        programme_type=programme_type or "", admin=current_admin(),
    )


@admin_bp.route("/academics/programmes/<int:programme_id>", methods=["GET", "POST"])
@admin_required
def academics_programme_edit(programme_id):
    try:
        programme = cms_service.get_programme_admin(programme_id)
    except NotFoundError:
        abort(404)

    if request.method == "POST":
        _require_csrf()
        try:
            cms_service.update_programme(
                programme_id,
                overview=request.form.get("overview"),
                gain_points=request.form.get("gain_points"),
                entry_requirement=request.form.get("entry_requirement"),
                exam_body=request.form.get("exam_body"),
                apply_heading=request.form.get("apply_heading"),
                apply_subtext=request.form.get("apply_subtext"),
                is_active=request.form.get("is_active") == "on",
                display_order=request.form.get("display_order", type=int),
            )
            flash("Programme updated.", "success")
            return redirect(url_for("admin.academics_programme_edit", programme_id=programme_id))
        except ValidationError as e:
            flash("Could not save: " + "; ".join(sum(e.errors.values(), [])), "error")

    return render_template("admin/academics_programme_form.html", programme=programme, admin=current_admin(), csrf_token=get_csrf_token())


@admin_bp.route("/academics/programmes/modes/<int:mode_id>", methods=["POST"])
@admin_required
def academics_programme_mode_update(mode_id):
    _require_csrf()
    try:
        mode = cms_service.update_programme_mode(
            mode_id,
            fee_amount=request.form.get("fee_amount") if "fee_amount" in request.form else None,
            is_available=(request.form.get("is_available") == "on") if "is_available_present" in request.form else None,
            schedule=request.form.get("schedule") if "schedule" in request.form else None,
        )
        flash("Programme mode updated.", "success")
        return redirect(url_for("admin.academics_programme_edit", programme_id=mode.programme_id))
    except NotFoundError:
        abort(404)
    except ValidationError as e:
        flash("Could not save mode: " + "; ".join(sum(e.errors.values(), [])), "error")
        return redirect(request.referrer or url_for("admin.academics_programmes_list"))


# =================================================================
# ACADEMICS — Categories
# =================================================================

@admin_bp.route("/academics/categories")
@admin_required
def academics_categories_list():
    categories = cms_service.list_categories_admin()
    return render_template("admin/academics_categories_list.html", categories=categories, admin=current_admin())


@admin_bp.route("/academics/categories/<int:category_id>", methods=["GET", "POST"])
@admin_required
def academics_category_edit(category_id):
    try:
        category = cms_service.get_category_admin(category_id)
    except NotFoundError:
        abort(404)

    if request.method == "POST":
        _require_csrf()
        try:
            cms_service.update_category(category_id, label=request.form.get("label"), icon=request.form.get("icon"))
            flash("Category updated.", "success")
            return redirect(url_for("admin.academics_categories_list"))
        except ValidationError as e:
            flash("Could not save: " + "; ".join(sum(e.errors.values(), [])), "error")

    return render_template("admin/academics_category_form.html", category=category, admin=current_admin(), csrf_token=get_csrf_token())
