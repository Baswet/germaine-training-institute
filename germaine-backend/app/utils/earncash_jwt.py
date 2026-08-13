"""
EarnCash JWT auth: token issuing + route decorators.

EarnCash is bearer-token authenticated (JWT via PyJWT), ported as-is
from build10/EarnCash/backend/utils/security.py — behavior is
unchanged, only the config source moved (EARNCASH_JWT_SECRET /
EARNCASH_JWT_EXP_HOURS, read from this app's environment instead of
EarnCash's own standalone Config class).

Deliberately separate from app/utils/auth.py, which is the existing
Germaine staff admin portal's session-cookie auth (Step 7). The two
systems never interact: EarnCash's own users (earncash_users table,
role='user'/'admin') carry a JWT; Germaine's admin_users table still
uses server-side sessions via app/utils/auth.py. Neither can be used
to authenticate against the other.
"""

import os
from functools import wraps
import datetime

import jwt
from flask import request, jsonify, g


def _jwt_secret():
    # Falls back to the app's own SECRET_KEY if EARNCASH_JWT_SECRET isn't
    # set, so this works out of the box in development without requiring
    # a second secret — but a dedicated EARNCASH_JWT_SECRET is recommended
    # for production so rotating one doesn't invalidate the other.
    return os.environ.get("EARNCASH_JWT_SECRET") or os.environ.get("SECRET_KEY", "")


def _jwt_exp_hours():
    try:
        return int(os.environ.get("EARNCASH_JWT_EXP_HOURS", "24"))
    except (TypeError, ValueError):
        return 24


def issue_token(user_id, role="user"):
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": now + datetime.timedelta(hours=_jwt_exp_hours()),
        "iat": now,
    }
    return jwt.encode(payload, _jwt_secret(), algorithm="HS256")


def _extract_token():
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header.split(" ", 1)[1].strip()
    return None


def _decode_or_error():
    token = _extract_token()
    if not token:
        return None, (jsonify({"error": "Authentication token is missing"}), 401)
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=["HS256"])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, (jsonify({"error": "Session expired, please log in again"}), 401)
    except jwt.InvalidTokenError:
        return None, (jsonify({"error": "Invalid authentication token"}), 401)


def token_required(f):
    """Requires a valid JWT for any logged-in EarnCash user (or admin)."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        payload, err = _decode_or_error()
        if err:
            return err
        g.earncash_user_id = payload["user_id"]
        g.earncash_user_role = payload.get("role", "user")
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    """Requires a valid JWT belonging to an EarnCash admin account."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        payload, err = _decode_or_error()
        if err:
            return err
        if payload.get("role") != "admin":
            return jsonify({"error": "Admin privileges required"}), 403
        g.earncash_user_id = payload["user_id"]
        g.earncash_user_role = "admin"
        return f(*args, **kwargs)
    return wrapper


def owner_or_admin_required(f):
    """
    For routes like /users/profile/<user_id>: allows the token owner to
    access their own resource, or an EarnCash admin to access anyone's.
    Expects the route to have a `user_id` kwarg.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        payload, err = _decode_or_error()
        if err:
            return err
        requested_id = kwargs.get("user_id")
        if payload.get("role") != "admin" and payload["user_id"] != requested_id:
            return jsonify({"error": "You may only access your own data"}), 403
        g.earncash_user_id = payload["user_id"]
        g.earncash_user_role = payload.get("role", "user")
        return f(*args, **kwargs)
    return wrapper
