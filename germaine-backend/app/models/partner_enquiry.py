"""
PartnerEnquiry — Step 2 §28 "Table: partner_enquiries".

One table for both partner-with-us.html and corporate-training.html's
consultation form (confirmed identical field shape, Step 2 §13/§15) —
enquiry_type distinguishes them without duplicating the table.
"""

from datetime import datetime, timezone

from app.extensions import db


class PartnerEnquiry(db.Model):
    __tablename__ = "partner_enquiries"
    __table_args__ = (
        db.CheckConstraint(
            "enquiry_type IN ('partnership', 'corporate_training')",
            name="ck_partner_enquiries_enquiry_type",
        ),
        db.CheckConstraint("status IN ('new', 'contacted', 'closed')", name="ck_partner_enquiries_status"),
    )

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)

    organisation = db.Column(db.String(200), nullable=False)
    contact_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    enquiry_type = db.Column(db.String(30), nullable=False)
    message = db.Column(db.Text, nullable=True)

    status = db.Column(db.String(20), nullable=False, default="new")
    submitted_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<PartnerEnquiry id={self.id} organisation={self.organisation!r}>"
