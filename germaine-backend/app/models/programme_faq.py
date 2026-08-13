"""ProgrammeFAQ — Step 2 §28 "Table: programme_faqs". Confirmed dynamically rendered (renderFaqs)."""

from app.extensions import db


class ProgrammeFAQ(db.Model):
    __tablename__ = "programme_faqs"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    programme_id = db.Column(db.BigInteger, db.ForeignKey("programmes.id"), nullable=False)

    question = db.Column(db.String(300), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    display_order = db.Column(db.Integer, nullable=True)

    programme = db.relationship("Programme", back_populates="faqs")

    def __repr__(self):
        return f"<ProgrammeFAQ id={self.id}>"
