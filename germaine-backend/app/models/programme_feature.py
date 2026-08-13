"""
ProgrammeFeature — Step 2 §28 "Table: programme_features".

The "What's Included" checklist items actually shown on the pricing
cards (from course.format in ai-courses-data.js). Confirmed dynamically
rendered.
"""

from app.extensions import db


class ProgrammeFeature(db.Model):
    __tablename__ = "programme_features"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    programme_id = db.Column(db.BigInteger, db.ForeignKey("programmes.id"), nullable=False)

    icon = db.Column(db.String(80), nullable=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    display_order = db.Column(db.Integer, nullable=True)

    programme = db.relationship("Programme", back_populates="features")

    def __repr__(self):
        return f"<ProgrammeFeature id={self.id} title={self.title!r}>"
