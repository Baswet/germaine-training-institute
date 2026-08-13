"""
Admin blueprint (Step 7) — the secure GTI staff administration portal.

Server-rendered (Jinja2) pages under /admin, session-cookie authenticated
(app/utils/auth.py), CSRF-protected on every state-changing POST
(app/utils/csrf.py). This blueprint calls app/services/admin_service.py
directly for all data access — no duplicate models, no second copy of
business logic (Step 7 §14Y/§14Z).

Routing note: this blueprint was previously registered at url_prefix
"/api/admin" as an empty Step 3 placeholder (no routes existed). It is
now registered at url_prefix "/admin" in app/__init__.py because it
serves HTML pages for human staff, not a JSON API — "/api/..." remains
reserved for the public, unauthenticated catalogue/enquiry endpoints
documented in API_DOCS.md. This is a zero-risk rename: no route existed
under the old prefix for anything to depend on.

Every route except /admin/login requires an authenticated session
(admin_required). No admin data is ever reachable without it, and none
of these routes are registered under /api/, so the public catalogue
endpoints are never mixed with authenticated admin data.
"""

from flask import render_template, request, redirect, url_for, session, flash, abort

from app.blueprints.admin import admin_bp
from app.services import admin_service
from app.utils.auth import admin_required, current_admin
from app.utils.csrf import get_csrf_token, validate_csrf
from app.utils.validation import NotFoundError, ValidationError


@admin_bp.context_processor
def inject_csrf_token():
    """Every admin template (base.html's logout form included) can reference
    `csrf_token` without every single route explicitly passing it."""
    return {"csrf_token": get_csrf_token()}


# ---------------------------------------------------------------
# AUTH
# ---------------------------------------------------------------

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_admin() is not None:
        return redirect(url_for("admin.dashboard"))

    error = None
    if request.method == "POST":
        if not validate_csrf(request.form.get("csrf_token")):
            abort(403)
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""
        admin = admin_service.authenticate(email, password)
        if admin is None:
            # Deliberately generic — never reveals whether the account exists (Step 7 §14W).
            error = "Invalid email or password."
        else:
            session.clear()
            session["admin_user_id"] = admin.id
            session.permanent = True
            admin_service.record_login(admin)
            next_path = request.args.get("next") or url_for("admin.dashboard")
            return redirect(next_path)

    return render_template("admin/login.html", error=error, csrf_token=get_csrf_token())


@admin_bp.route("/logout", methods=["POST"])
@admin_required
def logout():
    if not validate_csrf(request.form.get("csrf_token")):
        abort(403)
    session.clear()
    return redirect(url_for("admin.login"))


# ---------------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------------

@admin_bp.route("/")
@admin_required
def dashboard():
    stats = admin_service.dashboard_stats()
    return render_template("admin/dashboard.html", stats=stats, admin=current_admin())


# ---------------------------------------------------------------
# APPLICATIONS  (also the Scholarship Applications view, filtered)
# ---------------------------------------------------------------

@admin_bp.route("/applications")
@admin_required
def applications_list():
    page = request.args.get("page", default=1, type=int)
    status = request.args.get("status") or None
    q = request.args.get("q") or None
    result = admin_service.list_applications(status=status, application_type=None, q=q, page=page)
    return render_template(
        "admin/applications_list.html", result=result, status=status, q=q or "",
        statuses=admin_service.APPLICATION_STATUSES, admin=current_admin(),
        title="Applications", base_url="admin.applications_list", application_type=None,
    )


@admin_bp.route("/scholarships")
@admin_required
def scholarships_list():
    page = request.args.get("page", default=1, type=int)
    status = request.args.get("status") or None
    q = request.args.get("q") or None
    result = admin_service.list_applications(status=status, application_type="scholarship", q=q, page=page)
    return render_template(
        "admin/applications_list.html", result=result, status=status, q=q or "",
        statuses=admin_service.APPLICATION_STATUSES, admin=current_admin(),
        title="Scholarship Applications", base_url="admin.scholarships_list", application_type="scholarship",
    )


@admin_bp.route("/applications/<int:app_id>")
@admin_required
def application_detail(app_id):
    try:
        application = admin_service.get_application(app_id)
    except NotFoundError:
        abort(404)
    return render_template(
        "admin/application_detail.html", application=application,
        statuses=admin_service.APPLICATION_STATUSES, admin=current_admin(), csrf_token=get_csrf_token(),
    )


@admin_bp.route("/applications/<int:app_id>/status", methods=["POST"])
@admin_required
def application_status_update(app_id):
    if not validate_csrf(request.form.get("csrf_token")):
        abort(403)
    new_status = request.form.get("status", "")
    try:
        admin_service.update_application_status(app_id, new_status)
    except NotFoundError:
        abort(404)
    except ValidationError:
        flash("Invalid status value.", "error")
    return redirect(url_for("admin.application_detail", app_id=app_id))


@admin_bp.route("/applications/<int:app_id>/confirm-tuition", methods=["POST"])
@admin_required
def application_confirm_tuition(app_id):
    """EarnFastCash referral integration (Part 1): admin confirms real
    tuition payment was received on this application. Only when the
    application was genuinely referred AND its programme mode has a
    real published fee does this create a real commission — see
    admin_service.confirm_application_tuition for the full rule."""
    if not validate_csrf(request.form.get("csrf_token")):
        abort(403)
    try:
        result = admin_service.confirm_application_tuition(app_id)
    except NotFoundError:
        abort(404)
    if result["already_confirmed"]:
        flash("Tuition payment was already confirmed for this application.", "info")
    elif result["commission_created"]:
        flash(f"Tuition payment confirmed. Referral commission of KES {result['commission_amount']:.2f} credited.", "success")
    else:
        flash("Tuition payment confirmed.", "success")
    return redirect(url_for("admin.application_detail", app_id=app_id))


# ---------------------------------------------------------------
# ALUMNI (read-only)
# ---------------------------------------------------------------

@admin_bp.route("/alumni")
@admin_required
def alumni_list():
    page = request.args.get("page", default=1, type=int)
    q = request.args.get("q") or None
    grad_year = request.args.get("graduation_year", type=int)
    result = admin_service.list_alumni(q=q, graduation_year=grad_year, page=page)
    return render_template("admin/alumni_list.html", result=result, q=q or "", admin=current_admin())


@admin_bp.route("/alumni/<int:alumni_id>")
@admin_required
def alumni_detail(alumni_id):
    try:
        record = admin_service.get_alumni_record(alumni_id)
    except NotFoundError:
        abort(404)
    return render_template("admin/alumni_detail.html", record=record, admin=current_admin())


# ---------------------------------------------------------------
# ENQUIRIES — contact
# ---------------------------------------------------------------

@admin_bp.route("/enquiries/contact")
@admin_required
def contact_list():
    page = request.args.get("page", default=1, type=int)
    status = request.args.get("status") or None
    q = request.args.get("q") or None
    result = admin_service.list_contact_messages(status=status, q=q, page=page)
    return render_template(
        "admin/contact_list.html", result=result, status=status, q=q or "",
        statuses=admin_service.CONTACT_MESSAGE_STATUSES, admin=current_admin(),
    )


@admin_bp.route("/enquiries/contact/<int:message_id>")
@admin_required
def contact_detail(message_id):
    try:
        record = admin_service.get_contact_message(message_id)
    except NotFoundError:
        abort(404)
    return render_template(
        "admin/contact_detail.html", record=record, statuses=admin_service.CONTACT_MESSAGE_STATUSES,
        admin=current_admin(), csrf_token=get_csrf_token(),
    )


@admin_bp.route("/enquiries/contact/<int:message_id>/status", methods=["POST"])
@admin_required
def contact_status_update(message_id):
    if not validate_csrf(request.form.get("csrf_token")):
        abort(403)
    try:
        admin_service.update_contact_message_status(message_id, request.form.get("status", ""))
    except NotFoundError:
        abort(404)
    except ValidationError:
        flash("Invalid status value.", "error")
    return redirect(url_for("admin.contact_detail", message_id=message_id))


# ---------------------------------------------------------------
# ENQUIRIES — graduate profile requests
# ---------------------------------------------------------------

@admin_bp.route("/enquiries/graduate-requests")
@admin_required
def graduate_requests_list():
    page = request.args.get("page", default=1, type=int)
    status = request.args.get("status") or None
    q = request.args.get("q") or None
    result = admin_service.list_graduate_requests(status=status, q=q, page=page)
    return render_template(
        "admin/graduate_requests_list.html", result=result, status=status, q=q or "",
        statuses=admin_service.GRADUATE_REQUEST_STATUSES, admin=current_admin(),
    )


@admin_bp.route("/enquiries/graduate-requests/<int:request_id>")
@admin_required
def graduate_request_detail(request_id):
    try:
        record = admin_service.get_graduate_request(request_id)
    except NotFoundError:
        abort(404)
    return render_template(
        "admin/graduate_request_detail.html", record=record, statuses=admin_service.GRADUATE_REQUEST_STATUSES,
        admin=current_admin(), csrf_token=get_csrf_token(),
    )


@admin_bp.route("/enquiries/graduate-requests/<int:request_id>/status", methods=["POST"])
@admin_required
def graduate_request_status_update(request_id):
    if not validate_csrf(request.form.get("csrf_token")):
        abort(403)
    try:
        admin_service.update_graduate_request_status(request_id, request.form.get("status", ""))
    except NotFoundError:
        abort(404)
    except ValidationError:
        flash("Invalid status value.", "error")
    return redirect(url_for("admin.graduate_request_detail", request_id=request_id))


# ---------------------------------------------------------------
# ENQUIRIES — partnerships / corporate training (same table, enquiry_type)
# ---------------------------------------------------------------

@admin_bp.route("/enquiries/partnerships")
@admin_required
def partnerships_list():
    page = request.args.get("page", default=1, type=int)
    status = request.args.get("status") or None
    q = request.args.get("q") or None
    result = admin_service.list_partner_enquiries(enquiry_type="partnership", status=status, q=q, page=page)
    return render_template(
        "admin/partner_enquiries_list.html", result=result, status=status, q=q or "",
        statuses=admin_service.PARTNER_ENQUIRY_STATUSES, admin=current_admin(),
        title="Partnership Enquiries", base_url="admin.partnerships_list",
    )


@admin_bp.route("/enquiries/corporate-training")
@admin_required
def corporate_training_list():
    page = request.args.get("page", default=1, type=int)
    status = request.args.get("status") or None
    q = request.args.get("q") or None
    result = admin_service.list_partner_enquiries(enquiry_type="corporate_training", status=status, q=q, page=page)
    return render_template(
        "admin/partner_enquiries_list.html", result=result, status=status, q=q or "",
        statuses=admin_service.PARTNER_ENQUIRY_STATUSES, admin=current_admin(),
        title="Corporate Training Requests", base_url="admin.corporate_training_list",
    )


@admin_bp.route("/enquiries/partner/<int:enquiry_id>")
@admin_required
def partner_enquiry_detail(enquiry_id):
    try:
        record = admin_service.get_partner_enquiry(enquiry_id)
    except NotFoundError:
        abort(404)
    return render_template(
        "admin/partner_enquiry_detail.html", record=record, statuses=admin_service.PARTNER_ENQUIRY_STATUSES,
        admin=current_admin(), csrf_token=get_csrf_token(),
    )


@admin_bp.route("/enquiries/partner/<int:enquiry_id>/status", methods=["POST"])
@admin_required
def partner_enquiry_status_update(enquiry_id):
    if not validate_csrf(request.form.get("csrf_token")):
        abort(403)
    try:
        admin_service.update_partner_enquiry_status(enquiry_id, request.form.get("status", ""))
    except NotFoundError:
        abort(404)
    except ValidationError:
        flash("Invalid status value.", "error")
    return redirect(url_for("admin.partner_enquiry_detail", enquiry_id=enquiry_id))


# ---------------------------------------------------------------
# NEWSLETTER SUBSCRIBERS (read-only)
# ---------------------------------------------------------------

@admin_bp.route("/newsletter")
@admin_required
def newsletter_list():
    page = request.args.get("page", default=1, type=int)
    q = request.args.get("q") or None
    active_param = request.args.get("active")
    active_only = {"true": True, "false": False}.get(active_param)
    result = admin_service.list_newsletter_subscribers(active_only=active_only, q=q, page=page)
    return render_template("admin/newsletter_list.html", result=result, q=q or "", active_param=active_param or "", admin=current_admin())
