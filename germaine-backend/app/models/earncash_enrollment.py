"""
EarnCashEnrollment — "Table: earncash_enrollments".

Mirrors build10/EarnCash/database/earncash.sql's `enrollments` table.
The real, revenue-bearing event that funds commissions: a snapshot of
who referred the student (if anyone) is kept at enrollment time so a
later change to the student's `referred_by` can never retroactively
alter who a commission is owed to.
"""

from datetime import datetime, timezone

from app.extensions import db


class EarnCashEnrollment(db.Model):
    __tablename__ = "earncash_enrollments"
    __table_args__ = (
        db.CheckConstraint(
            "payment_status IN ('unpaid', 'partial', 'paid')",
            name="ck_earncash_enrollments_payment_status",
        ),
    )

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)

    student_id = db.Column(db.BigInteger, db.ForeignKey("earncash_users.id", ondelete="CASCADE"), nullable=False)
    course_id = db.Column(db.BigInteger, db.ForeignKey("earncash_courses.id"), nullable=False)
    referred_by = db.Column(db.BigInteger, db.ForeignKey("earncash_users.id", ondelete="SET NULL"), nullable=True)

    amount_due = db.Column(db.Numeric(10, 2), nullable=False)
    amount_paid = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    payment_status = db.Column(db.String(20), nullable=False, default="unpaid")
    verified_by_admin = db.Column(db.BigInteger, db.ForeignKey("earncash_users.id", ondelete="SET NULL"), nullable=True)
    commission_awarded = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    student = db.relationship("EarnCashUser", foreign_keys=[student_id])
    course = db.relationship("EarnCashCourse")
    referrer = db.relationship("EarnCashUser", foreign_keys=[referred_by])

    def __repr__(self):
        return f"<EarnCashEnrollment id={self.id} student_id={self.student_id}>"
