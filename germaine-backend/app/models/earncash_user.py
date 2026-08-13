"""
EarnCashUser — "Table: earncash_users".

EarnCash is Germaine's student referral/affiliate platform (previously
a fully separate Flask+MySQL app under build10/EarnCash/backend/,
now integrated as a blueprint against this same PostgreSQL database).
All EarnCash tables are prefixed `earncash_` so they can never collide
with any existing or future Germaine table name, even though today's
19 Germaine tables (schools, admin_users, applications, etc.) already
share no names with EarnCash's original schema.

This mirrors build10/EarnCash/database/earncash.sql's `users` table
1:1 in meaning: `role`/`status` were MySQL ENUM columns there — stored
here as plain VARCHAR + CHECK constraint, matching how every other
enum-like column in this codebase is already represented (see
Application.status, MediaAsset.status, etc.) rather than a native
Postgres ENUM type, so it stays consistent with the rest of the schema.

password_hash is Werkzeug pbkdf2:sha256, exactly as EarnCash's own
routes already produce it — never included in any API response.
"""

from datetime import datetime, timezone

from app.extensions import db


class EarnCashUser(db.Model):
    __tablename__ = "earncash_users"
    __table_args__ = (
        db.CheckConstraint("role IN ('user', 'admin')", name="ck_earncash_users_role"),
        db.CheckConstraint("status IN ('active', 'suspended')", name="ck_earncash_users_status"),
    )

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)

    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(30), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)

    referral_code = db.Column(db.String(20), nullable=False, unique=True)
    referred_by = db.Column(db.BigInteger, db.ForeignKey("earncash_users.id", ondelete="SET NULL"), nullable=True)

    wallet = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    role = db.Column(db.String(20), nullable=False, default="user")
    status = db.Column(db.String(20), nullable=False, default="active")

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    referrer = db.relationship("EarnCashUser", remote_side=[id], backref="referred_users")

    def __repr__(self):
        return f"<EarnCashUser id={self.id} email={self.email!r}>"

    def to_public_dict(self):
        """Matches the shape EarnCash's original get_public_profile() SELECT returned."""
        return {
            "id": self.id,
            "fullname": self.fullname,
            "email": self.email,
            "phone": self.phone,
            "wallet": str(self.wallet),
            "referral_code": self.referral_code,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
