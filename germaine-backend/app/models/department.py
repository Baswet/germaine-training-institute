"""
Department — Step 2 §28 "Table: departments".

Real for exactly 4 of 9 active schools today (hospitality, engineering,
cosmetology, business) per school-data.js. school_id is required (a
department always belongs to a school), but a School may have zero
departments — this table is not populated for schools without them.
"""

from datetime import datetime, timezone

from app.extensions import db


class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    school_id = db.Column(db.BigInteger, db.ForeignKey("schools.id"), nullable=False)

    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(300), nullable=True)
    display_order = db.Column(db.Integer, nullable=True)

    careers = db.Column(db.JSON, nullable=True)
    quick_links = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    school = db.relationship("School", back_populates="departments")
    programmes = db.relationship("Programme", back_populates="department")

    def __repr__(self):
        return f"<Department id={self.id} name={self.name!r}>"
