"""
Admin session-authentication helpers (Step 7).

Session-cookie based (Flask's own signed session, via SECRET_KEY) —
no new auth dependency is introduced. `admin_required` protects every
admin page/route except the login page itself; `current_admin()` loads
the authenticated AdminUser row (or None) for the current request.

Security notes (Step 7 §14U):
  - The session cookie is HttpOnly + SameSite=Lax by default (see
    app/config.py) so it is never readable from admin-portal JS and is
    not sent cross-site.
  - No password, password hash, or session secret is ever stored in
    the session payload itself — only the admin's integer id.
  - `admin_required` returns a 401/redirect rather than leaking whether
    a route exists to an unauthenticated caller in any way beyond the
    normal login redirect.
"""

from functools import wraps

from flask import session, redirect, url_for, request, abort

from app.extensions import db
from app.models import AdminUser


def current_admin():
    """Return the logged-in AdminUser, or None if not authenticated / no longer active."""
    admin_id = session.get("admin_user_id")
    if not admin_id:
        return None
    admin = db.session.get(AdminUser, admin_id)
    if admin is None or not admin.is_active:
        return None
    return admin


def admin_required(view_func):
    """Redirect unauthenticated requests to the login page; never render protected content."""

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        admin = current_admin()
        if admin is None:
            session.pop("admin_user_id", None)
            if request.path.startswith("/admin/api/"):
                abort(401)
            return redirect(url_for("admin.login", next=request.path))
        return view_func(*args, **kwargs)

    return wrapped
