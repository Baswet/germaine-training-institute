"""
Small reusable helpers for the EarnCash blueprint, ported unchanged in
behavior from build10/EarnCash/backend/utils/helpers.py.
"""

import os
import re
import secrets
import string

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def generate_referral_code(length=8):
    alphabet = string.ascii_uppercase + string.digits
    return "EC" + "".join(secrets.choice(alphabet) for _ in range(length))


def commission_rate() -> float:
    """Same EARNCASH_COMMISSION_RATE env var (default 10%) already used by
    the enrollment-based verify-payment flow in
    app/blueprints/earncash/admin_routes.py, factored out here so the
    GTI-application-based commission flow (admin_service.py) uses the
    identical real rate rather than a second, possibly-divergent number.
    That existing route's own private _commission_rate() is left
    untouched — this is purely an additive, reusable copy of the same
    logic."""
    try:
        return float(os.environ.get("EARNCASH_COMMISSION_RATE", "0.10"))
    except (TypeError, ValueError):
        return 0.10


def is_valid_email(email):
    return bool(email) and bool(EMAIL_RE.match(email))


def is_valid_password(password):
    return bool(password) and len(password) >= 8


def require_fields(data, fields):
    """Returns a list of missing/empty required fields."""
    missing = []
    for field in fields:
        value = data.get(field) if data else None
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(field)
    return missing
