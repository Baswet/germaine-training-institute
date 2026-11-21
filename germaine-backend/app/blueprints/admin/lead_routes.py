"""
Admin — Applicant Leads (real-time lead capture follow-up).

Uses the existing admin session auth (admin_required) and the existing
session CSRF token (validate_csrf) on every state-changing POST — no new
login system, no JSON API, nothing under /api/. All data access goes through
app/services/lead_service.py.
"""

from flask import abort, flash, redirect, render_template, request, url_for

from app.blueprints.admin import admin_bp
from app.models.applicant_lead import LEAD_STATUS_LABELS, LEAD_STATUSES
from app.services import lead_service
from app.utils.auth import admin_required, current_admin
from app.utils.csrf import validate_csrf
from app.utils.validation import NotFoundError, ValidationError

SORTS = {"newest": "Newest first", "oldest": "Oldest first"}
APP_STATUSES = {"incomplete": "Incomplete", "submitted": "Submitted"}


@admin_bp.app_template_filter("eat")
def format_eat(value, fmt="%d %b %Y, %H:%M"):
    """Render an aware UTC datetime in Nairobi time (EAT, UTC+3)."""
    if not value:
        return "—"
    if value.tzinfo is None:  # SQLite (tests) returns naive UTC
        from datetime import timezone
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(lead_service.EAT).strftime(fmt)


def _require_csrf():
    if not validate_csrf(request.form.get("csrf_token")):
        abort(403)


@admin_bp.route("/leads")
@admin_required
def leads_list():
    page = request.args.get("page", default=1, type=int)
    q = (request.args.get("q") or "").strip()[:100]
    lead_status = request.args.get("lead_status") or ""
    app_status = request.args.get("app_status") or ""
    sort = request.args.get("sort") if request.args.get("sort") in SORTS else "newest"
    uncontacted = request.args.get("uncontacted") == "1"
    result = lead_service.list_leads(
        q=q or None, lead_status=lead_status or None, app_status=app_status or None,
        sort=sort, uncontacted=uncontacted, page=page,
    )
    filters = {"q": q, "lead_status": lead_status, "app_status": app_status, "sort": sort,
               "uncontacted": "1" if uncontacted else ""}
    return render_template(
        "admin/leads_list.html", result=result, stats=lead_service.lead_stats(), filters=filters,
        lead_statuses=LEAD_STATUSES, status_labels=LEAD_STATUS_LABELS, app_statuses=APP_STATUSES,
        sorts=SORTS, admin=current_admin(),
    )


@admin_bp.route("/leads/<int:lead_id>")
@admin_required
def lead_detail(lead_id):
    try:
        lead = lead_service.get_lead(lead_id)
    except NotFoundError:
        abort(404)
    return render_template(
        "admin/lead_detail.html", lead=lead, duplicates=lead_service.possible_duplicates(lead),
        audit=lead_service.audit_entries(lead.id), lead_statuses=LEAD_STATUSES,
        status_labels=LEAD_STATUS_LABELS, admin=current_admin(),
    )


@admin_bp.route("/leads/<int:lead_id>/follow-up", methods=["POST"])
@admin_required
def lead_follow_up_update(lead_id):
    _require_csrf()
    try:
        lead_service.update_follow_up(
            lead_id, current_admin(),
            status=request.form.get("lead_status") or None,
            contacted_at_raw=request.form.get("contacted_at") or None,
            notes=request.form.get("follow_up_notes"),
        )
        flash("Follow-up details saved.", "success")
    except NotFoundError:
        abort(404)
    except ValidationError as err:
        flash(next(iter(err.errors.values()))[0], "error")
    return redirect(url_for("admin.lead_detail", lead_id=lead_id))


@admin_bp.route("/leads/<int:lead_id>/delete", methods=["GET"])
@admin_required
def lead_delete_confirm(lead_id):
    try:
        lead = lead_service.get_lead(lead_id)
    except NotFoundError:
        flash("That lead has already been deleted.", "info")
        return redirect(url_for("admin.leads_list"))
    return render_template("admin/lead_delete_confirm.html", lead=lead, admin=current_admin())


@admin_bp.route("/leads/<int:lead_id>/delete", methods=["POST"])
@admin_required
def lead_delete(lead_id):
    _require_csrf()
    if request.form.get("confirm") != "yes":
        flash("Deletion was not confirmed.", "error")
        return redirect(url_for("admin.lead_delete_confirm", lead_id=lead_id))
    try:
        result = lead_service.delete_lead(
            lead_id, current_admin(), acknowledge_linked=request.form.get("confirm_linked") == "yes",
        )
    except ValidationError as err:
        flash(next(iter(err.errors.values()))[0], "error")
        return redirect(url_for("admin.lead_delete_confirm", lead_id=lead_id))
    if result["already_deleted"]:
        flash("That lead had already been deleted.", "info")
    else:
        flash("Lead deleted. No application or other admissions record was changed.", "success")
    return redirect(url_for("admin.leads_list"))


@admin_bp.route("/leads/<int:lead_id>/anonymise", methods=["POST"])
@admin_required
def lead_anonymise(lead_id):
    _require_csrf()
    if request.form.get("confirm") != "yes":
        flash("Anonymisation was not confirmed.", "error")
        return redirect(url_for("admin.lead_delete_confirm", lead_id=lead_id))
    try:
        lead_service.anonymize_lead(lead_id, current_admin())
    except NotFoundError:
        flash("That lead no longer exists.", "info")
        return redirect(url_for("admin.leads_list"))
    flash("Personal details removed. The lead record is kept for statistics.", "success")
    return redirect(url_for("admin.lead_detail", lead_id=lead_id))
