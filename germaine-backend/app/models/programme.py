"""
Programme — Step 2 §28 "Table: programmes".

Unified academic + AI Bootcamp table (339 real academic entries + 14
real AI Bootcamp entries), per Step 2 instruction #1's preference to
reuse one entity rather than build two parallel systems.

programme_type discriminates the two kinds. school_id/department_id are
NULL for AI Bootcamp rows; category_id is NULL for academic rows.

Deliberately excluded fields (see STEP-2-DATABASE-ARCHITECTURE.md §4 /
§28 note): `careers` (confirmed dead-in-JS / static-HTML-only) and
`skills`/detailed `projects` entries (confirmed dead data, rendered
nowhere).

Pricing note (Step 2 §8): academic programmes have NO fee column here —
their price is the parent School's flat `fee` string. AI Bootcamp
pricing lives exclusively on ProgrammeMode.fee_amount, never here.
"""

from datetime import datetime, timezone

from app.extensions import db


class Programme(db.Model):
    __tablename__ = "programmes"
    __table_args__ = (
        db.CheckConstraint("programme_type IN ('academic', 'ai_bootcamp')", name="ck_programmes_programme_type"),
    )

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    programme_type = db.Column(db.String(20), nullable=False)
    slug = db.Column(db.String(150), nullable=False, unique=True)

    school_id = db.Column(db.BigInteger, db.ForeignKey("schools.id"), nullable=True)
    department_id = db.Column(db.BigInteger, db.ForeignKey("departments.id"), nullable=True)
    category_id = db.Column(db.BigInteger, db.ForeignKey("programme_categories.id"), nullable=True)

    name = db.Column(db.String(250), nullable=False)
    level = db.Column(db.String(50), nullable=True)
    level_class = db.Column(db.String(30), nullable=True)
    duration = db.Column(db.String(50), nullable=True)
    entry_requirement = db.Column(db.Text, nullable=True)
    exam_body = db.Column(db.String(50), nullable=True)
    overview = db.Column(db.Text, nullable=True)
    gain_points = db.Column(db.JSON, nullable=True)  # array of strings
    image_path = db.Column(db.String(300), nullable=True)
    apply_heading = db.Column(db.String(200), nullable=True)
    apply_subtext = db.Column(db.String(300), nullable=True)

    is_active = db.Column(db.Boolean, nullable=False, default=True)
    display_order = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    school = db.relationship("School", back_populates="programmes")
    department = db.relationship("Department", back_populates="programmes")
    category = db.relationship("ProgrammeCategory", back_populates="programmes")

    modes = db.relationship("ProgrammeMode", back_populates="programme", cascade="all, delete-orphan")
    faqs = db.relationship("ProgrammeFAQ", back_populates="programme", cascade="all, delete-orphan")
    features = db.relationship("ProgrammeFeature", back_populates="programme", cascade="all, delete-orphan")
    applications = db.relationship("Application", back_populates="programme")
    alumni = db.relationship("Alumni", back_populates="programme")

    def __repr__(self):
        return f"<Programme id={self.id} slug={self.slug!r} type={self.programme_type!r}>"
