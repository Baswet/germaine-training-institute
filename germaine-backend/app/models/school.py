"""
School — Step 2 §28 "Table: schools".

The 15 academic schools sourced from assets/js/school-data.js (9 shown
in current navigation, 6 kept for existing bookmarked pages). Not
seeded here — see STEP-2-DATABASE-ARCHITECTURE.md §31 for the seed
plan, which is a future step, not part of this scaffold.
"""

from datetime import datetime, timezone

from app.extensions import db


class School(db.Model):
    __tablename__ = "schools"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    slug = db.Column(db.String(80), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(300), nullable=True)

    # Flat representative fee, e.g. "KES 11,500". Kept as a display
    # string, not decimal — see Step 2 §39 Open Question A. Do not
    # convert to numeric without verification.
    fee = db.Column(db.String(50), nullable=True)

    is_active = db.Column(db.Boolean, nullable=False, default=True)
    display_order = db.Column(db.Integer, nullable=True)

    careers = db.Column(db.JSON, nullable=True)       # array of strings
    quick_links = db.Column(db.JSON, nullable=True)   # array of {label, url}

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    departments = db.relationship("Department", back_populates="school", cascade="all, delete-orphan")
    programmes = db.relationship("Programme", back_populates="school")

    def __repr__(self):
        return f"<School id={self.id} slug={self.slug!r}>"
