"""
EarnCash referral routes — ported from
build10/EarnCash/backend/routes/referrals.py.

Registered at /api/earncash/referrals/... (see app/__init__.py).
"""

from flask import jsonify, g

from app.extensions import db
from app.models import EarnCashUser, EarnCashReferralCommission, EarnCashEnrollment, EarnCashCourse
from app.utils.earncash_jwt import owner_or_admin_required, token_required
from app.blueprints.earncash import earncash_bp


# ======================================
# MY REFERRAL CODE + SHAREABLE LINK
# ======================================
@earncash_bp.route("/referrals/code", methods=["GET"])
@token_required
def my_referral_code():
    user = db.session.get(EarnCashUser, g.earncash_user_id)
    return jsonify({"referral_code": user.referral_code})


# ======================================
# PEOPLE I'VE REFERRED
# ======================================
@earncash_bp.route("/referrals/<int:user_id>", methods=["GET"])
@owner_or_admin_required
def get_referrals(user_id):
    referred_users = (
        EarnCashUser.query.filter_by(referred_by=user_id)
        .order_by(EarnCashUser.created_at.desc())
        .all()
    )
    return jsonify([
        {"id": u.id, "fullname": u.fullname, "email": u.email,
         "created_at": u.created_at.isoformat() if u.created_at else None}
        for u in referred_users
    ])


# ======================================
# MY COMMISSION HISTORY
# (only ever created after a verified tuition payment — see
#  admin_routes.py::verify_enrollment_payment)
# ======================================
@earncash_bp.route("/referrals/<int:user_id>/commissions", methods=["GET"])
@owner_or_admin_required
def get_commissions(user_id):
    rows = (
        db.session.query(EarnCashReferralCommission, EarnCashUser, EarnCashCourse)
        .join(EarnCashUser, EarnCashReferralCommission.referred_user_id == EarnCashUser.id)
        .join(EarnCashEnrollment, EarnCashReferralCommission.enrollment_id == EarnCashEnrollment.id)
        .join(EarnCashCourse, EarnCashEnrollment.course_id == EarnCashCourse.id)
        .filter(EarnCashReferralCommission.referrer_id == user_id)
        .order_by(EarnCashReferralCommission.created_at.desc())
        .all()
    )
    return jsonify([
        {
            "id": rc.id,
            "referred_user_id": rc.referred_user_id,
            "commission_amount": str(rc.commission_amount),
            "status": rc.status,
            "created_at": rc.created_at.isoformat() if rc.created_at else None,
            "referred_user_name": u.fullname,
            "course_name": c.name,
        }
        for rc, u, c in rows
    ])
