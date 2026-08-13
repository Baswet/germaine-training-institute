"""
AdminUser — Step 2 §28 "Table: admin_users" (Phase 2).

Minimum viable: a single implicit admin role for Phase 1/2, per
STEP-2-DATABASE-ARCHITECTURE.md §18/§19. No `role`/`permissions` field
is included — every admin_users row can do everything the dashboard
offers, by design, until a real multi-tier need appears.

password_hash is written/verified via app/utils/security.py
(Werkzeug-style generate_password_hash/check_password_hash) and is
never included in any API response, ever.
"""

from datetime import datetime, timezone

from app.extensions import db


class AdminUser(db.Model):
    __tablename__ = "admin_users"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)

    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)  # never plaintext

    is_active = db.Column(db.Boolean, nullable=False, default=True)
    last_login_at = db.Column(db.DateTime(timezone=True), nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<AdminUser id={self.id} email={self.email!r}>"
