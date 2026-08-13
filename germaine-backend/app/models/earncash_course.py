"""
EarnCashCourse — "Table: earncash_courses".

Mirrors build10/EarnCash/database/earncash.sql's `courses` table.
The real product behind every referral: a student must actually
enroll and pay tuition for a course before any commission can exist.
"""

from datetime import datetime, timezone

from app.extensions import db


class EarnCashCourse(db.Model):
    __tablename__ = "earncash_courses"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)

    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    tuition_fee = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<EarnCashCourse id={self.id} name={self.name!r}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "tuition_fee": str(self.tuition_fee),
            "description": self.description,
        }
