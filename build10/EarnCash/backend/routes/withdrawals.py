from flask import Blueprint, request, jsonify, g

from database import get_db
from models import user as user_model, withdrawal as withdrawal_model
from utils.security import token_required
from config import Config

withdrawals = Blueprint("withdrawals", __name__)

VALID_METHODS = {"mpesa", "bank", "airtel_money"}


# ======================================
# CREATE WITHDRAWAL REQUEST
# ======================================
@withdrawals.route("/request", methods=["POST"])
@token_required
def create_withdrawal():
    data = request.get_json(silent=True) or {}
    user_id = g.current_user_id

    try:
        amount = float(data.get("amount", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid amount"}), 400

    method = data.get("method")
    details = (data.get("details") or "").strip()

    if method not in VALID_METHODS:
        return jsonify({"error": "method must be one of: mpesa, bank, airtel_money"}), 400
    if not details:
        return jsonify({"error": "Account details are required"}), 400
    if amount < Config.MIN_WITHDRAWAL_AMOUNT:
        return jsonify({"error": f"Minimum withdrawal amount is KES {Config.MIN_WITHDRAWAL_AMOUNT:.2f}"}), 400

    with get_db() as (conn, cursor):
        user = user_model.find_by_id(cursor, user_id)
        if float(user["wallet"]) < amount:
            return jsonify({"error": "Insufficient wallet balance"}), 400

        try:
            # Reserve the funds immediately so the same balance can't be
            # withdrawn twice while the request is pending admin approval.
            debited = user_model.debit_wallet(cursor, user_id, amount)
            if not debited:
                conn.rollback()
                return jsonify({"error": "Insufficient wallet balance"}), 400

            withdrawal_id = withdrawal_model.create_withdrawal(cursor, user_id, amount, method, details)

            cursor.execute(
                "INSERT INTO transactions (user_id, type, amount, description) VALUES (%s,%s,%s,%s)",
                (user_id, "withdrawal", -amount, f"Withdrawal request #{withdrawal_id} submitted"),
            )
            cursor.execute(
                "INSERT INTO notifications (user_id, title, message) VALUES (%s,%s,%s)",
                (user_id, "Withdrawal submitted",
                 f"Your withdrawal request for KES {amount:.2f} is pending admin approval."),
            )
            conn.commit()

            return jsonify({"message": "Withdrawal request submitted", "withdrawal_id": withdrawal_id}), 201
        except Exception as e:
            conn.rollback()
            return jsonify({"error": "Withdrawal failed", "details": str(e)}), 500


# ======================================
# WITHDRAWAL HISTORY
# ======================================
@withdrawals.route("/history/<int:user_id>", methods=["GET"])
@token_required
def history(user_id):
    if g.current_user_role != "admin" and g.current_user_id != user_id:
        return jsonify({"error": "You may only access your own data"}), 403

    with get_db() as (conn, cursor):
        records = withdrawal_model.get_history(cursor, user_id)
        return jsonify(records)
