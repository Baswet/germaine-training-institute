"""
ProgrammeMode — Step 2 §28 "Table: programme_modes".

The exact data behind the existing AI Bootcamp pricing cards (Full-Time
Hybrid / Full-Time Remote / Part-Time Remote). Academic programmes have
zero rows here — their price is the parent School's flat fee (§8).

start_date and fee_amount are both nullable, matching the current
frontend's "Contact Admissions" / "Applications Open" sentinel
behaviour exactly (Step 2 §8): NULL means "Contact Admissions", never a
literal string stored in these columns.
"""

from datetime import datetime, timezone

from app.extensions import db


class ProgrammeMode(db.Model):
    __tablename__ = "programme_modes"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    programme_id = db.Column(db.BigInteger, db.ForeignKey("programmes.id"), nullable=False)

    mode_key = db.Column(db.String(30), nullable=False)  # 'ft-hybrid' / 'ft-remote' / 'pt-remote'
    label = db.Column(db.String(50), nullable=False)      # "Full-time" / "Part-time"
    sub_label = db.Column(db.String(50), nullable=True)   # "Hybrid" / "Remote"
    icon = db.Column(db.String(80), nullable=True)
    duration = db.Column(db.String(50), nullable=True)

    start_date = db.Column(db.Date, nullable=True)  # NULL = "Contact Admissions" / "Applications Open"
    fee_amount = db.Column(db.Numeric(10, 2), nullable=True)  # NULL = "Contact Admissions"
    fee_currency = db.Column(db.String(10), nullable=False, default="KES")

    schedule = db.Column(db.Text, nullable=True)
    is_available = db.Column(db.Boolean, nullable=False, default=True)
    display_order = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    programme = db.relationship("Programme", back_populates="modes")
    applications = db.relationship("Application", back_populates="programme_mode")

    def __repr__(self):
        return f"<ProgrammeMode id={self.id} mode_key={self.mode_key!r}>"
