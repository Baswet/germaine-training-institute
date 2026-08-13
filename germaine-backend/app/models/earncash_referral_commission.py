"""
EarnCashReferralCommission — "Table: earncash_referral_commissions".

Mirrors build10/EarnCash/database/earncash.sql's `referral_commissions`
table. One row per enrollment that actually paid — created ONLY from
app/blueprints/earncash/routes.py's admin verify-payment route, after
an admin confirms real tuition payment was received. Never created
from a signup or a user-facing endpoint.
"""

from datetime import datetime, timezone

from app.extensions import db


class EarnCashReferralCommission(db.Model):
    __tablename__ = "earncash_referral_commissions"
    __table_args__ = (
        db.CheckConstraint(
            "status IN ('approved', 'reversed')",
            name="ck_earncash_referral_commissions_status",
        ),
    )

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)

    referrer_id = db.Column(db.BigInteger, db.ForeignKey("earncash_users.id", ondelete="CASCADE"), nullable=False)
    referred_user_id = db.Column(db.BigInteger, db.ForeignKey("earncash_users.id", ondelete="CASCADE"), nullable=False)
    enrollment_id = db.Column(
        db.BigInteger, db.ForeignKey("earncash_enrollments.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    commission_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="approved")

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    referrer = db.relationship("EarnCashUser", foreign_keys=[referrer_id])
    referred_user = db.relationship("EarnCashUser", foreign_keys=[referred_user_id])
    enrollment = db.relationship("EarnCashEnrollment")

    def __repr__(self):
        return f"<EarnCashReferralCommission id={self.id} referrer_id={self.referrer_id}>"
