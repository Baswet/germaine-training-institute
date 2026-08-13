"""
ContentListItem — Step 7 CMS addition.

CMS SCHEMA CHANGE REQUIRED (documented, not silent):
  Entity: content_list_items
  Reason: several existing pages show a small ORDERED, repeating list of
    image+caption items — the homepage hero slideshow (4 slides) and
    Student Life's Clubs & Societies slideshow are the two confirmed in
    the current frontend (Step 7 CMS instruction #11/#20). Rather than
    building a separate near-identical table per list (hero_slides,
    clubs, societies, ...), one generic ordered-list table is used,
    discriminated by `list_key` — this mirrors the same normalization
    reasoning already used for `partner_enquiries.enquiry_type` in Step
    2 §15 ("a third near-identical table here would be exactly the
    unjustified duplication your instructions warn against").
  Fields: see below.
  Relationship: nullable FK to media_assets.
  Why existing schema cannot support it: no such concept exists in the
    approved schema.
  Impact: additive only. Recognized `list_key` values are enforced in
    app/services/cms_service.py's LIST_KEY_REGISTRY — administrators
    cannot invent new arbitrary lists, only add/edit/reorder items
    within the lists the actual frontend already renders. An empty
    result set for a given list_key means "no CMS items yet" — the
    corresponding page's existing static slides/cards are used
    unchanged.
"""

from datetime import datetime, timezone

from app.extensions import db


class ContentListItem(db.Model):
    __tablename__ = "content_list_items"
    __table_args__ = (
        db.CheckConstraint(
            "list_key IN ('homepage_hero_slides', 'student_life_clubs', 'student_life_sports')",
            name="ck_content_list_items_list_key",
        ),
    )

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    list_key = db.Column(db.String(50), nullable=False)

    title = db.Column(db.String(200), nullable=True)
    subtitle = db.Column(db.String(300), nullable=True)
    link_url = db.Column(db.String(500), nullable=True)
    image_id = db.Column(db.BigInteger, db.ForeignKey("media_assets.id"), nullable=True)

    display_order = db.Column(db.Integer, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc),
    )

    image = db.relationship("MediaAsset")

    def __repr__(self):
        return f"<ContentListItem id={self.id} list_key={self.list_key!r}>"
