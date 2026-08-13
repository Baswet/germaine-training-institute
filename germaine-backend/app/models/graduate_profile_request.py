"""
GraduateProfileRequest — Step 2 §28 "Table: graduate_profile_requests".

No FK to an `employers` table (deliberately not built — Step 2 §12):
graduate-hire.html collects employer/company/contact details inline,
per request, with no employer login or repeat-employer recognition in
the current frontend. Columns here are exactly what that form collects.

No FK to a `graduates` table either — no frontend path exists yet for a
graduate to submit/claim their own profile (Phase 3/4, per §12).
"""

from datetime import datetime, timezone

from app.extensions import db


class GraduateProfileRequest(db.Model):
    __tablename__ = "graduate_profile_requests"
    __table_args__ = (
        db.CheckConstraint(
            "status IN ('pending', 'approved', 'fulfilled', 'declined')",
            name="ck_graduate_profile_requests_status",
        ),
    )

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)

    employer_name = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role_needed = db.Column(db.String(200), nullable=True)
    message = db.Column(db.Text, nullable=True)

    status = db.Column(db.String(20), nullable=False, default="pending")
    submitted_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<GraduateProfileRequest id={self.id} employer_name={self.employer_name!r}>"
