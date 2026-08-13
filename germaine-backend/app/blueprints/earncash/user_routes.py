"""
EarnCash user/profile/dashboard routes — ported from
build10/EarnCash/backend/routes/users.py.

Registered at /api/earncash/users/... (see app/__init__.py).
"""

from flask import request, jsonify, g
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models import EarnCashUser, EarnCashReferralCommission, EarnCashTransaction
from app.utils.earncash_jwt import owner_or_admin_required, token_required
from app.utils.earncash_helpers import is_valid_password
from app.blueprints.earncash import earncash_bp


# ======================================
# GET PROFILE
# ======================================
@earncash_bp.route("/users/profile/<int:user_id>", methods=["GET"])
@owner_or_admin_required
def profile(user_id):
    user = db.session.get(EarnCashUser, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_public_dict())


# ======================================
# DASHBOARD STATISTICS
# ======================================
@earncash_bp.route("/users/stats/<int:user_id>", methods=["GET"])
@owner_or_admin_required
def stats(user_id):
    user = db.session.get(EarnCashUser, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    referral_count = EarnCashUser.query.filter_by(referred_by=user_id).count()

    total_commission = (
        db.session.query(db.func.coalesce(db.func.sum(EarnCashReferralCommission.commission_amount), 0))
        .filter(EarnCashReferralCommission.referrer_id == user_id)
        .scalar()
    )

    return jsonify({
        "wallet_balance": str(user.wallet),
        "total_referrals": referral_count,
        "total_commission_earned": str(total_commission),
        "referral_code": user.referral_code,
    })


# ======================================
# UPDATE PROFILE (name, phone only — email/wallet are not editable here)
# ======================================
@earncash_bp.route("/users/profile/<int:user_id>", methods=["PUT"])
@owner_or_admin_required
def update_profile(user_id):
    data = request.get_json(silent=True) or {}
    fullname = (data.get("fullname") or "").strip()
    phone = (data.get("phone") or "").strip()

    if not fullname:
        return jsonify({"error": "Full name is required"}), 400

    user = db.session.get(EarnCashUser, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.fullname = fullname
    user.phone = phone or None
    db.session.commit()
    return jsonify({"message": "Profile updated successfully"})


# ======================================
# CHANGE PASSWORD
# ======================================
@earncash_bp.route("/users/password/<int:user_id>", methods=["PUT"])
@token_required
def change_password(user_id):
    if g.earncash_user_id != user_id:
        return jsonify({"error": "You may only change your own password"}), 403

    data = request.get_json(silent=True) or {}
    current_password = data.get("current_password") or ""
    new_password = data.get("new_password") or ""

    if not is_valid_password(new_password):
        return jsonify({"error": "New password must be at least 8 characters"}), 400

    user = db.session.get(EarnCashUser, user_id)
    if not user or not check_password_hash(user.password_hash, current_password):
        return jsonify({"error": "Current password is incorrect"}), 401

    user.password_hash = generate_password_hash(new_password, method="pbkdf2:sha256")
    db.session.commit()
    return jsonify({"message": "Password changed successfully"})


# ======================================
# TRANSACTION HISTORY
# ======================================
@earncash_bp.route("/users/transactions/<int:user_id>", methods=["GET"])
@owner_or_admin_required
def transactions(user_id):
    records = (
        EarnCashTransaction.query.filter_by(user_id=user_id)
        .order_by(EarnCashTransaction.created_at.desc())
        .all()
    )
    return jsonify([t.to_dict() for t in records])
