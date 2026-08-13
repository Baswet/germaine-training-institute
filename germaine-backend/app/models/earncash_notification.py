"""
EarnCashNotification — "Table: earncash_notifications".

Mirrors build10/EarnCash/database/earncash.sql's `notifications` table.
"""

from datetime import datetime, timezone

from app.extensions import db


class EarnCashNotification(db.Model):
    __tablename__ = "earncash_notifications"
    __table_args__ = (
        db.CheckConstraint("status IN ('unread', 'read')", name="ck_earncash_notifications_status"),
    )

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)

    user_id = db.Column(db.BigInteger, db.ForeignKey("earncash_users.id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="unread")

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("EarnCashUser")

    def __repr__(self):
        return f"<EarnCashNotification id={self.id} user_id={self.user_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "message": self.message,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
