"""
ProgrammeCategory — Step 2 §28 "Table: programme_categories".

The real AI Bootcamp catalogue filter categories (cyber-security,
data-analytics, cloud-computing, etc.) sourced from
assets/js/ai-courses-data.js. Not used by academic programmes.
"""

from app.extensions import db


class ProgrammeCategory(db.Model):
    __tablename__ = "programme_categories"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    slug = db.Column(db.String(80), nullable=False, unique=True)
    label = db.Column(db.String(150), nullable=False)
    icon = db.Column(db.String(80), nullable=True)  # Font Awesome class, as used today

    programmes = db.relationship("Programme", back_populates="category")

    def __repr__(self):
        return f"<ProgrammeCategory id={self.id} slug={self.slug!r}>"
