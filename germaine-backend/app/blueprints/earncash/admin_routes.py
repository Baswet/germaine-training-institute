"""
EarnCash admin routes — ported from
build10/EarnCash/backend/routes/admin.py.

Registered at /api/earncash/admin/... (see app/__init__.py). This is
EarnCash's own admin surface (JWT-authenticated, role='admin' on
earncash_users) — entirely separate from Germaine's staff admin portal
at /admin/ (session-cookie authenticated, admin_users table). Neither
can authenticate against the other.
"""

import os

from flask import request, jsonify, g
from werkzeug.security import check_password_hash

from app.extensions import db
from app.models import (
    EarnCashUser, EarnCashWithdrawal, EarnCashEnrollment, EarnCashCourse,
    EarnCashReferralCommission, EarnCashTransaction, EarnCashNotification, EarnCashAdminLog,
)
from app.utils.earncash_jwt import issue_token, admin_required
from app.utils.earncash_helpers import require_fields
from app.blueprints.earncash import earncash_bp


def _commission_rate():
    try:
        return float(os.environ.get("EARNCASH_COMMISSION_RATE", "0.10"))
    except (TypeError, ValueError):
        return 0.10


def _log_admin_action(admin_id, action, target_type=None, target_id=None):
    db.session.add(EarnCashAdminLog(admin_id=admin_id, action=action, target_type=target_type, target_id=target_id))


# ======================================
# ADMIN LOGIN
# ======================================
@earncash_bp.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json(silent=True) or {}
    missing = require_fields(data, ["email", "password"])
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    email = data["email"].strip().lower()
    password = data["password"]

    admin_user = EarnCashUser.query.filter_by(email=email, role="admin").first()

    if not admin_user or not check_password_hash(admin_user.password_hash, password):
        return jsonify({"error": "Invalid admin credentials"}), 401

    token = issue_token(admin_user.id, role="admin")
    return jsonify({
        "message": "Admin login successful",
        "token": token,
        "admin": {"id": admin_user.id, "name": admin_user.fullname, "role": "admin"},
    })


# ======================================
# VIEW ALL USERS
# ======================================
@earncash_bp.route("/admin/users", methods=["GET"])
@admin_required
def all_users():
    users = (
        EarnCashUser.query.filter_by(role="user")
        .order_by(EarnCashUser.created_at.desc())
        .all()
    )
    return jsonify([
        {
            "id": u.id, "fullname": u.fullname, "email": u.email, "phone": u.phone,
            "wallet": str(u.wallet), "referral_code": u.referral_code, "status": u.status,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ])


# ======================================
# PLATFORM STATISTICS
# ======================================
@earncash_bp.route("/admin/stats", methods=["GET"])
@admin_required
def admin_stats():
    total_users = EarnCashUser.query.filter_by(role="user").count()

    total_paid_out = (
        db.session.query(db.func.coalesce(db.func.sum(EarnCashWithdrawal.amount), 0))
        .filter(EarnCashWithdrawal.status == "approved").scalar()
    )
    pending_withdrawals = EarnCashWithdrawal.query.filter_by(status="pending").count()

    total_tuition_collected = (
        db.session.query(db.func.coalesce(db.func.sum(EarnCashEnrollment.amount_paid), 0))
        .filter(EarnCashEnrollment.payment_status == "paid").scalar()
    )
    pending_enrollments = EarnCashEnrollment.query.filter_by(payment_status="unpaid").count()

    return jsonify({
        "total_users": total_users,
        "total_paid_out": str(total_paid_out),
        "pending_withdrawals": pending_withdrawals,
        "total_tuition_collected": str(total_tuition_collected),
        "pending_enrollments": pending_enrollments,
    })


# ======================================
# VIEW WITHDRAWAL REQUESTS
# ======================================
@earncash_bp.route("/admin/withdrawals", methods=["GET"])
@admin_required
def withdrawals_list():
    status = request.args.get("status")
    query = EarnCashWithdrawal.query
    if status:
        query = query.filter_by(status=status)
    records = query.order_by(EarnCashWithdrawal.created_at.desc()).all()
    return jsonify([w.to_dict(with_user=True) for w in records])


# ======================================
# APPROVE / REJECT WITHDRAWAL
# ======================================
@earncash_bp.route("/admin/withdrawals/<int:withdrawal_id>/approve", methods=["PUT"])
@admin_required
def approve_withdrawal(withdrawal_id):
    w = db.session.get(EarnCashWithdrawal, withdrawal_id)
    if not w:
        return jsonify({"error": "Withdrawal not found"}), 404
    if w.status != "pending":
        return jsonify({"error": f"Withdrawal is already {w.status}"}), 409

    w.status = "approved"
    _log_admin_action(g.earncash_user_id, f"Approved withdrawal #{withdrawal_id}", "withdrawal", withdrawal_id)
    db.session.add(EarnCashNotification(
        user_id=w.user_id, title="Withdrawal approved",
        message=f"Your withdrawal of KES {float(w.amount):.2f} has been approved.",
    ))
    db.session.commit()
    return jsonify({"message": "Withdrawal approved"})


@earncash_bp.route("/admin/withdrawals/<int:withdrawal_id>/reject", methods=["PUT"])
@admin_required
def reject_withdrawal(withdrawal_id):
    data = request.get_json(silent=True) or {}
    note = (data.get("reason") or "").strip() or None

    w = db.session.get(EarnCashWithdrawal, withdrawal_id)
    if not w:
        return jsonify({"error": "Withdrawal not found"}), 404
    if w.status != "pending":
        return jsonify({"error": f"Withdrawal is already {w.status}"}), 409

    w.status = "rejected"
    w.admin_note = note
    # Refund the reserved amount back to the user's wallet.
    user = db.session.get(EarnCashUser, w.user_id)
    user.wallet = float(user.wallet) + float(w.amount)

    db.session.add(EarnCashTransaction(
        user_id=w.user_id, type="reversal", amount=w.amount,
        description=f"Withdrawal #{withdrawal_id} rejected — funds returned",
    ))
    _log_admin_action(g.earncash_user_id, f"Rejected withdrawal #{withdrawal_id}", "withdrawal", withdrawal_id)
    db.session.add(EarnCashNotification(
        user_id=w.user_id, title="Withdrawal rejected",
        message=(
            f"Your withdrawal of KES {float(w.amount):.2f} was rejected. Funds were returned to your wallet."
            + (f" Reason: {note}" if note else "")
        ),
    ))
    db.session.commit()
    return jsonify({"message": "Withdrawal rejected and funds returned"})


# ======================================
# VIEW ENROLLMENTS AWAITING PAYMENT VERIFICATION
# ======================================
@earncash_bp.route("/admin/enrollments", methods=["GET"])
@admin_required
def list_enrollments():
    status = request.args.get("status", "unpaid")
    enrollments = (
        EarnCashEnrollment.query.filter_by(payment_status=status)
        .order_by(EarnCashEnrollment.created_at.desc())
        .all()
    )
    return jsonify([
        {
            "id": e.id,
            "amount_due": str(e.amount_due),
            "amount_paid": str(e.amount_paid),
            "payment_status": e.payment_status,
            "created_at": e.created_at.isoformat() if e.created_at else None,
            "student_name": e.student.fullname if e.student else None,
            "student_email": e.student.email if e.student else None,
            "course_name": e.course.name if e.course else None,
            "referred_by_name": e.referrer.fullname if e.referrer else None,
        }
        for e in enrollments
    ])


# ======================================
# VERIFY TUITION PAYMENT
# This is the ONLY place a referral commission can be created. Admin
# staff confirm real tuition money was received before any commission
# is credited to a referrer's wallet.
# ======================================
@earncash_bp.route("/admin/enrollments/<int:enrollment_id>/verify-payment", methods=["PUT"])
@admin_required
def verify_enrollment_payment(enrollment_id):
    data = request.get_json(silent=True) or {}
    try:
        amount_paid = float(data.get("amount_paid", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid amount_paid"}), 400

    if amount_paid <= 0:
        return jsonify({"error": "amount_paid must be greater than zero"}), 400

    enrollment = db.session.get(EarnCashEnrollment, enrollment_id)
    if not enrollment:
        return jsonify({"error": "Enrollment not found"}), 404

    new_total_paid = float(enrollment.amount_paid) + amount_paid
    amount_due = float(enrollment.amount_due)
    new_status = "paid" if new_total_paid >= amount_due else "partial"

    enrollment.amount_paid = new_total_paid
    enrollment.payment_status = new_status
    enrollment.verified_by_admin = g.earncash_user_id

    commission_created = False
    commission_amount = 0

    # Award commission once, only when the enrollment is fully paid, only
    # if there is a referrer, and only if we haven't already awarded it.
    if new_status == "paid" and enrollment.referred_by and not enrollment.commission_awarded:
        commission_amount = round(amount_due * _commission_rate(), 2)

        db.session.add(EarnCashReferralCommission(
            referrer_id=enrollment.referred_by,
            referred_user_id=enrollment.student_id,
            enrollment_id=enrollment_id,
            commission_amount=commission_amount,
        ))
        referrer = db.session.get(EarnCashUser, enrollment.referred_by)
        referrer.wallet = float(referrer.wallet) + commission_amount
        db.session.add(EarnCashTransaction(
            user_id=enrollment.referred_by, type="commission", amount=commission_amount,
            description=f"Referral commission for enrollment #{enrollment_id}",
        ))
        enrollment.commission_awarded = True
        db.session.add(EarnCashNotification(
            user_id=enrollment.referred_by, title="Commission received",
            message=f"You earned KES {commission_amount:.2f} because your referral completed tuition payment.",
        ))
        commission_created = True

    _log_admin_action(
        g.earncash_user_id,
        f"Verified payment of KES {amount_paid:.2f} for enrollment #{enrollment_id}",
        "enrollment", enrollment_id,
    )
    db.session.add(EarnCashNotification(
        user_id=enrollment.student_id, title="Payment received",
        message=f"We've recorded your payment of KES {amount_paid:.2f}. Status: {new_status}.",
    ))

    db.session.commit()

    return jsonify({
        "message": "Payment verified",
        "payment_status": new_status,
        "total_paid": str(new_total_paid),
        "commission_created": commission_created,
        "commission_amount": str(commission_amount),
    })


# ======================================
# MANAGE COURSES
# ======================================
@earncash_bp.route("/admin/courses", methods=["POST"])
@admin_required
def create_course():
    data = request.get_json(silent=True) or {}
    missing = require_fields(data, ["name", "category", "tuition_fee"])
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    try:
        tuition_fee = float(data["tuition_fee"])
    except (TypeError, ValueError):
        return jsonify({"error": "tuition_fee must be a number"}), 400

    course = EarnCashCourse(
        name=data["name"], category=data["category"], tuition_fee=tuition_fee,
        description=data.get("description"),
    )
    db.session.add(course)
    db.session.commit()
    return jsonify({"message": "Course created", "course_id": course.id}), 201
