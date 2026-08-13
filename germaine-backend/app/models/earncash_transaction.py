"""
EarnCashTransaction — "Table: earncash_transactions".

Mirrors build10/EarnCash/database/earncash.sql's `transactions` table:
a ledger of every wallet movement (commission credit, withdrawal
debit, admin adjustment, or a reversal). Every wallet balance change
is written here in the same DB transaction as the balance update, so
the ledger and the balance can never drift apart.
"""

from datetime import datetime, timezone

from app.extensions import db


class EarnCashTransaction(db.Model):
    __tablename__ = "earncash_transactions"
    __table_args__ = (
        db.CheckConstraint(
            "type IN ('commission', 'withdrawal', 'adjustment', 'reversal')",
            name="ck_earncash_transactions_type",
        ),
    )

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)

    user_id = db.Column(db.BigInteger, db.ForeignKey("earncash_users.id", ondelete="CASCADE"), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("EarnCashUser")

    def __repr__(self):
        return f"<EarnCashTransaction id={self.id} user_id={self.user_id} type={self.type!r}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type,
            "amount": str(self.amount),
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
