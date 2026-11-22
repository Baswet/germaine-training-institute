"""add admin_users password reset token fields

Revision ID: f3a9c7e21b04
Revises: dd6cf06dc972
Create Date: 2026-08-26

Additive, non-destructive schema change (Step 10 - Forgot Password):

Adds three nullable columns to admin_users:
  - reset_token_hash          sha256 hash of a one-time reset token
                               (the raw token is never stored)
  - reset_token_expires_at    when that token stops being valid
  - reset_requested_at        when the last reset was requested, used
                               only to rate-limit repeat requests

No existing table is dropped. No existing row is modified, deleted, or
reinterpreted - every admin_users row simply gets these three new
columns as NULL until a reset is actually requested for it.
"""
from alembic import op
import sqlalchemy as sa

revision = 'f3a9c7e21b04'
down_revision = 'dd6cf06dc972'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('admin_users', sa.Column('reset_token_hash', sa.String(255), nullable=True))
    op.add_column('admin_users', sa.Column('reset_token_expires_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('admin_users', sa.Column('reset_requested_at', sa.DateTime(timezone=True), nullable=True))


def downgrade():
    op.drop_column('admin_users', 'reset_requested_at')
    op.drop_column('admin_users', 'reset_token_expires_at')
    op.drop_column('admin_users', 'reset_token_hash')
