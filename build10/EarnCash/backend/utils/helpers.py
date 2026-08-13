"""
Small reusable helpers shared across routes.
"""

import re
import secrets
import string

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def generate_referral_code(length=8):
    alphabet = string.ascii_uppercase + string.digits
    return "EC" + "".join(secrets.choice(alphabet) for _ in range(length))


def is_valid_email(email):
    return bool(email) and bool(EMAIL_RE.match(email))


def is_valid_password(password):
    # Keep this simple and honest with the user about requirements.
    return bool(password) and len(password) >= 8


def require_fields(data, fields):
    """Returns a list of missing/empty required fields."""
    missing = []
    for field in fields:
        value = data.get(field) if data else None
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(field)
    return missing
