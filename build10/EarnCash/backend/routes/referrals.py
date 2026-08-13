from flask import Blueprint, jsonify, g

from database import get_db
from models import user as user_model, referral as referral_model
from utils.security import owner_or_admin_required, token_required

referrals = Blueprint("referrals", __name__)


# ======================================
# MY REFERRAL CODE + SHAREABLE LINK
# ======================================
@referrals.route("/code", methods=["GET"])
@token_required
def my_referral_code():
    with get_db() as (conn, cursor):
        user = user_model.find_by_id(cursor, g.current_user_id)
        return jsonify({"referral_code": user["referral_code"]})


# ======================================
# PEOPLE I'VE REFERRED
# ======================================
@referrals.route("/<int:user_id>", methods=["GET"])
@owner_or_admin_required
def get_referrals(user_id):
    with get_db() as (conn, cursor):
        referred_users = referral_model.get_referred_users(cursor, user_id)
        return jsonify(referred_users)


# ======================================
# MY COMMISSION HISTORY
# (only ever created after a verified tuition payment — see
#  routes/admin.py::verify_enrollment_payment)
# ======================================
@referrals.route("/<int:user_id>/commissions", methods=["GET"])
@owner_or_admin_required
def get_commissions(user_id):
    with get_db() as (conn, cursor):
        commissions = referral_model.get_commissions_for_referrer(cursor, user_id)
        return jsonify(commissions)
