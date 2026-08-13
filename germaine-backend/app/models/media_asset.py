"""
MediaAsset — Step 7 CMS addition.

CMS SCHEMA CHANGE REQUIRED (documented, not silent):
  Entity: media_assets
  Reason: no table anywhere in the approved Step 2 schema represents an
    uploaded image. The CMS requires one central place to store upload
    metadata (never the binary itself — Step 2 §21's file-storage
    recommendation is followed here: filesystem/object storage holds
    the bytes, the database holds only metadata).
  Fields: see below.
  Relationship: nullable FK from news_articles.featured_image_id and
    content_list_items.image_id.
  Why existing schema cannot support it: no image/media concept exists
    anywhere in the 14+1 approved tables.
  Impact: additive only — one new table, no change to any existing
    table's columns or constraints.
"""

from datetime import datetime, timezone

from app.extensions import db


class MediaAsset(db.Model):
    __tablename__ = "media_assets"
    __table_args__ = (
        db.CheckConstraint("status IN ('active', 'archived')", name="ck_media_assets_status"),
    )

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)

    filename = db.Column(db.String(255), nullable=False)  # safe, generated — never the raw upload name
    original_filename = db.Column(db.String(255), nullable=True)  # for staff reference only, never used as a path
    url_path = db.Column(db.String(500), nullable=False)  # public-servable path, e.g. /media/uploads/<filename>
    alt_text = db.Column(db.String(300), nullable=True)
    mime_type = db.Column(db.String(100), nullable=False)
    size_bytes = db.Column(db.Integer, nullable=False)
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)

    status = db.Column(db.String(20), nullable=False, default="active")

    uploaded_by_id = db.Column(db.BigInteger, db.ForeignKey("admin_users.id"), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc),
    )

    uploaded_by = db.relationship("AdminUser")

    def __repr__(self):
        return f"<MediaAsset id={self.id} filename={self.filename!r}>"
