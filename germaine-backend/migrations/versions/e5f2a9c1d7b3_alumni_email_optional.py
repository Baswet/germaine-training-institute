"""alumni email optional (public registration no longer collects it)

The public alumni registration form no longer asks for an email address.
Existing email values are preserved untouched and the column is kept.

The UNIQUE index is deliberately retained: PostgreSQL treats NULLs as
distinct, so any number of alumni may have no email while real addresses
are still de-duplicated.

Revision ID: e5f2a9c1d7b3
Revises: b7c1d9e4f2a8
"""
from alembic import op
import sqlalchemy as sa

revision = "e5f2a9c1d7b3"
down_revision = "b7c1d9e4f2a8"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "alumni",
        "email",
        existing_type=sa.String(length=200),
        nullable=True,
    )


def downgrade():
    # Intentionally strict: this fails if any alumni row has a NULL email.
    # Rolling back must never invent placeholder addresses to satisfy the
    # NOT NULL constraint - clean those rows deliberately first.
    op.alter_column(
        "alumni",
        "email",
        existing_type=sa.String(length=200),
        nullable=False,
    )
