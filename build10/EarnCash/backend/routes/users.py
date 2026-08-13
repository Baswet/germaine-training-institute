from flask import Blueprint, jsonify, request, g
from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db
from models import user as user_model, wallet as wallet_model
from utils.security import owner_or_admin_required, token_required
from utils.helpers import is_valid_password

users = Blueprint("users", __name__)


# ======================================
# GET PROFILE
# ======================================
@users.route("/profile/<int:user_id>", methods=["GET"])
@owner_or_admin_required
def profile(user_id):
    with get_db() as (conn, cursor):
        user = user_model.get_public_profile(cursor, user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user)


# ======================================
# DASHBOARD STATISTICS
# ======================================
@users.route("/stats/<int:user_id>", methods=["GET"])
@owner_or_admin_required
def stats(user_id):
    with get_db() as (conn, cursor):
        user = user_model.find_by_id(cursor, user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        cursor.execute(
            "SELECT COUNT(*) AS total FROM users WHERE referred_by=%s", (user_id,)
        )
        referral_count = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COALESCE(SUM(commission_amount),0) AS total FROM referral_commissions WHERE referrer_id=%s",
            (user_id,),
        )
        total_commission = cursor.fetchone()["total"]

        return jsonify({
            "wallet_balance": user["wallet"],
            "total_referrals": referral_count,
            "total_commission_earned": total_commission,
            "referral_code": user["referral_code"],
        })


# ======================================
# UPDATE PROFILE (name, phone only — email/wallet are not editable here)
# ======================================
@users.route("/profile/<int:user_id>", methods=["PUT"])
@owner_or_admin_required
def update_profile(user_id):
    data = request.get_json(silent=True) or {}
    fullname = (data.get("fullname") or "").strip()
    phone = (data.get("phone") or "").strip()

    if not fullname:
        return jsonify({"error": "Full name is required"}), 400

    with get_db() as (conn, cursor):
        cursor.execute(
            "UPDATE users SET fullname=%s, phone=%s WHERE id=%s",
            (fullname, phone or None, user_id),
        )
        conn.commit()
        return jsonify({"message": "Profile updated successfully"})


# ======================================
# CHANGE PASSWORD
# ======================================
@users.route("/password/<int:user_id>", methods=["PUT"])
@token_required
def change_password(user_id):
    if g.current_user_id != user_id:
        return jsonify({"error": "You may only change your own password"}), 403

    data = request.get_json(silent=True) or {}
    current_password = data.get("current_password") or ""
    new_password = data.get("new_password") or ""

    if not is_valid_password(new_password):
        return jsonify({"error": "New password must be at least 8 characters"}), 400

    with get_db() as (conn, cursor):
        user = user_model.find_by_id(cursor, user_id)
        if not user or not check_password_hash(user["password_hash"], current_password):
            return jsonify({"error": "Current password is incorrect"}), 401

        new_hash = generate_password_hash(new_password, method="pbkdf2:sha256")
        cursor.execute("UPDATE users SET password_hash=%s WHERE id=%s", (new_hash, user_id))
        conn.commit()
        return jsonify({"message": "Password changed successfully"})


# ======================================
# TRANSACTION HISTORY
# ======================================
@users.route("/transactions/<int:user_id>", methods=["GET"])
@owner_or_admin_required
def transactions(user_id):
    with get_db() as (conn, cursor):
        records = wallet_model.get_transactions(cursor, user_id)
        return jsonify(records)
