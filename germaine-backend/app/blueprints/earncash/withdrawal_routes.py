"""
EarnCash withdrawal routes — ported from
build10/EarnCash/backend/routes/withdrawals.py.

Registered at /api/earncash/withdrawals/... (see app/__init__.py).
"""

import os

from flask import request, jsonify, g, current_app

from app.extensions import db
from app.models import EarnCashUser, EarnCashWithdrawal, EarnCashTransaction, EarnCashNotification
from app.utils.earncash_jwt import token_required
from app.blueprints.earncash import earncash_bp

VALID_METHODS = {"mpesa", "bank", "airtel_money"}


def _min_withdrawal_amount():
    try:
        return float(os.environ.get("EARNCASH_MIN_WITHDRAWAL_AMOUNT", "500"))
    except (TypeError, ValueError):
        return 500.0


# ======================================
# CREATE WITHDRAWAL REQUEST
# ======================================
@earncash_bp.route("/withdrawals/request", methods=["POST"])
@token_required
def create_withdrawal():
    data = request.get_json(silent=True) or {}
    user_id = g.earncash_user_id

    try:
        amount = float(data.get("amount", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid amount"}), 400

    method = data.get("method")
    details = (data.get("details") or "").strip()
    min_amount = _min_withdrawal_amount()

    if method not in VALID_METHODS:
        return jsonify({"error": "method must be one of: mpesa, bank, airtel_money"}), 400
    if not details:
        return jsonify({"error": "Account details are required"}), 400
    if amount < min_amount:
        return jsonify({"error": f"Minimum withdrawal amount is KES {min_amount:.2f}"}), 400

    user = db.session.get(EarnCashUser, user_id)
    if float(user.wallet) < amount:
        return jsonify({"error": "Insufficient wallet balance"}), 400

    try:
        # Reserve the funds immediately so the same balance can't be
        # withdrawn twice while the request is pending admin approval.
        if float(user.wallet) < amount:
            db.session.rollback()
            return jsonify({"error": "Insufficient wallet balance"}), 400
        user.wallet = float(user.wallet) - amount

        withdrawal = EarnCashWithdrawal(user_id=user_id, amount=amount, method=method, account_details=details)
        db.session.add(withdrawal)
        db.session.flush()  # get withdrawal.id before commit

        db.session.add(EarnCashTransaction(
            user_id=user_id, type="withdrawal", amount=-amount,
            description=f"Withdrawal request #{withdrawal.id} submitted",
        ))
        db.session.add(EarnCashNotification(
            user_id=user_id, title="Withdrawal submitted",
            message=f"Your withdrawal request for KES {amount:.2f} is pending admin approval.",
        ))
        db.session.commit()

        return jsonify({"message": "Withdrawal request submitted", "withdrawal_id": withdrawal.id}), 201
    except Exception:
        db.session.rollback()
        # Log the real exception server-side only — never send stack traces
        # or raw exception text to the client (Phase 4 fix).
        current_app.logger.exception("EarnCash withdrawal request failed")
        return jsonify({"error": "Withdrawal request failed. Please try again."}), 500


# ======================================
# WITHDRAWAL HISTORY
# ======================================
@earncash_bp.route("/withdrawals/history/<int:user_id>", methods=["GET"])
@token_required
def history(user_id):
    if g.earncash_user_role != "admin" and g.earncash_user_id != user_id:
        return jsonify({"error": "You may only access your own data"}), 403

    records = (
        EarnCashWithdrawal.query.filter_by(user_id=user_id)
        .order_by(EarnCashWithdrawal.created_at.desc())
        .all()
    )
    return jsonify([w.to_dict() for w in records])
