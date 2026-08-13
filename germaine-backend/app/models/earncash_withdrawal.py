"""
EarnCashWithdrawal — "Table: earncash_withdrawals".

Mirrors build10/EarnCash/database/earncash.sql's `withdrawals` table.
Funds are debited from the user's wallet immediately on request
(reserved) so the same balance can't be withdrawn twice while pending
admin approval; rejection refunds the wallet.
"""

from datetime import datetime, timezone

from app.extensions import db


class EarnCashWithdrawal(db.Model):
    __tablename__ = "earncash_withdrawals"
    __table_args__ = (
        db.CheckConstraint(
            "method IN ('mpesa', 'bank', 'airtel_money')",
            name="ck_earncash_withdrawals_method",
        ),
        db.CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')",
            name="ck_earncash_withdrawals_status",
        ),
    )

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)

    user_id = db.Column(db.BigInteger, db.ForeignKey("earncash_users.id", ondelete="CASCADE"), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    method = db.Column(db.String(20), nullable=False)
    account_details = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    admin_note = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = db.relationship("EarnCashUser")

    def __repr__(self):
        return f"<EarnCashWithdrawal id={self.id} user_id={self.user_id} status={self.status!r}>"

    def to_dict(self, with_user=False):
        d = {
            "id": self.id,
            "user_id": self.user_id,
            "amount": str(self.amount),
            "method": self.method,
            "account_details": self.account_details,
            "status": self.status,
            "admin_note": self.admin_note,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if with_user and self.user:
            d["fullname"] = self.user.fullname
            d["email"] = self.user.email
        return d
