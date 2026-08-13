"""
Auth helpers: JWT creation/verification and route decorators.
"""

from functools import wraps
import datetime
import jwt
from flask import request, jsonify, g
from config import Config


def issue_token(user_id, role="user"):
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": now + datetime.timedelta(hours=Config.JWT_EXP_HOURS),
        "iat": now,
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")


def _extract_token():
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header.split(" ", 1)[1].strip()
    return None


def token_required(f):
    """Requires a valid JWT for any logged-in user (or admin)."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = _extract_token()
        if not token:
            return jsonify({"error": "Authentication token is missing"}), 401
        try:
            payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Session expired, please log in again"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid authentication token"}), 401

        g.current_user_id = payload["user_id"]
        g.current_user_role = payload.get("role", "user")
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    """Requires a valid JWT belonging to an admin account."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = _extract_token()
        if not token:
            return jsonify({"error": "Authentication token is missing"}), 401
        try:
            payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Session expired, please log in again"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid authentication token"}), 401

        if payload.get("role") != "admin":
            return jsonify({"error": "Admin privileges required"}), 403

        g.current_user_id = payload["user_id"]
        g.current_user_role = "admin"
        return f(*args, **kwargs)
    return wrapper


def owner_or_admin_required(f):
    """
    For routes like /users/profile/<user_id>: allows the token owner
    to access their own resource, or an admin to access anyone's.
    Expects the route to have a `user_id` kwarg.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = _extract_token()
        if not token:
            return jsonify({"error": "Authentication token is missing"}), 401
        try:
            payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Session expired, please log in again"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid authentication token"}), 401

        requested_id = kwargs.get("user_id")
        if payload.get("role") != "admin" and payload["user_id"] != requested_id:
            return jsonify({"error": "You may only access your own data"}), 403

        g.current_user_id = payload["user_id"]
        g.current_user_role = payload.get("role", "user")
        return f(*args, **kwargs)
    return wrapper
