"""
Applicant — Step 2 §28 "Table: applicants".

Built from apply.html's real fields only (Step 2 §9 / STEP-2 instruction
#4) — not built around the unconfirmed external endpoint
(germaineinstitute.com/application/clients/add).

One applicant, many applications over time — looked up/created by
email+phone on each new submission, not force-unique per application.
national_id and date_of_birth are sensitive fields (Step 2 §22):
admin-only, never exposed via any public API.
"""

from datetime import datetime, timezone

from app.extensions import db


class Applicant(db.Model):
    __tablename__ = "applicants"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)

    full_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)  # stored with "254" prefix, matching current payload

    national_id = db.Column(db.String(30), nullable=True)   # sensitive — Step 2 §22
    date_of_birth = db.Column(db.Date, nullable=True)       # sensitive
    gender = db.Column(db.String(20), nullable=True)
    county = db.Column(db.String(50), nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    applications = db.relationship("Application", back_populates="applicant", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Applicant id={self.id} email={self.email!r}>"
