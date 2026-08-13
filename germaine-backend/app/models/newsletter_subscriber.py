"""
NewsletterSubscriber — Step 2 §28 "Table: newsletter_subscribers".

One table for all 10 newsletter forms sitewide — source_page records
which page a subscriber came from. No `name` column — none of the 10
instances collect one.
"""

from datetime import datetime, timezone

from app.extensions import db


class NewsletterSubscriber(db.Model):
    __tablename__ = "newsletter_subscribers"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)

    email = db.Column(db.String(200), nullable=False, unique=True)
    source_page = db.Column(db.String(100), nullable=True)  # which of the 10 pages, Step 2 §14
    consent = db.Column(db.Boolean, nullable=False, default=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    subscribed_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    unsubscribed_at = db.Column(db.DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<NewsletterSubscriber id={self.id} email={self.email!r}>"
