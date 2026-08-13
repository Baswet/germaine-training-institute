"""
Alumni — Step 2 §28 "Table: alumni".

One table, not split into "registration" + "profile" — the real
alumni.html form collects everything in a single submission (Step 2
§11). programme_id is a nullable FK ("Programme Studied").
"""

from datetime import datetime, timezone

from app.extensions import db


class Alumni(db.Model):
    __tablename__ = "alumni"
    __table_args__ = (
        db.CheckConstraint("graduation_year >= 1990 AND graduation_year <= 2100", name="ck_alumni_graduation_year"),
    )

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)

    full_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)

    programme_id = db.Column(db.BigInteger, db.ForeignKey("programmes.id"), nullable=True)
    graduation_year = db.Column(db.Integer, nullable=True)
    organisation = db.Column(db.String(200), nullable=True)

    # Array — Networking/Mentorship/Events/Career Opportunities pill selections
    engagement_interests = db.Column(db.JSON, nullable=True)

    consent = db.Column(db.Boolean, nullable=False, default=False)
    registered_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    programme = db.relationship("Programme", back_populates="alumni")

    def __repr__(self):
        return f"<Alumni id={self.id} email={self.email!r}>"
