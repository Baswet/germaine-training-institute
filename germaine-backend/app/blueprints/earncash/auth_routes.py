"""
EarnCash auth routes — ported from
build10/EarnCash/backend/routes/auth.py, behavior unchanged, storage
moved from raw mysql.connector SQL to this app's SQLAlchemy session.

Registered at /api/earncash/auth/... (see app/__init__.py).
"""

from flask import request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.models import EarnCashUser
from app.utils.earncash_jwt import issue_token
from app.utils.earncash_helpers import generate_referral_code, is_valid_email, is_valid_password, require_fields
from app.blueprints.earncash import earncash_bp


# ======================================
# REGISTER USER
# ======================================
@earncash_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    missing = require_fields(data, ["fullname", "email", "password"])
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    fullname = data["fullname"].strip()
    email = data["email"].strip().lower()
    phone = (data.get("phone") or "").strip() or None
    password = data["password"]
    referral_code_used = (data.get("referral_code") or "").strip().upper() or None

    if not is_valid_email(email):
        return jsonify({"error": "Please enter a valid email address"}), 400
    if not is_valid_password(password):
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    if EarnCashUser.query.filter_by(email=email).first():
        return jsonify({"error": "An account with this email already exists"}), 409

    referred_by = None
    if referral_code_used:
        referrer = EarnCashUser.query.filter_by(referral_code=referral_code_used).first()
        if referrer:
            referred_by = referrer.id
        # If the code is invalid, silently ignore it rather than blocking
        # registration — the person can still sign up.

    password_hash = generate_password_hash(password, method="pbkdf2:sha256")
    new_code = generate_referral_code()
    # extremely unlikely, but guarantee uniqueness
    while EarnCashUser.query.filter_by(referral_code=new_code).first():
        new_code = generate_referral_code()

    try:
        user = EarnCashUser(
            fullname=fullname,
            email=email,
            phone=phone,
            password_hash=password_hash,
            referral_code=new_code,
            referred_by=referred_by,
        )
        db.session.add(user)
        db.session.commit()

        return jsonify({
            "message": "Account created successfully",
            "referral_code": new_code,
        }), 201
    except Exception:
        db.session.rollback()
        # Log the real exception server-side only — never send stack traces
        # or raw exception text (which can include DB/column detail) to
        # the client (Phase 4 fix).
        current_app.logger.exception("EarnCash registration failed")
        return jsonify({"error": "Registration failed. Please try again."}), 500


# ======================================
# LOGIN USER
# ======================================
@earncash_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    missing = require_fields(data, ["email", "password"])
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    email = data["email"].strip().lower()
    password = data["password"]

    try:
        user = EarnCashUser.query.filter_by(email=email).first()

        # Same generic error for "no such user" and "wrong password" so we
        # don't leak which emails are registered.
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid email or password"}), 401

        if user.status != "active":
            return jsonify({"error": "This account has been suspended"}), 403

        token = issue_token(user.id, role=user.role)

        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user.id,
                "name": user.fullname,
                "email": user.email,
                "role": user.role,
                "referral_code": user.referral_code,
            },
        })
    except Exception:
        current_app.logger.exception("EarnCash login failed")
        return jsonify({"error": "Login failed. Please try again."}), 500
