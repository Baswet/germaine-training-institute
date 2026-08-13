"""
SiteContent — Step 7 CMS addition.

CMS SCHEMA CHANGE REQUIRED (documented, not silent):
  Entity: site_content
  Reason: structured, editable text fields for Homepage / About Us /
    Contact Information (Student Life's repeating items use
    ContentListItem instead — see that model). No table in the approved
    schema represents page copy.
  Fields: see below.
  Relationship: none (standalone key/value row per field).
  Why existing schema cannot support it: no content concept exists in
    the approved schema.
  Impact: additive only. `content_key` is constrained by application
    code (app/services/cms_service.py's CONTENT_FIELD_REGISTRY) to a
    fixed, known set of keys — administrators can only fill in values
    for fields that genuinely already exist on the corresponding public
    page (Step 7 CMS instruction: "Only include fields that correspond
    to content already present in the actual frontend"). This is
    deliberately NOT a free-form key-value store a template could
    invent new keys into — it is a structured registry, enforced at the
    service layer, which is what keeps this a CMS rather than a page
    builder.
  Backward compatibility: an absent row for a given key means "no CMS
    override yet" — the public page's existing static text is used
    unchanged (see each page's content bridge script). An empty table
    changes nothing on the live site.
"""

from datetime import datetime, timezone

from app.extensions import db


class SiteContent(db.Model):
    __tablename__ = "site_content"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    content_key = db.Column(db.String(150), nullable=False, unique=True)  # e.g. "homepage.hero_badge"
    value = db.Column(db.Text, nullable=True)

    updated_by_id = db.Column(db.BigInteger, db.ForeignKey("admin_users.id"), nullable=True)
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc),
    )

    updated_by = db.relationship("AdminUser")

    def __repr__(self):
        return f"<SiteContent key={self.content_key!r}>"
