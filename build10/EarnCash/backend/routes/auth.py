from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db
from models import user as user_model
from utils.security import issue_token
from utils.helpers import generate_referral_code, is_valid_email, is_valid_password, require_fields

auth = Blueprint("auth", __name__)


# ======================================
# REGISTER USER
# ======================================
@auth.route("/register", methods=["POST"])
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

    try:
        with get_db() as (conn, cursor):
            if user_model.find_by_email(cursor, email):
                return jsonify({"error": "An account with this email already exists"}), 409

            referred_by = None
            if referral_code_used:
                referrer = user_model.find_by_referral_code(cursor, referral_code_used)
                if referrer:
                    referred_by = referrer["id"]
                # If the code is invalid, we silently ignore it rather than
                # blocking registration — the person can still sign up.

            password_hash = generate_password_hash(password, method="pbkdf2:sha256")
            new_code = generate_referral_code()
            # extremely unlikely, but guarantee uniqueness
            while user_model.find_by_referral_code(cursor, new_code):
                new_code = generate_referral_code()

            user_id = user_model.create_user(
                cursor, fullname, email, phone, password_hash, new_code, referred_by
            )
            conn.commit()

            return jsonify({
                "message": "Account created successfully",
                "referral_code": new_code,
            }), 201

    except Exception as e:
        return jsonify({"error": "Registration failed", "details": str(e)}), 500


# ======================================
# LOGIN USER
# ======================================
@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    missing = require_fields(data, ["email", "password"])
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    email = data["email"].strip().lower()
    password = data["password"]

    try:
        with get_db() as (conn, cursor):
            user = user_model.find_by_email(cursor, email)

            # Same generic error for "no such user" and "wrong password" so
            # we don't leak which emails are registered.
            if not user or not check_password_hash(user["password_hash"], password):
                return jsonify({"error": "Invalid email or password"}), 401

            if user["status"] != "active":
                return jsonify({"error": "This account has been suspended"}), 403

            token = issue_token(user["id"], role=user["role"])

            return jsonify({
                "message": "Login successful",
                "token": token,
                "user": {
                    "id": user["id"],
                    "name": user["fullname"],
                    "email": user["email"],
                    "role": user["role"],
                    "referral_code": user["referral_code"],
                },
            })
    except Exception as e:
        return jsonify({"error": "Login failed", "details": str(e)}), 500
