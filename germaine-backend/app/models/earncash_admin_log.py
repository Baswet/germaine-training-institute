"""
EarnCashAdminLog — "Table: earncash_admin_logs".

Mirrors build10/EarnCash/database/earncash.sql's `admin_logs` table.
"""

from datetime import datetime, timezone

from app.extensions import db


class EarnCashAdminLog(db.Model):
    __tablename__ = "earncash_admin_logs"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)

    admin_id = db.Column(db.BigInteger, db.ForeignKey("earncash_users.id", ondelete="CASCADE"), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    target_type = db.Column(db.String(50), nullable=True)
    target_id = db.Column(db.BigInteger, nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<EarnCashAdminLog id={self.id} admin_id={self.admin_id} action={self.action!r}>"
