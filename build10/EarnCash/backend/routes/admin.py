from flask import Blueprint, request, jsonify, g
from werkzeug.security import check_password_hash

from database import get_db
from models import user as user_model, wallet as wallet_model, referral as referral_model, withdrawal as withdrawal_model
from utils.security import issue_token, admin_required
from utils.helpers import require_fields
from config import Config

admin = Blueprint("admin", __name__)


def _log_admin_action(cursor, admin_id, action, target_type=None, target_id=None):
    cursor.execute(
        "INSERT INTO admin_logs (admin_id, action, target_type, target_id) VALUES (%s,%s,%s,%s)",
        (admin_id, action, target_type, target_id),
    )


# ======================================
# ADMIN LOGIN
# ======================================
@admin.route("/login", methods=["POST"])
def admin_login():
    data = request.get_json(silent=True) or {}
    missing = require_fields(data, ["email", "password"])
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    email = data["email"].strip().lower()
    password = data["password"]

    with get_db() as (conn, cursor):
        cursor.execute("SELECT * FROM users WHERE email=%s AND role='admin'", (email,))
        admin_user = cursor.fetchone()

        if not admin_user or not check_password_hash(admin_user["password_hash"], password):
            return jsonify({"error": "Invalid admin credentials"}), 401

        token = issue_token(admin_user["id"], role="admin")
        return jsonify({
            "message": "Admin login successful",
            "token": token,
            "admin": {"id": admin_user["id"], "name": admin_user["fullname"], "role": "admin"},
        })


# ======================================
# VIEW ALL USERS
# ======================================
@admin.route("/users", methods=["GET"])
@admin_required
def all_users():
    with get_db() as (conn, cursor):
        cursor.execute(
            """
            SELECT id, fullname, email, phone, wallet, referral_code, status, created_at
            FROM users WHERE role='user'
            ORDER BY created_at DESC
            """
        )
        return jsonify(cursor.fetchall())


# ======================================
# PLATFORM STATISTICS
# ======================================
@admin.route("/stats", methods=["GET"])
@admin_required
def admin_stats():
    with get_db() as (conn, cursor):
        cursor.execute("SELECT COUNT(*) AS total FROM users WHERE role='user'")
        total_users = cursor.fetchone()["total"]

        cursor.execute("SELECT COALESCE(SUM(amount),0) AS total FROM withdrawals WHERE status='approved'")
        total_paid_out = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM withdrawals WHERE status='pending'")
        pending_withdrawals = cursor.fetchone()["total"]

        cursor.execute("SELECT COALESCE(SUM(amount_paid),0) AS total FROM enrollments WHERE payment_status='paid'")
        total_tuition_collected = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM enrollments WHERE payment_status='unpaid'")
        pending_enrollments = cursor.fetchone()["total"]

        return jsonify({
            "total_users": total_users,
            "total_paid_out": total_paid_out,
            "pending_withdrawals": pending_withdrawals,
            "total_tuition_collected": total_tuition_collected,
            "pending_enrollments": pending_enrollments,
        })


# ======================================
# VIEW WITHDRAWAL REQUESTS
# ======================================
@admin.route("/withdrawals", methods=["GET"])
@admin_required
def withdrawals_list():
    status = request.args.get("status")
    with get_db() as (conn, cursor):
        return jsonify(withdrawal_model.get_all(cursor, status))


# ======================================
# APPROVE / REJECT WITHDRAWAL
# ======================================
@admin.route("/withdrawals/<int:withdrawal_id>/approve", methods=["PUT"])
@admin_required
def approve_withdrawal(withdrawal_id):
    with get_db() as (conn, cursor):
        w = withdrawal_model.get_by_id(cursor, withdrawal_id)
        if not w:
            return jsonify({"error": "Withdrawal not found"}), 404
        if w["status"] != "pending":
            return jsonify({"error": f"Withdrawal is already {w['status']}"}), 409

        withdrawal_model.set_status(cursor, withdrawal_id, "approved")
        _log_admin_action(cursor, g.current_user_id, f"Approved withdrawal #{withdrawal_id}", "withdrawal", withdrawal_id)
        cursor.execute(
            "INSERT INTO notifications (user_id, title, message) VALUES (%s,%s,%s)",
            (w["user_id"], "Withdrawal approved", f"Your withdrawal of KES {w['amount']:.2f} has been approved."),
        )
        conn.commit()
        return jsonify({"message": "Withdrawal approved"})


@admin.route("/withdrawals/<int:withdrawal_id>/reject", methods=["PUT"])
@admin_required
def reject_withdrawal(withdrawal_id):
    data = request.get_json(silent=True) or {}
    note = (data.get("reason") or "").strip() or None

    with get_db() as (conn, cursor):
        w = withdrawal_model.get_by_id(cursor, withdrawal_id)
        if not w:
            return jsonify({"error": "Withdrawal not found"}), 404
        if w["status"] != "pending":
            return jsonify({"error": f"Withdrawal is already {w['status']}"}), 409

        withdrawal_model.set_status(cursor, withdrawal_id, "rejected", note)
        # Refund the reserved amount back to the user's wallet.
        user_model.credit_wallet(cursor, w["user_id"], w["amount"])
        cursor.execute(
            "INSERT INTO transactions (user_id, type, amount, description) VALUES (%s,%s,%s,%s)",
            (w["user_id"], "reversal", w["amount"], f"Withdrawal #{withdrawal_id} rejected — funds returned"),
        )
        _log_admin_action(cursor, g.current_user_id, f"Rejected withdrawal #{withdrawal_id}", "withdrawal", withdrawal_id)
        cursor.execute(
            "INSERT INTO notifications (user_id, title, message) VALUES (%s,%s,%s)",
            (w["user_id"], "Withdrawal rejected",
             f"Your withdrawal of KES {w['amount']:.2f} was rejected. Funds were returned to your wallet." +
             (f" Reason: {note}" if note else "")),
        )
        conn.commit()
        return jsonify({"message": "Withdrawal rejected and funds returned"})


# ======================================
# VIEW ENROLLMENTS AWAITING PAYMENT VERIFICATION
# ======================================
@admin.route("/enrollments", methods=["GET"])
@admin_required
def list_enrollments():
    status = request.args.get("status", "unpaid")
    with get_db() as (conn, cursor):
        cursor.execute(
            """
            SELECT e.id, e.amount_due, e.amount_paid, e.payment_status, e.created_at,
                   s.fullname AS student_name, s.email AS student_email,
                   c.name AS course_name,
                   r.fullname AS referred_by_name
            FROM enrollments e
            JOIN users s ON e.student_id = s.id
            JOIN courses c ON e.course_id = c.id
            LEFT JOIN users r ON e.referred_by = r.id
            WHERE e.payment_status = %s
            ORDER BY e.created_at DESC
            """,
            (status,),
        )
        return jsonify(cursor.fetchall())


# ======================================
# VERIFY TUITION PAYMENT
# This is the ONLY place a referral commission can be created.
# Admin/finance staff confirm that real tuition money has been
# received (e.g. from an M-Pesa statement or bank deposit slip)
# before any commission is credited to a referrer's wallet.
# ======================================
@admin.route("/enrollments/<int:enrollment_id>/verify-payment", methods=["PUT"])
@admin_required
def verify_enrollment_payment(enrollment_id):
    data = request.get_json(silent=True) or {}
    try:
        amount_paid = float(data.get("amount_paid", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid amount_paid"}), 400

    if amount_paid <= 0:
        return jsonify({"error": "amount_paid must be greater than zero"}), 400

    with get_db() as (conn, cursor):
        cursor.execute("SELECT * FROM enrollments WHERE id=%s", (enrollment_id,))
        enrollment = cursor.fetchone()
        if not enrollment:
            return jsonify({"error": "Enrollment not found"}), 404

        new_total_paid = float(enrollment["amount_paid"]) + amount_paid
        amount_due = float(enrollment["amount_due"])
        new_status = "paid" if new_total_paid >= amount_due else "partial"

        cursor.execute(
            """
            UPDATE enrollments
            SET amount_paid=%s, payment_status=%s, verified_by_admin=%s
            WHERE id=%s
            """,
            (new_total_paid, new_status, g.current_user_id, enrollment_id),
        )

        commission_created = False
        commission_amount = 0

        # Award commission once, only when the enrollment is fully paid,
        # only if there is a referrer, and only if we haven't already
        # awarded it for this enrollment.
        if new_status == "paid" and enrollment["referred_by"] and not enrollment["commission_awarded"]:
            commission_amount = round(amount_due * Config.COMMISSION_RATE, 2)

            referral_model.create_commission(
                cursor, enrollment["referred_by"], enrollment["student_id"], enrollment_id, commission_amount
            )
            wallet_model.credit(
                cursor, enrollment["referred_by"], commission_amount,
                f"Referral commission for enrollment #{enrollment_id}"
            )
            cursor.execute(
                "UPDATE enrollments SET commission_awarded=TRUE WHERE id=%s", (enrollment_id,)
            )
            cursor.execute(
                "INSERT INTO notifications (user_id, title, message) VALUES (%s,%s,%s)",
                (enrollment["referred_by"], "Commission received",
                 f"You earned KES {commission_amount:.2f} because your referral completed tuition payment."),
            )
            commission_created = True

        _log_admin_action(
            cursor, g.current_user_id,
            f"Verified payment of KES {amount_paid:.2f} for enrollment #{enrollment_id}",
            "enrollment", enrollment_id,
        )

        cursor.execute(
            "INSERT INTO notifications (user_id, title, message) VALUES (%s,%s,%s)",
            (enrollment["student_id"], "Payment received",
             f"We've recorded your payment of KES {amount_paid:.2f}. Status: {new_status}."),
        )

        conn.commit()

        return jsonify({
            "message": "Payment verified",
            "payment_status": new_status,
            "total_paid": new_total_paid,
            "commission_created": commission_created,
            "commission_amount": commission_amount,
        })


# ======================================
# MANAGE COURSES
# ======================================
@admin.route("/courses", methods=["POST"])
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

    with get_db() as (conn, cursor):
        cursor.execute(
            "INSERT INTO courses (name, category, tuition_fee, description) VALUES (%s,%s,%s,%s)",
            (data["name"], data["category"], tuition_fee, data.get("description")),
        )
        conn.commit()
        return jsonify({"message": "Course created", "course_id": cursor.lastrowid}), 201
