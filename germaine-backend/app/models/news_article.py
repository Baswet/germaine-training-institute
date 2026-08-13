"""
NewsArticle — Step 7 CMS addition.

CMS SCHEMA CHANGE REQUIRED (documented, not silent):
  Entity: news_articles
  Reason: news.html is currently 6 hand-authored static cards (confirmed
    in Step 2 §17 — "Option A: remain static, no table proposed" was the
    Step 2-era decision, made before a CMS was in scope). The Step 7 CMS
    addition explicitly requires real news create/edit/draft/publish/
    unpublish/archive — none of the 15 approved tables represent this.
  Fields: see below.
  Relationship: nullable FK to media_assets (featured image), nullable
    FK to admin_users (author/creator).
  Why existing schema cannot support it: no content/article concept
    exists anywhere in the approved schema.
  Impact: additive only. news.html's existing 6 static cards are NOT
    migrated into this table automatically (Step 7 CMS instruction #34:
    "do not invent news articles" / do not fabricate migrated content) —
    they remain exactly as static HTML until a real editor chooses to
    recreate them here. The public frontend only swaps to CMS-sourced
    cards once at least one article is actually published (see the
    news.html bridge script) — an empty table changes nothing.
"""

from datetime import datetime, timezone

from app.extensions import db


class NewsArticle(db.Model):
    __tablename__ = "news_articles"
    __table_args__ = (
        db.CheckConstraint("status IN ('draft', 'published', 'archived')", name="ck_news_articles_status"),
    )

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    slug = db.Column(db.String(220), nullable=False, unique=True)

    title = db.Column(db.String(250), nullable=False)
    summary = db.Column(db.String(500), nullable=True)
    body = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    author = db.Column(db.String(150), nullable=True)

    featured_image_id = db.Column(db.BigInteger, db.ForeignKey("media_assets.id"), nullable=True)

    status = db.Column(db.String(20), nullable=False, default="draft")
    published_at = db.Column(db.DateTime(timezone=True), nullable=True)

    created_by_id = db.Column(db.BigInteger, db.ForeignKey("admin_users.id"), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc),
    )

    featured_image = db.relationship("MediaAsset")
    created_by = db.relationship("AdminUser")

    def __repr__(self):
        return f"<NewsArticle id={self.id} slug={self.slug!r} status={self.status!r}>"
