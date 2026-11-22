"""
Newsroom (News & Events publication) — additive tables only.

  * NewsArticleMeta — 1:1 extension of the EXISTING news_articles table
    (Step 7 CMS). Holds the editorial fields the News & Events publication
    needs: newsroom category, external-source attribution (publisher name,
    original URL, original publication time), editorial flags (featured /
    trending / breaking / editor's pick), an optional official video URL
    for the Watch section, and a real read counter for Most Read.

    The existing NewsArticle model, its admin editor and /api/news are not
    modified. An article with no meta row (or is_external = False) is a GTI
    institutional article and is shown only in the "GTI Updates" section,
    never mixed with external reporting.

  * NewsEvent — events discovery records (conferences, concerts, sports,
    workshops…). Only rows with publication_status='published' are public.
    Upcoming / ongoing / completed is COMPUTED from the dates in Nairobi
    time, so a past event can never be advertised as upcoming;
    status_override only adds 'cancelled' / 'postponed'.

Editorial rules encoded here: every external story must carry a source
name and original URL (enforced in newsroom_service before publishing);
every event must name its organizer and an official source URL.
"""

from datetime import datetime, timezone

from app.extensions import db

NEWS_CATEGORIES = [
    ("kenya", "Kenya News"),
    ("business", "Business & Economy"),
    ("world", "Africa & World"),
    ("sports", "Sports"),
    ("entertainment", "Entertainment & Culture"),
    ("technology", "Technology & Innovation"),
    ("crime", "Crime & Security"),
    ("lifestyle", "Lifestyle & Health"),
    ("education", "Education & Opportunities"),
]
NEWS_CATEGORY_KEYS = [k for k, _ in NEWS_CATEGORIES]
NEWS_CATEGORY_LABELS = dict(NEWS_CATEGORIES)

EVENT_CATEGORIES = [
    ("conference", "Conferences"),
    ("concert", "Concerts"),
    ("festival", "Festivals"),
    ("sports", "Sports"),
    ("technology", "Technology"),
    ("business", "Business"),
    ("exhibition", "Exhibitions"),
    ("workshop", "Workshops"),
    ("career", "Career Events"),
    ("student", "Student Events"),
    ("culture", "Arts & Culture"),
]
EVENT_CATEGORY_KEYS = [k for k, _ in EVENT_CATEGORIES]
EVENT_CATEGORY_LABELS = dict(EVENT_CATEGORIES)


def _now():
    return datetime.now(timezone.utc)


class NewsArticleMeta(db.Model):
    __tablename__ = "news_article_meta"
    __table_args__ = (
        db.UniqueConstraint("article_id", name="uq_news_article_meta_article_id"),
        db.Index("ix_news_article_meta_category", "news_category"),
    )

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    article_id = db.Column(
        db.BigInteger, db.ForeignKey("news_articles.id", ondelete="CASCADE"), nullable=False
    )
    news_category = db.Column(db.String(30), nullable=True)
    is_external = db.Column(db.Boolean, nullable=False, default=True)
    source_name = db.Column(db.String(150), nullable=True)
    source_url = db.Column(db.String(600), nullable=True)
    source_published_at = db.Column(db.DateTime(timezone=True), nullable=True)
    image_credit = db.Column(db.String(200), nullable=True)
    video_url = db.Column(db.String(600), nullable=True)
    video_duration = db.Column(db.String(20), nullable=True)

    is_featured = db.Column(db.Boolean, nullable=False, default=False)
    is_trending = db.Column(db.Boolean, nullable=False, default=False)
    is_breaking = db.Column(db.Boolean, nullable=False, default=False)
    is_editors_pick = db.Column(db.Boolean, nullable=False, default=False)
    feature_rank = db.Column(db.Integer, nullable=False, default=0)  # higher = more prominent
    trending_note = db.Column(db.String(200), nullable=True)          # editorial signal, e.g. "Covered by 5 outlets"

    view_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_now)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_now, onupdate=_now)

    article = db.relationship(
        "NewsArticle", backref=db.backref("meta", uselist=False, passive_deletes=True)
    )

    @property
    def category_label(self):
        return NEWS_CATEGORY_LABELS.get(self.news_category, "")


class NewsEvent(db.Model):
    __tablename__ = "news_events"
    __table_args__ = (
        db.CheckConstraint("publication_status IN ('draft', 'published')", name="ck_news_events_publication_status"),
        db.CheckConstraint(
            "status_override IS NULL OR status_override IN ('cancelled', 'postponed')",
            name="ck_news_events_status_override",
        ),
        db.UniqueConstraint("slug", name="uq_news_events_slug"),
        db.Index("ix_news_events_start_date", "start_date"),
        db.Index("ix_news_events_publication_status", "publication_status"),
    )

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    slug = db.Column(db.String(220), nullable=False)
    title = db.Column(db.String(250), nullable=False)
    category = db.Column(db.String(30), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_id = db.Column(db.BigInteger, db.ForeignKey("media_assets.id", ondelete="SET NULL"), nullable=True)
    organizer = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    start_time = db.Column(db.String(40), nullable=True)   # free text, e.g. "9:00 AM – 5:00 PM"
    venue = db.Column(db.String(250), nullable=True)
    county = db.Column(db.String(60), nullable=True)
    registration_url = db.Column(db.String(600), nullable=True)
    source_url = db.Column(db.String(600), nullable=True)
    date_note = db.Column(db.String(250), nullable=True)   # e.g. "Performances 20–22 and 28–29 Nov"
    status_override = db.Column(db.String(20), nullable=True)
    publication_status = db.Column(db.String(20), nullable=False, default="draft")
    is_featured = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_now)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_now, onupdate=_now)

    image = db.relationship("MediaAsset", foreign_keys=[image_id])

    @property
    def category_label(self):
        return EVENT_CATEGORY_LABELS.get(self.category, self.category)
