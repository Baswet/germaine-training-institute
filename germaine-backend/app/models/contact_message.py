"""ContactMessage — Step 2 §28 "Table: contact_messages". No `phone` column — the real form doesn't collect one."""

from datetime import datetime, timezone

from app.extensions import db


class ContactMessage(db.Model):
    __tablename__ = "contact_messages"
    __table_args__ = (
        db.CheckConstraint("status IN ('new', 'read', 'responded')", name="ck_contact_messages_status"),
    )

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)

    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(200), nullable=True)
    message = db.Column(db.Text, nullable=False)

    status = db.Column(db.String(20), nullable=False, default="new")
    submitted_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<ContactMessage id={self.id} email={self.email!r}>"
