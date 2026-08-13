"""
Minimal CSRF protection for the session-authenticated admin portal
(Step 7). No new dependency is added (no Flask-WTF) — this uses only
`secrets` (stdlib) and the existing signed Flask session, which is
already relied on for admin login state.

Pattern: a random token is generated once per session and stored in
`session["csrf_token"]`. Every admin form embeds it as a hidden field
(see templates/admin/_csrf.html). Every state-changing POST route
calls `validate_csrf(request.form.get("csrf_token"))` before touching
the database, and aborts with 403 on mismatch — consistent with Step 2
§22/Step 7 §14V's requirement that CSRF not be skipped for convenience.
"""

import secrets

from flask import session


def get_csrf_token() -> str:
    """Return the current session's CSRF token, creating one if absent."""
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


def validate_csrf(submitted_token: str | None) -> bool:
    """Constant-time comparison against the session's token."""
    expected = session.get("csrf_token")
    if not expected or not submitted_token:
        return False
    return secrets.compare_digest(expected, submitted_token)
