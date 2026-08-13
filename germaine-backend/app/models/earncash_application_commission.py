"""
EarnCashApplicationCommission — "Table: earncash_application_commissions".

The EarnFastCash <-> Germaine Training Institute referral bridge.

EarnCash's original commission model (EarnCashReferralCommission) is
tied to `earncash_enrollments` — EarnCash's own internal, self-contained
courses/enrollments system (see earncash_enrollment.py), which is a
completely separate product from the real GTI academic/AI-Bootcamp
`applications` table. That existing table and its unique-per-enrollment
constraint are left completely untouched by this file.

This is a new, additive-only table for the other real flow the site
supports: a visitor arrives via an EarnFastCash referral link, browses
into the real GTI website, and submits a real `Application` (scholarship
or AI Bootcamp programme_inquiry). One row here is created ONLY when:
  1. that application has a real referred_by_earncash_user_id (a valid
     referral_code was supplied at submission time), AND
  2. a GTI admin has confirmed real tuition payment on that application
     (application.tuition_confirmed_at is set), AND
  3. the application's programme_mode has a real, published fee_amount
     (never invented — applications with no real fee, e.g. most academic
     scholarship applications, simply never generate a commission here).

Uses the exact same EARNCASH_COMMISSION_RATE environment variable and
wallet/transaction/notification crediting mechanism as the existing
enrollment-based flow (see app/utils/earncash_helpers.py's
commission_rate() and app/services/admin_service.py's
confirm_application_tuition()), so a referral credited through either
flow behaves identically on the EarnFastCash side.
"""

from datetime import datetime, timezone

from app.extensions import db


class EarnCashApplicationCommission(db.Model):
    __tablename__ = "earncash_application_commissions"
    __table_args__ = (
        db.CheckConstraint(
            "status IN ('approved', 'reversed')",
            name="ck_earncash_application_commissions_status",
        ),
    )

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)

    referrer_id = db.Column(db.BigInteger, db.ForeignKey("earncash_users.id", ondelete="CASCADE"), nullable=False)
    application_id = db.Column(
        db.BigInteger, db.ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    commission_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="approved")

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    referrer = db.relationship("EarnCashUser", foreign_keys=[referrer_id])
    application = db.relationship("Application")

    def __repr__(self):
        return f"<EarnCashApplicationCommission id={self.id} referrer_id={self.referrer_id}>"
