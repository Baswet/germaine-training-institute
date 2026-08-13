"""
Password hashing utility for AdminUser.password_hash.

Uses Werkzeug's own PBKDF2-SHA256 implementation (already a Flask
dependency via Flask itself, so no new package is added to
requirements.txt for this). This module intentionally does NOT
implement login routes, sessions, or tokens — Step 3 scaffolds the
hashing utility only; a full auth flow is future work
(app/services/auth_service.py has the placeholder for that).
"""

from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(plain_password: str) -> str:
    """Return a salted PBKDF2-SHA256 hash. Never store the plain password."""
    return generate_password_hash(plain_password, method="pbkdf2:sha256")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Check a plain password against a stored hash. Never log either value."""
    return check_password_hash(password_hash, plain_password)
